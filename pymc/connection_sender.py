import random

from distributor_interfaces import ConnectionBase, ConnectionSenderBase, DistributorBase
from pymc.msg.net_msg_update import NetMsgUpdate
from pymc.msg.net_msg_heartbeat import NetMsgHeartbeat
from pymc.msg.net_msg_configuration import NetMsgConfiguration
from pymc.msg.net_msg_retransmission import NetMsgRetransmissionRqst, NetMsgRetransmissionNAK
from pymc.msg.xta_update import XtaUpdate
from pymc.msg.xta_segment import XtaSegment
from pymc.msg.segment import Segment
from pymc.aux.aux import Aux
from pymc.distributor_events import DistributorCommunicationErrorEvent
from pymc.aux.aux_uuid import Aux_UUID
from pymc.aux.log_manager import LogManager
from pymc.retransmission_cache import RetransmissionCache
from pymc.traffic_flow_task import TrafficFlowTask
from connection_configuration import ConnectionConfiguration
from aux.distributor_exception import DistributorException
from pymc.send_holdback_task import SenderHoldbackTimerTask
from pymc.connection_timers import ConnectionTimerExecutor, ConnectionTimerTask
from pymc.distributor_configuration import DistributorLogFlags
from pymc.client_controller import ClientDeliveryController
from pymc.connection import Connection
from logging import Logger


def sendHeartbeat(connection: Connection):
    _heartbeat = NetMsgHeartbeat(XtaSegment(connection.configuration.small_segment_size))
    _heartbeat.setHeader(
        message_type=Segment.MSG_TYPE_HEARTBEAT,
        segment_flags=Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END,
        local_address=connection.connection_sender.local_address,
        sender_id=connection.connection_sender.sender_id,
        sender_start_time_sec=connection.connection_sender.sender_start_time,
        app_id=connection.distributor.app_id())

    _heartbeat.set(
        mc_addr=connection.ipmc.mc_address,
        mc_port=connection.ipmc.mc_port,
        sender_id=connection.connection_sender.sender_id,
        sequence_no=connection.connection_sender.current_seqno)
    _heartbeat.encode()
    connection.connection_sender.send_segment(_heartbeat.segment)


class SendHeartbeatTask(ConnectionTimerTask):
    def __init__(self, connection_id):
        super().__init__(connection_id)
        self._connection_is_sending = False

    def dataHasBeenPublished(self):
        self._connection_is_sending = True

    def execute(self, connection: Connection):
        if connection.is_time_to_die:
            super().cancel()
            return
        if len(connection.publishers) == 0:
            return
        if not self._connection_is_sending:
            sendHeartbeat(connection)
        self._connection_is_sending = False


def sendConfiguration(connection: Connection):
    connection.pushOutConfiguration()
    connection.pushOutConfiguration()


class SendConfigurationTask(ConnectionTimerTask):
    def __init__(self, connection_id: int):
        super().__init__(connection_id)

    def execute(self, connection: Connection):
        if connection.is_time_to_die:
            self.cancel()
            return
        if len(connection.publishers) == 0:
            return
        sendConfiguration(connection)


"""
##=====================================================================
## ConnectionSender
## ======================================================================
"""


def logInfo(msg):
    ConnectionSender.logger().info(msg)


def logWarning(msg):
    ConnectionSender.logger().warning(msg)


def logError(msg):
    ConnectionSender.logger().error(msg)


def logThrowable(exception):
    ConnectionSender.logger().exception(exception)


def logProtocolData(segment: Segment):
    _msg_type = segment.hdr_msg_type

    if _msg_type == Segment.MSG_TYPE_CONFIGURATION:
        _msg = NetMsgConfiguration(segment)
        _msg.decode()
        logInfo("PROTOCOL [XTA] " + str(_msg))
    elif _msg_type == Segment.MSG_TYPE_HEARTBEAT:
        _msg = NetMsgHeartbeat(segment)
        _msg.decode()
        logInfo("PROTOCOL [XTA] " + str(_msg))
    elif _msg_type == Segment.MSG_TYPE_RETRANSMISSION:
        _msg = NetMsgUpdate(segment)
        _msg.decode()
        logInfo("PROTOCOL [XTA] <retrans>" + str(_msg))
    elif _msg_type == Segment.MSG_TYPE_RETRANSMISSION_NAK:
        _msg = NetMsgRetransmissionNAK(segment)
        _msg.decode()
        logInfo("PROTOCOL [XTA] " + str(_msg))
    elif _msg_type == Segment.MSG_TYPE_RETRANSMISSION_RQST:
        _msg = NetMsgRetransmissionRqst(segment)
        _msg.decode()
        logInfo("PROTOCOL [XTA] " + str(_msg))
    elif _msg_type == Segment.MSG_TYPE_UPDATE:
        _msg = NetMsgUpdate(segment)
        _msg.decode()
        logInfo("PROTOCOL [XTA] " + str(_msg))
    else:
        logInfo("PROTOCOL [XTA] unknown message: " + Segment.getMessageTypeString(_msg_type))


def log_throwable(exception):
    ConnectionSender.logger().exception(exception)


class ConnectionSender(ConnectionSenderBase):
    _cLogger: Logger = None

    def __init__(self, connection_base: ConnectionBase):
        self._sender_id: int = Aux_UUID.getId()
        self._error_signaled: bool = False
        self._sender_start_time = Aux.currentSeconds()
        self._last_update_flush_seqno: int = 0
        self._connection: ConnectionBase = connection_base
        self._configuration: ConnectionConfiguration = connection_base.configuration()
        self._distributor: DistributorBase = connection_base.distributor()
        self._current_update: NetMsgUpdate = self.get_new_current_update()  # initialize self.mCurrentUpdate:NetMsgUpdate
        self._heartbeat_timer_task = SendHeartbeatTask(connection_id=connection_base.connection_id)
        if ConnectionSender._cLogger is None:
            ConnectionSender._cLogger = LogManager.getInstance().getLogger('ConnectionSender')

        if self._configuration.sender_id_port == 0:
            self._sender_id = Aux.allocateServerPortId(self._configuration.sender_id_port_offset)
        else:
            self._sender_id = self._configuration.sender_id_port

        self._local_address: int = self._distributor.local_address()
        self._current_seqno: int = 0
        self._traffic_flow_task: TrafficFlowTask = TrafficFlowTask(connection_id=self._connection.connection_id())
        self._retransmission_cache = RetransmissionCache(self)

    @property
    def local_address(self) -> int:
        return self._local_address

    @staticmethod
    def logger() -> Logger:
        return ConnectionSender._cLogger

    @property
    def sender_id(self) -> int:
        return self._sender_id

    @property
    def sender_start_time(self) -> int:
        return self._sender_start_time

    @property
    def current_seqno(self) -> int:
        return self._current_seqno

    def get_new_current_update(self) -> NetMsgUpdate:
        # should always be None when calling this method
        if self._current_update:
            raise DistributorException("Illegal state: mCurrentUpdate is not null")

        _msg = NetMsgUpdate(XtaSegment(self._configuration.segment_size))

        _msg.setHeader(message_type=Segment.MSG_TYPE_UPDATE,
                       segment_flags=Segment.FLAG_M_SEGMENT_START,
                       local_address=self._local_address,
                       sender_id=self._sender_id,
                       sender_start_time_sec=self._sender_start_time,
                       app_id=self._distributor.distributor_id())

        return _msg

    def publishUpdate(self, xta_update: XtaUpdate):
        return self.updateToSegment(xta_update)

    def flushHolback(self,  flush_request_seqno: int):
        if (self._current_update and
            flush_request_seqno == self._current_update.flush_seqno and
            self._current_update.update_count > 0):
                self.queueCurrentUpdate(Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END)


    def updateToSegment(self, xta_update: XtaUpdate):
        if xta_update.size > self._configuration.segment_size - NetMsgUpdate.MIN_UPDATE_HEADER_SIZE:
            self.largeUpdateToSegments(xta_update)
        else:
            self.smallUpdateToSegment(xta_update)

        if (self._configuration.send_holdback_delay_ms > 0 and
                self._traffic_flow_task.getUpdateRate() > self._configuration.send_holdback_threshold and
                Aux.currentMilliseconds() - self._current_update.create_time < self._configuration.send_holdback_delay_ms):
            if self._last_update_flush_seqno < self._current_update.flush_seqno:
                self._last_update_flush_seqno = self._current_update.flush_seqno
                _timerTask: SenderHoldbackTimerTask = SenderHoldbackTimerTask(
                    connection_id=self._connection.connection_id(),
                    flush_seqno=self._last_update_flush_seqno)
                ConnectionTimerExecutor.getInstance().queue(interval=self._configuration.send_holdback_delay_ms,
                                                            task=_timerTask)
            return 0
        # send message
        return self.queueCurrentUpdate(Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END)

    def smallUpdateToSegment(self, xta_update: XtaUpdate):
        if not self._current_update.addUpdate(xta_update):
            # send current segment and allocate a new empty one
            self.queueCurrentUpdate(Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END)

            if not self._current_update.addUpdate(xta_update):
                raise DistributorException('Update did not fit into segment, {} bytes'.format(xta_update.size))

    def largeUpdateToSegments(self, xta_update: XtaUpdate):
        # If we have updates in the current segment, queue and get a new segment
        self.queueCurrentUpdate(Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END)

        _offset: int = 0
        _segment_count = 0

        self._current_update.addLargeUpdateHeader(xta_update.subject, xta_update.data_length)

        while _offset < xta_update.data_length:
            _offset += self._current_update.addLargeData(xta_update.data, _offset)
            self._current_update.update_count = 1
            if _segment_count == 0:
                self.queueCurrentUpdate(Segment.FLAG_M_SEGMENT_START)
            elif _offset == xta_update.data_length:
                self.queueCurrentUpdate(Segment.FLAG_M_SEGMENT_END)
            else:
                self.queueCurrentUpdate(Segment.FLAG_M_SEGMENT_MORE)
            _segment_count += 1

    def queueCurrentUpdate(self, segment_flags: int) -> int:

        if self._current_update.update_count == 0:
            return 0  # No updates in segment we can continue to use this one

        self._current_update.sequence_no = self._current_seqno
        self._current_update.hdr_segment_flags = segment_flags

        self._current_update.encode()
        _send_delay = self.send_segment(self._current_update.segment)
        self._current_update = None
        self._current_update = self.get_new_current_update()
        return _send_delay

    def is_logging_enabled(self, flag: int):
        if self._distributor.configuration().log_flags() & flag:
            return True
        else:
            return False

    def log_info(self, message: str):
        ConnectionSender.logger().info(message)

    def random_error(self, probability: int):  # n/1000
        x = random.randrange(0, 1000)
        if x <= probability:
            return True
        return False

    def send_segment(self, segment: Segment):

        _send_time_usec: int = 0

        if self._error_signaled:
            return 0

        if segment.hdr_msg_type == Segment.MSG_TYPE_UPDATE:
            if self._configuration.max_bandwidth_kbit > 0:
                self._traffic_flow_task.increment(segment.length)
                _wait_ms = self._traffic_flow_task.calculateWaitTimeMs()
                Aux.sleepMs(_wait_ms)

        if self.is_logging_enabled(DistributorLogFlags.LOG_SEGMENTS_EVENTS):
            logInfo('XTA Segment: {}'.format(segment))

        if self.is_logging_enabled(DistributorLogFlags.LOG_DATA_PROTOCOL_XTA):
            logProtocolData(segment)

        if (self._configuration.fake_xta_error_rate > 0 and
                self.random_error(self._configuration.fake_xta_error_rate) and
                segment.hdr_msg_type == Segment.MSG_TYPE_UPDATE):
            logInfo('SIMULATED XTA Error Segment [{}] dropped'.format(segment.seqno))

        else:
            try:
                _send_time_usec = self._connection.send(segment)
                self._connection.traffic_statistic_task().updateXtaStatistics(segment, _send_time_usec)
            except Exception as e:
                self._error_signaled = True
                logThrowable(e)
                _event: DistributorCommunicationErrorEvent = DistributorCommunicationErrorEvent(direction="[SEND]",
                                                                                                mc_addr=self._connection.mc_address(),
                                                                                                mc_port=self._connection.mc_port(),
                                                                                                reason=str(e))
                ClientDeliveryController.getInstance().queueEvent(connection_id=self._connection.connection_id(), event=_event)

            if segment.hdr_msg_type == Segment.MSG_TYPE_UPDATE:
                self._retransmission_cache.addSentUpdate(segment)
                self._heartbeat_timer_task.dataHasBeenPublished()


        return _send_time_usec
