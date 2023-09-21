import random

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
from pymc.retransmission_cache import RetransmissionCache
from pymc.traffic_flow_task import TrafficFlowTask
from pymc.connection_configuration import ConnectionConfiguration
from pymc.aux.distributor_exception import DistributorException
from pymc.send_holdback_task import SenderHoldbackTimerTask
from pymc.connection_timers import ConnectionTimerExecutor, ConnectionTimerTask
from pymc.distributor_configuration import DistributorLogFlags
from pymc.client_controller import ClientDeliveryController



def sendHeartbeat(connection: 'Connection'):
    from pymc.distributor import Distributor
    _heartbeat = NetMsgHeartbeat(XtaSegment(connection.configuration.small_segment_size))
    _heartbeat.setHeader(
        message_type=Segment.MSG_TYPE_HEARTBEAT,
        segment_flags=Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END,
        local_address=connection.connection_sender.local_address,
        sender_id=connection.connection_sender.sender_id,
        sender_start_time_sec=connection.connection_sender.sender_start_time,
        app_id=Distributor.get_instance().app_id)

    _heartbeat.set(
        mc_addr=connection.ipmc.mc_address,
        mc_port=connection.ipmc.mc_port,
        sender_id=connection.connection_sender.sender_id,
        sequence_no=connection.connection_sender.current_seqno)
    _heartbeat.encode()
    from pymc.connection import Connection
    connection.connection_sender.send_segment(_heartbeat.segment)


class SendHeartbeatTask(ConnectionTimerTask):
    def __init__(self, connection_id):
        super().__init__(connection_id)
        self._connection_is_sending = False

    def dataHasBeenPublished(self):
        self._connection_is_sending = True

    def execute(self, connection: 'Connection'):
        if connection.is_time_to_die:
            super().cancel()
            return
        if len(connection.publishers) == 0:
            return
        if not self._connection_is_sending:
            sendHeartbeat(connection)
        self._connection_is_sending = False


def sendConfiguration(connection: 'Connection'):
    connection.push_out_configuration()
    connection.push_out_configuration()


class SendConfigurationTask(ConnectionTimerTask):
    def __init__(self, connection_id: int):
        super().__init__(connection_id)

    def execute(self, connection: 'Connection'):
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


def random_error(probability: int):  # n/1000
    x = random.randrange(0, 1000)
    if x <= probability:
        return True
    return False


class ConnectionSender(object):
    def __init__(self, connection: 'Connection'):
        self._sender_id: int = Aux_UUID.getId()
        self._error_signaled: bool = False
        self._sender_start_time = Aux.current_seconds()
        self._last_update_flush_seqno: int = 0
        self._connection: 'Connection' = connection


        self._heartbeat_timer_task = SendHeartbeatTask(connection_id=connection.connection_id)
        self._logger = connection.logger

        if connection.configuration.sender_id_port == 0:
            self._sender_id = Aux.allocate_server_port_id(connection.configuration.sender_id_port_offset)
        else:
            self._sender_id = connection.configuration.sender_id_port

        from pymc.distributor import Distributor
        self._local_address: int = Distributor.get_instance().local_address
        self._app_id: int = Distributor.get_instance().app_id
        self._current_seqno: int = 1 # Start at sequence number 1

        self._configuration: ConnectionConfiguration = connection.configuration

        self._current_update: NetMsgUpdate = None
        self._current_update = self.get_new_current_update()  # initialize self.mCurrentUpdate:NetMsgUpdate


        self._traffic_flow_task: TrafficFlowTask = TrafficFlowTask(connection_id=connection.connection_id,
                                                                   recalc_interval_ms=100,
                                                                   max_bandwidth_kbit_sec=connection.configuration.max_bandwidth_kbit)

        self._retransmission_cache = RetransmissionCache(self)

        from pymc.connection_timers import ConnectionTimerExecutor
        ConnectionTimerExecutor.getInstance().queue(interval=connection.configuration.heartbeat_interval_ms,
                                                    task=self._heartbeat_timer_task)

        ConnectionTimerExecutor.getInstance().queue(interval=1000, task=self._traffic_flow_task)


    def log_protocol_data(self, segment: Segment):
        _msg_type = segment.hdr_msg_type

        _segment = segment.clone_to_decoder()

        if _msg_type == Segment.MSG_TYPE_CONFIGURATION:
            _msg = NetMsgConfiguration(_segment)
            _msg.decode()
            self._connection.log_info("PROTOCOL [XTA] [CONFIGURATION] " + str(_msg))
        elif _msg_type == Segment.MSG_TYPE_HEARTBEAT:
            _msg = NetMsgHeartbeat(_segment)
            _msg.decode()
            self._connection.log_info("PROTOCOL [XTA] [HEARTBEAT]" + str(_msg))
        elif _msg_type == Segment.MSG_TYPE_RETRANSMISSION:
            _msg = NetMsgUpdate(_segment)
            _msg.decode()
            self._connection.log_info("PROTOCOL [XTA] [RETRANSMISSION]" + str(_msg))
        elif _msg_type == Segment.MSG_TYPE_RETRANSMISSION_NAK:
            _msg = NetMsgRetransmissionNAK(_segment)
            _msg.decode()
            self._connection.log_info("PROTOCOL [XTA] [RETRANS-NAK]" + str(_msg))
        elif _msg_type == Segment.MSG_TYPE_RETRANSMISSION_RQST:
            _msg = NetMsgRetransmissionRqst(_segment)
            _msg.decode()
            self._connection.log_info("PROTOCOL [XTA] [RETRANS-RQST]" + str(_msg))
        elif _msg_type == Segment.MSG_TYPE_UPDATE:
            _msg = NetMsgUpdate(_segment)
            _msg.decode()
            self._connection.log_info("PROTOCOL [XTA] [UPDATE] " + str(_msg))
        else:
            self._connection.log_info("PROTOCOL [XTA] unknown message: " + Segment.getMessageTypeString(_msg_type))

    @property
    def local_address(self) -> int:
        return self._local_address

    @property
    def sender_id(self) -> int:
        return self._sender_id

    @property
    def sender_start_time(self) -> int:
        return self._sender_start_time

    @property
    def current_seqno(self) -> int:
        return self._current_seqno

    @property
    def retransmission_cache(self) -> RetransmissionCache:
        return self._retransmission_cache

    @property
    def connection(self) -> 'Connection':
        return self._connection

    def retransmit(self, msg: NetMsgRetransmissionRqst):
        if msg.sender_start_time == self.sender_start_time and msg.sender_id == self.sender_id:
            self._connection.updateInRetransmissionStatistics(self._connection.mc_address(),
                                                              self._connection.mc_port,
                                                              msg, True)
            self._retransmission_cache.retransmit(msg.low_sequence_no, msg.high_sequence_no)
        else:
            self._connection.updateInRetransmissionStatistics(self._connection.mc_address(),
                                                              self._connection.mc_port,
                                                              msg, False)

    def get_new_current_update(self) -> NetMsgUpdate:
        # should always be None when calling this method
        if self._current_update:
            raise DistributorException("Illegal state: mCurrentUpdate is not null")

        _msg = NetMsgUpdate(XtaSegment(self._configuration.segment_size))

        _msg.setHeader(message_type=Segment.MSG_TYPE_UPDATE,
                       segment_flags=Segment.FLAG_M_SEGMENT_START,
                       local_address=self.local_address,
                       sender_id=self._sender_id,
                       sender_start_time_sec=self._sender_start_time,
                       app_id=self._app_id)

        return _msg

    def publish_update(self, xta_update: XtaUpdate) -> int:
        return self.update_to_segment(xta_update)

    def flush_holback(self, flush_request_seqno: int):
        if (self._current_update and
                flush_request_seqno == self._current_update.flush_seqno and
                self._current_update.update_count > 0):
            self.queue_current_update(Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END)

    def eval_outgoing_traffic_flow(self, bytes_sent: int) -> int:
        self._traffic_flow_task.increment(bytes_sent)
        return self._traffic_flow_task.calculate_wait_time_ms

    def update_to_segment(self, xta_update: XtaUpdate) -> int:
        if xta_update.size > self._configuration.segment_size - NetMsgUpdate.MIN_UPDATE_HEADER_SIZE:
            self.large_update_to_segments(xta_update)
        else:
            self.small_update_to_segment(xta_update)

        if (self._configuration.send_holdback_delay_ms > 0 and
                self._traffic_flow_task.get_update_rate() > self._configuration.send_holdback_threshold and
                Aux.current_milliseconds() - self._current_update.create_time < self._configuration.send_holdback_delay_ms):
            if self._last_update_flush_seqno < self._current_update.flush_seqno:
                self._last_update_flush_seqno = self._current_update.flush_seqno
                _timerTask: SenderHoldbackTimerTask = SenderHoldbackTimerTask(
                    connection_id=self._connection.connection_id,
                    flush_seqno=self._last_update_flush_seqno)
                ConnectionTimerExecutor.getInstance().queue(interval=self._configuration.send_holdback_delay_ms,
                                                            task=_timerTask)
                if self._connection.is_logging_enabled(DistributorLogFlags.LOG_TRAFFIC_FLOW_EVENTS):
                    self._connection.log_info("outgoing flow, queue new holdback flush timer seqno: {} holddback time: {} (ms)"
                                  .format(self._last_update_flush_seqno, self._configuration.send_holdback_delay_ms))
            return 0
        # send message
        return self.queue_current_update(Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END)

    def small_update_to_segment(self, xta_update: XtaUpdate):
        if not self._current_update.addUpdate(xta_update):
            # send current segment and allocate a new empty one
            self.queue_current_update(Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END)

            if not self._current_update.addUpdate(xta_update):
                raise DistributorException('Update did not fit into segment, {} bytes'.format(xta_update.size))

    def large_update_to_segments(self, xta_update: XtaUpdate):
        # If we have updates in the current segment, queue and get a new segment
        self.queue_current_update(Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END)

        _offset: int = 0
        _segment_count = 0

        self._current_update.addLargeUpdateHeader(xta_update.subject, xta_update.data_length)

        while _offset < xta_update.data_length:
            _offset += self._current_update.addLargeData(xta_update.data, _offset)
            self._current_update.update_count = 1
            if _segment_count == 0:
                self.queue_current_update(Segment.FLAG_M_SEGMENT_START)
            elif _offset == xta_update.data_length:
                self.queue_current_update(Segment.FLAG_M_SEGMENT_END)
            else:
                self.queue_current_update(Segment.FLAG_M_SEGMENT_MORE)
            _segment_count += 1

    def queue_current_update(self, segment_flags: int) -> int:

        if self._current_update.update_count == 0:
            return 0  # No updates in segment we can continue to use this one

        self._current_update.sequence_no = self._current_seqno
        self._current_update.hdr_segment_flags = segment_flags


        # self._current_update.encode()
        _send_delay = self.send_segment(self._current_update.segment)

        self._current_seqno += 1

        self._current_update = None
        self._current_update = self.get_new_current_update()
        return _send_delay

    def send_segment(self, segment: Segment):

        _send_time_usec: int = 0

        if self._error_signaled:
            return 0

        if segment.hdr_msg_type == Segment.MSG_TYPE_UPDATE:
            if self._configuration.max_bandwidth_kbit > 0:
                self._traffic_flow_task.increment(segment.length)
                _wait_ms = self._traffic_flow_task.calculate_wait_time_ms
                Aux.sleep_ms(_wait_ms)

        if self._connection.is_logging_enabled(DistributorLogFlags.LOG_SEGMENTS_EVENTS):
            self._connection.log_info('XTA Segment: {}'.format(segment))

        if self._connection.is_logging_enabled(DistributorLogFlags.LOG_DATA_PROTOCOL_XTA):
            self.log_protocol_data(segment)

        if (self._configuration.fake_xta_error_rate > 0 and
                random_error(self._configuration.fake_xta_error_rate) and
                segment.hdr_msg_type == Segment.MSG_TYPE_UPDATE):
            self._connection.log_info('SIMULATED XTA Error Segment [{}] dropped'.format(segment.seqno))

        else:
            try:
                _send_time_usec = self._connection.send(segment)
                self._connection.traffic_statistic_task.update_xta_statistics(segment, _send_time_usec)
            except Exception as e:
                self._error_signaled = True
                self._connection.log_exception(e)
                _event: DistributorCommunicationErrorEvent = DistributorCommunicationErrorEvent(direction="[SEND]",
                                                                                                mc_addr=self._connection.mc_address,
                                                                                                mc_port=self._connection.mc_port,
                                                                                                reason=str(e))
                ClientDeliveryController.get_instance().queue_event(connection_id=self._connection.connection_id,
                                                                    event=_event)

            if segment.hdr_msg_type == Segment.MSG_TYPE_UPDATE:
                self._retransmission_cache.addSentUpdate(segment)
                self._heartbeat_timer_task.dataHasBeenPublished()

        return _send_time_usec
