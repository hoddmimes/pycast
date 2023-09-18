from __future__ import annotations
from pymc.check_heartbeat_task import CheckHeartbeatTask
from pymc.client_controller import ClientDeliveryController
from pymc.distributor_events import DistributorRemoveRemoteConnectionEvent
from io import StringIO
from pymc.aux.linked_list import LinkedList
from pymc.msg.net_msg import NetMsg
from pymc.msg.net_msg_heartbeat import NetMsgHeartbeat
from pymc.msg.net_msg_update import NetMsgUpdate
from pymc.msg.rcv_segment import RcvSegmentBatch, RcvSegment
from pymc.msg.segment import Segment
from pymc.msg.net_msg_configuration import NetMsgConfiguration
from pymc.aux.aux import Aux
from pymc.aux.aux_uuid import Aux_UUID
from pymc.connection_timers import ConnectionTimerExecutor, ConnectionTimerTask
from pymc.distributor_configuration import DistributorLogFlags


class RemoteConnection(object):

    def __init__(self, segment: Segment, controller: 'RemoteConnectionController', connection: 'Connection'):
        self._remote_connection_id: int = Aux_UUID.getId()
        self._connection: 'Connection' = connection
        self._hash_code: int = segment.__hash__()
        _msg = NetMsgConfiguration(segment)
        _msg.decode()
        self._remote_app_id: int = segment.hdr_app_id
        self._connect_time_string: str = Aux.time_string()
        self._remote_host_address_string: str = Aux.ip_addr_int_to_str(_msg.host_address)
        self._remote_host_address: int = _msg.host_address
        self._remote_sender_id: int = _msg.sender_id
        self._remote_start_time: int = _msg.send_start_time
        self._heartbeat_interval = _msg.hb_interval_ms
        self._configuration_interval = _msg.cfg_interval_ms
        self._remote_application_name = _msg.app_name
        self._configuration = connection.configuration
        self._remote_connection_controller = controller
        self._retransmission_controller = connection.retransmission_controller
        self._ipmc = connection.ipmc
        self._rcv_segment_batch = None
        self._pending_receiver_queue: LinkedList = LinkedList()  # Linked list with unprocessed received segmenet
        self._hb_active = True
        self._cfg_is_active = True
        self._is_dead = False
        self._start_synchronized = False
        self._next_expected_seqno = 0
        self._highiest_seen_seqno = 0

        self._check_heartbeat_task = CheckHeartbeatTask(connection_id=connection.connection_id,
                                                        remote_connection_id=self._remote_connection_id)

        self._check_configuration_task = CheckConfigurationTask(connection_id=connection.connection_id,
                                                                remote_connection_id=self._remote_connection_id)

        _interval = (self._configuration.heartbeat_max_lost + 1) * self._configuration_interval
        ConnectionTimerExecutor.getInstance().queue(interval=_interval, task=self._check_heartbeat_task, repeat=True)

        _interval = (self._configuration.configuration_max_lost + 1) * self._configuration_interval
        ConnectionTimerExecutor.getInstance().queue(interval=_interval, task=self._check_configuration_task,
                                                    repeat=True)

    @property
    def remote_start_time(self) -> int:
        return self._remote_start_time

    @property
    def remote_application_id(self) -> int:
        return self._remote_app_id

    @property
    def remote_application_name(self) -> str:
        return self._remote_application_name

    @property
    def mc_address(self) -> int:
        return self._ipmc.mc_address

    @property
    def mc_port(self) -> int:
        return self._ipmc.mc_port

    @property
    def remote_sender_id(self) -> int:
        return self._remote_sender_id

    @property
    def remote_host_address(self) -> int:
        return self._remote_host_address

    @property
    def remote_host_address_string(self) -> str:
        return Aux.ip_addr_int_to_str(self._remote_host_address)

    @property
    def is_heartbeat_active(self) -> bool:
        return self._hb_active

    @is_heartbeat_active.setter
    def is_heartbeat_active(self, value: int):
        self._hb_active = value

    @property
    def is_dead(self) -> bool:
        return self._is_dead

    @is_dead.setter
    def is_dead(self, value: bool):
        self._is_dead = value

    @property
    def is_configuration_active(self) -> bool:
        return self._cfg_is_active

    @is_configuration_active.setter
    def is_configuration_active(self, value: int):
        self._cfg_is_active = value

    @property
    def remote_connection_id(self) -> int:
        return self._remote_connection_id

    @property
    def connection(self) -> 'Connection':
        return self._connection

    @property
    def highiest_seen_seqno(self) -> int:
        return self._highiest_seen_seqno

    def cancel(self):
        self._check_configuration_task.cancel()
        self._check_heartbeat_task.cancel()

    def __str__(self):
        sb = StringIO()
        sb.write("host: {}".format(self._remote_host_address_string))
        sb.write(" sender_id: {0:x}".format(self._remote_sender_id))
        sb.write(" start_time: {}".format(Aux.time_string(self._remote_start_time)))
        sb.write(" connect_time: {}".format(self._connect_time_string))
        sb.write(" appl_name: {} \n".format(self._remote_application_name))
        sb.write("    hb_interval: {}".format(self._heartbeat_interval))
        sb.write(" cfg_interval: {}".format(self._configuration_interval))
        sb.write(" local_mca: {}".format(Aux.ip_addr_int_to_str(self._connection.mc_address())))
        return sb.getvalue()

    def process_heartbeat_message(self, segment: Segment):
        _msg = NetMsgHeartbeat(segment)
        _msg.decode()
        self._hb_active = True
        if self._start_synchronized and self._highiest_seen_seqno < _msg.sequence_no:
            self._retransmission_controller.create_retransmission_request(self, self._highiest_seen_seqno + 1,
                                                                          _msg.sequence_no)
            self._highiest_seen_seqno = _msg.sequence_no

    def check_message_sequence(self, msg: NetMsgUpdate):
        if self._start_synchronized:
            _rcv_seqno = msg.sequence_no
            if _rcv_seqno == self._next_expected_seqno:
                return NetMsg.SYNCH
            elif _rcv_seqno > self._next_expected_seqno:
                return NetMsg.HIGHER
            else:
                return NetMsg.LOWER
        else:
            if msg.hdr_segment_flags & Segment.FLAG_M_SEGMENT_START != 0:
                self._start_synchronized = True
                self._highiest_seen_seqno = msg.sequence_no - 1
                self._next_expected_seqno = self._highiest_seen_seqno + 1
                return NetMsg.SYNCH
            else:
                return NetMsg.IGNORE

    def segment_to_rcv_segment_batch(self, segment: Segment):
        if self._rcv_segment_batch is None:
            self._rcv_segment_batch = RcvSegmentBatch(RcvSegment(segment))
        else:
            self._rcv_segment_batch.addSegment(RcvSegment(segment))
        if segment.is_end_segment:
            self._connection.connection_receiver.process_receive_segment_batch(self._rcv_segment_batch)
            self._rcv_segment_batch = None

    def process_pending_receiver_queue(self):
        while True:
            if self._pending_receiver_queue.is_empty():
                return
            _msg = NetMsgUpdate(Segment.cast(self._pending_receiver_queue.peekFirst()))
            _msg.decode()
            if _msg.sequence_no == self._next_expected_seqno:
                self._next_expected_seqno += 1
                _rcv_segment = RcvSegment(Segment.cast(self._pending_receiver_queue.removeFirst()))
                if self._connection.is_logging_enabled(DistributorLogFlags.LOG_RETRANSMISSION_EVENTS):
                    self._connection.lo(
                        "RETRANSMISSION: RCV Process message from pending queue Segment [{}] QueueSize: {}".format(
                            _rcv_segment.sequence_no, self._pending_receiver_queue.size))
                self.segment_to_rcv_segment_batch(_rcv_segment)
            else:
                return

    def segment_to_rcv_segment_batch(self, rcv_segment: RcvSegment):
        if self._rcv_segment_batch is None:
            self._rcv_segment_batch = RcvSegmentBatch(rcv_segment)
        else:
            self._rcv_segment_batch.addSegment(rcv_segment)

        if rcv_segment.is_end_segment:
            self._connection.connection_receiver.process_receive_segment_batch(self._rcv_segment_batch)
            self._rcv_segment_batch = None


    def processUpdateSegment(self, segment: Segment):

        if len(self._connection.subscribers) == 0:
            self._start_synchronized = False
            self._highiest_seen_seqno = 0
            return

        _msg: NetMsgUpdate = NetMsgUpdate(segment)
        _msg.decode()

        if segment.hdr_msg_type == Segment.MSG_TYPE_RETRANSMISSION:
            self._retransmission_controller.updateRetransmissions(segment)

        _action = self.check_message_sequence(_msg)

        if _action == NetMsg.SYNCH:
            if (segment.hdr_msg_type == Segment.MSG_TYPE_RETRANSMISSION and
                    self._connection.is_logging_enabled(DistributorLogFlags.LOG_RETRANSMISSION_EVENTS)):
                self._connection.log_info("RETRANSMISSION: RCV Retransmission Segment [{}]".format(_msg.sequence_no))

            self._next_expected_seqno += 1
            if _msg.sequence_no > self._highiest_seen_seqno:
                self._highiest_seen_seqno = _msg.sequence_no

            self.segment_to_rcv_segment_batch(segment)

            if not self._pending_receiver_queue.is_empty():
                self.process_pending_receiver_queue()
        elif _action == NetMsg.IGNORE:
            return
        elif _action == NetMsg.LOWER:
            return
        elif _action == NetMsg.HIGHER:
            if _msg.sequence_no > self._highiest_seen_seqno + 1:
                self._retransmission_controller.create_retransmission_request(self,
                                                                              self._highiest_seen_seqno,
                                                                              _msg.sequence_no - 1)
            self._highiest_seen_seqno = _msg.sequence_no

            if self._connection.is_logging_enabled(DistributorLogFlags.LOG_RETRANSMISSION_EVENTS):
                self._connection.log_info(
                    "RETRANSMISSION: RCV Message To Pending Queue Segment [{}]".format(_msg.sequence_no))
            self._retransmission_controller.updateRetransmissions(segment)
            self.segmentToPendingReceiverQueue(segment)





class CheckConfigurationTask(ConnectionTimerTask):
    def __init__(self, connection_id, remote_connection_id):
        super().__init__(connection_id)
        self.remote_connection_id = remote_connection_id

    def execute(self, connection):
        _remote_connection: RemoteConnection = connection.connection_receiver.get_remote_connection_by_id(self.remote_connection_id)
        if _remote_connection is None:
            self.cancel()
            return
        try:
            if _remote_connection.is_dead:
                self.cancel()
                return
            if connection.is_time_to_die:
                self.cancel()
                return
            if not _remote_connection.is_configuration_active:
                _remote_connection.is_dead = True
                connection.connection_receiver.remove_remote_connection(remote_connection=_remote_connection)
                if connection.is_logging_enabled(DistributorLogFlags.LOG_RMTDB_EVENTS):
                    connection.log_info("Remote connction disconnected (no configuration heartbeats) \n  {}"
                                        .format(_remote_connection))
                tEvent = DistributorRemoveRemoteConnectionEvent(source_addr=_remote_connection.remote_host_address,
                                                                sender_id=_remote_connection.remote_sender_id,
                                                                sender_start_time=_remote_connection.remote_start_time,
                                                                mc_addr=_remote_connection.mc_address,
                                                                mc_port=_remote_connection.mc_port,
                                                                appl_name=_remote_connection.remote_application_name,
                                                                appl_id=_remote_connection.remote_application_id)
                ClientDeliveryController.get_instance().queue_event(connection.connection_id, tEvent)
                self.cancel()
            else:
                _remote_connection.is_configuration_active = False
        except Exception as e:
            connection.log_exception(e)
