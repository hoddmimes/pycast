from __future__ import annotations
import types
from abc import ABC, abstractmethod
from pymc.aux.aux import Aux
from pymc.msg.rcv_segment import Segment, RcvSegment
from pymc.distributor_configuration import DistributorLogFlags


class AsyncEvent(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def execute(self, connection: 'Connection'):
        pass

    @abstractmethod
    def toString(self):
        pass

    def __str__(self):
        return "[ {} ] {}".format(self.__class__.__name__, self.toString())

    @classmethod
    def cast(cls, obj: object) -> AsyncEvent:
        if isinstance(obj, AsyncEvent):
            return obj
        raise Exception('object can not be cast to {}'.format(cls.__name__))


class DistributorEvent(object):
    NAGGING_EXCEPTION = 101
    REMOTE_CONNECTION_CREATED = 102
    REMOTE_CONNECTION_REMOVED = 103
    RETRANSMISSION_NAK = 104
    TOO_MANY_RETRIES = 105
    COMMUNICATION_FAILURE = 106
    CONNECTION_CLOSING = 107

    def __init__(self, event_type: int, message: str = None):
        self.event_type: int = event_type
        self.message: str = message

    def getMessage(self) -> str:
        return self.message

    def setMessage(self, message: str):
        self.message = message

    def __str__(self):
        return self.message

    def getEventType(self) -> int:
        return self.event_type


class DistributorErrorEvent(ABC, DistributorEvent):

    def __init__(self, event_type: int, message: str = None):
        super().__init__(event_type, message)


class DistributorCommunicationErrorEvent(DistributorErrorEvent):

    def __init__(self, direction: str, mc_addr: int, mc_port: int, reason: str):
        super().__init__(DistributorEvent.COMMUNICATION_FAILURE)
        self.mc_addr_str: str = Aux.ip_addr_int_to_str(mc_addr)
        self.mc_port = mc_port

        self.setMessage(
            '{} Connection communication error mc-addr: {} mc-port: {}\n  reason: {} '.format(direction,
                                                                                              self.mc_addr_str,
                                                                                              self.mc_port, reason))


class DistributorNaggingErrorEvent(DistributorErrorEvent):

    def __init__(self, mc_addr: int, mc_port: int):
        super().__init__(DistributorEvent.NAGGING_EXCEPTION)
        self.mc_addr: str = Aux.ip_addr_int_to_str(mc_addr)
        self.mc_port: int = mc_port

        super().setMessage('This connection mc-addr: {} mc-port: {} is nagging'.format(self.mc_addr, self.mc_port))


class DistributorNewRemoteConnectionEvent(DistributorEvent):

    def __init__(self, source_addr: int, mc_addr: int, mc_port: int, appl_name: str,
                 appl_id: int, sender_id: int, sender_start_time):
        super().__init__(DistributorEvent.REMOTE_CONNECTION_CREATED)
        self.mc_addr: str = Aux.ip_addr_int_to_str(mc_addr)
        self.mc_port: int = mc_port
        self.remote_addr: str = Aux.ip_addr_int_to_str(source_addr)
        self.appl_name: str = appl_name
        self.appl_id: int = appl_id
        self.sender_id: int = sender_id
        self.sender_start_time: str = Aux.time_string(sender_start_time)

        self.setMessage(
            "New Remote Connection host: {} mc-addr: {} mc-port: {} Application: {} App-id: {} Sender-id: {} sender started: {}".
            format(self.remote_addr, self.mc_addr, self.mc_port, self.appl_name,
                   hex(self.appl_id), self.sender_id, self.sender_start_time))


class DistributorRemoveRemoteConnectionEvent(DistributorEvent):

    def __init__(self, source_addr: int, mc_addr: int, mc_port: int, appl_name: str,
                 appl_id: int, sender_id: int, sender_start_time):
        super().__init__(DistributorEvent.REMOTE_CONNECTION_REMOVED)
        self.mc_addr: str = Aux.ip_addr_int_to_str(mc_addr)
        self.mc_port: int = mc_port
        self.remote_addr: str = Aux.ip_addr_int_to_str(source_addr)
        self.appl_name: str = appl_name
        self.appl_id: int = appl_id
        self.sender_id: int = sender_id
        self.sender_start_time: str = Aux.time_string(sender_start_time)

        self.setMessage(
            "Remote Connection Disconnected host: {} mc-addr: {} mc-port: {} Application: {} App-id: {} Sender-id: {} sender started: {}".
            format(self.remote_addr, self.mc_addr, self.mc_port, self.appl_name,
                   hex(self.appl_id), self.sender_id, self.sender_start_time))


class DistributorRetransmissionNAKErrorEvent(DistributorErrorEvent):

    def __init__(self, mc_addr: int, mc_port: int):
        super().__init__(DistributorEvent.RETRANSMISSION_NAK)
        self.mc_addr: str = Aux.ip_addr_int_to_str(mc_addr)
        self.mc_port: int = mc_port

        super().setMessage(
            'Distributor Connection, failed to recover lost message. Message not in remote cache. mc-addr: {} mc-port: {}'.
            format(self.mc_addr, self.mc_port))


class DistributorTooManyRetransmissionRetriesErrorEvent(DistributorErrorEvent):

    def __init__(self, mc_addr: int, mc_port: int):
        super().__init__(DistributorEvent.TOO_MANY_RETRIES)
        self.mc_addr: str = Aux.ip_addr_int_to_str(mc_addr)
        self.mc_port: int = mc_port

        super().setMessage(
            "Distributor Connection, failed to recover lost message. Too many recovery retries \n. mc-addr: {} mc-port: {}".format(
                self.mc_addr, self.mc_port))


class DistributorConnectionClosedErrorEvent(DistributorErrorEvent):

    def __init__(self, mc_addr: int, mc_port: int):
        super().__init__(DistributorEvent.CONNECTION_CLOSING)
        self.mc_addr: str = Aux.ip_addr_int_to_str(mc_addr)
        self.mc_port: int = mc_port

        super().setMessage("Distributor Connection Closing mc-addr: {} mc-port: {}".format(self.mc_addr, self.mc_port))


class AsyncEventSignalEvent(AsyncEvent, ABC):

    def __init__(self, event: DistributorEvent):
        super().__init__()
        self.event: DistributorEvent = event

    def __str__(self) -> str:
        return "AsyncEventSignalEvent event: {}".format(self.event)

    def execute(self, connection: 'Connection'):
        if connection.is_logging_enabled(DistributorLogFlags.LOG_ERROR_EVENTS):
            connection.log_info("APPLICATION ERROR EVENT Event: {}".format(self.event))

        connection.async_event_to_client(self.event)


class AsyncEventFlushSender(AsyncEvent, ABC):

    def __init__(self, current_flush_seqno):
        super().__init__()
        self.mCurrentFlushSeqno = current_flush_seqno

    def execute(self, connection: 'Connection'):
        connection.mConnectionSender.flush_holdback(self.mCurrentFlushSeqno)

    def toString(self) -> str:
        return " current-flush-seqno: {}".format(self.mCurrentFlushSeqno)


class AsyncEventReceiveSegment(AsyncEvent, ABC):
    def __init__(self, rcv_segment: RcvSegment):
        super().__init__()
        self.mRcvSegment = rcv_segment

    def execute(self, connection: 'Connection'):
        connection.traffic_statistic_task.update_rcv_statistics(self.mRcvSegment)
        connection.connection_receiver.process_received_segment(self.mRcvSegment)

    def toString(self) -> str:
        return self.mRcvSegment.__str__()
