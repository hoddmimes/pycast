from io import StringIO

from pymc.aux.linked_list import LinkedList
from pymc.msg.net_msg import NetMsg
from pymc.msg.net_msg_heartbeat import NetMsgHeartbeat
from pymc.msg.net_msg_update import NetMsgUpdate
from pymc.msg.rcv_segment import RcvSegmentBatch, RcvSegment
from pymc.msg.segment import Segment
from pymc.msg.net_msg_configuration import NetMsgConfiguration
from pymc.connection import Connection
from pymc.aux.aux import Aux
from pymc.aux.aux_uuid import Aux_UUID
from pymc.remote_connection_controller import RemoteConnectionController
from pymc.connection_timers import ConnectionTimerExecutor, ConnectionTimerTask
from pymc.distributor_configuration import DistributorLogFlags


class RemoteConnection(object):

    def __init__(self, segment: Segment, controller: RemoteConnectionController,  connection: Connection):
        self._remote_connection_id: int = Aux_UUID.getId()
        self._connection: Connection = connection
        self._hash_code: int = segment.__hash__()
        _msg = NetMsgConfiguration(segment)
        _msg.decode()
        self._remote_app_id: int  = segment.hdr_app_id
        self._connect_time_string: str = Aux.time_string()
        self._remote_host_address_string: str = Aux.ipAddrIntToStr(_msg.host_address)
        self._remote_host_address: int = _msg.host_address
        self._remote_sender_id: int = _msg.sender_id
        self._remote_start_time: int = _msg.send_start_time
        self._heartbeat_interval = _msg.hb_interval_ms
        self._configuration_interval = _msg.cfg_interval_ms
        self._remote_application_name = _msg.app_name
        self._configuration = connection.getConfiguration()
        self._remote_connection_controller = controller
        self._retransmission_controller = connection.retransmission_controller
        self._rcv_segment_batch = None
        self._pending_receiver_queue: LinkedList = LinkedList() # Linked list with unprocessed received segmenet
        self._hb_active = True
        self._cfg_is_active = True
        self._is_dead = False
        self._start_synchronized = False
        self._next_expected_seqno = 0
        self._highiest_seen_seqno = 0
        self._check_heartbeat_task = CheckHeartbeatTask(connection.connection_id, self._remote_connection_id)
        self._check_configuration_task = CheckConfigurationTask(connection.connection_id, self._remote_connection_id)

        _interval = (self._configuration.configuration.heartbeat_max_lost + 1) * self._configuration_interval
        ConnectionTimerExecutor.getInstance().queue( interval=_interval, task=  self._check_heartbeat_task, repeat=True)

        _interval = (self._configuration.configuration.configuration_max_lost + 1) * self._configuration_interval
        ConnectionTimerExecutor.getInstance().queue(interval=_interval, task=self._check_configuration_task, repeat=True)


    def __str__(self):
        sb = StringIO()
        sb.write("host: {}".format(self._remote_host_address_string))
        sb.write(" sender_id: {0:x}".format(self._remote_sender_id))
        sb.write(" start_time: {}".format( Aux.time_string( self._remote_start_time)))
        sb.write(" connect_time: {}".format(self._connect_time_string))
        sb.write(" appl_name: {} \n".format(self._remote_application_name))
        sb.write("    hb_interval: {}".format(self._heartbeat_interval))
        sb.write(" cfg_interval: {}".format(self._configuration_interval))
        sb.write(" local_mca: {}".format(Aux.ipAddrIntToStr(self._connection.mc_address)))
        return sb.getvalue()

    def processHeartbeatMsg(self, segment: Segment):
        _msg = NetMsgHeartbeat(segment)
        _msg.decode()
        self._hb_active = True
        if self._start_synchronized and self._highiest_seen_seqno < _msg.sequence_no:
            self._retransmission_controller.createRetransmissionRequest(self, self._highiest_seen_seqno + 1, _msg.sequence_no)
            self._highiest_seen_seqno = _msg.sequence_no

    def checkMessageSequence(self, msg: NetMsgUpdate):
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

    def segmentToRcvSegmentBatch(self, segment: Segment):
        if self._rcv_segment_batch is None:
            self._rcv_segment_batch = RcvSegmentBatch(RcvSegment(segment))
        else:
            self._rcv_segment_batch.addSegment(RcvSegment(segment))
        if segment.is_end_segment:
            self._connection.connection_receiver.processReceiveSegmentBatch(self._rcv_segment_batch)
            self._rcv_segment_batch = None

    def processPendingReceiverQueue(self):
        while True:
            if self._pending_receiver_queue.is_empty():
                return
            _msg = NetMsgUpdate(Segment.cast(self._pending_receiver_queue.peekFirst()))
            _msg.decode()
            if _msg.sequence_no == self._next_expected_seqno:
                self._next_expected_seqno += 1
                _rcv_segment = RcvSegment( Segment.cast(self._pending_receiver_queue.removeFirst()))
                if self._connection.isLogFlagSet(DistributorLogFlags.LOG_RETRANSMISSION_EVENTS):
                    self._connection.logInfo("RETRANSMISSION: RCV Process message from pending queue Segment [{}] QueueSize: {}".format( _rcv_segment.sequence_no, self._pending_receiver_queue.size))
                self.segmentToRcvSegmentBatch(_rcv_segment)
            else:
                return

    def processUpdateSegment(self, segment: Segment):

        if len(self._connections.subscribers) == 0:
            self._start_synchronized = False
            self._highiest_seen_seqno = 0
            return


        _msg: NetMsgUpdate = NetMsgUpdate(segment)
        _msg.decode()

        if segment.hdr_msg_type == Segment.MSG_TYPE_RETRANSMISSION:
            self._retransmission_controller.updateRetransmissions(segment)

        _action = self.checkMessageSequence(_msg)



        if _action == NetMsg.SequenceNumberActions.SYNCH:
            if segment.hdr_msg_type == Segment.MSG_TYPE_RETRANSMISSION and self._connection.isLogFlagSet(DistributorLogFlags.LOG_RETRANSMISSION_EVENTS):
                self._connection.logInfo("RETRANSMISSION: RCV Retransmission Segment [{}]".format(_msg.sequence_no))

            self._next_expected_seqno += 1
            if _msg.sequence_no > self._highiest_seen_seqno:
                self._highiest_seen_seqno = _msg.sequence_no

            self.segmentToRcvSegmentBatch(segment)

            if not self._pending_receiver_queue.is_empty():
                self.processPendingReceiverQueue()
        elif _action == NetMsg.IGNORE:
            return
        elif _action == NetMsg.LOWER:
            return
        elif _action == NetMsg.HIGHER:
            if _msg.sequence_no > self._highiest_seen_seqno + 1:
                self._retransmission_controller.createRetransmissionRequest( this, self._highiest_seen_seqno, _msg.sequence_no - 1)
            self._highiest_seen_seqno = _msg.sequence_no

            if self._connection.isLogFlagSet(DistributorLogFlags.LOG_RETRANSMISSION_EVENTS):
                self._connection.logInfo("RETRANSMISSION: RCV Message To Pending Queue Segment [{}]".format(_msg.sequence_no))
            self._retransmission_controller.updateRetransmissions(segment)
            self.segmentToPendingReceiverQueue(segment)

class CheckHeartbeatTask(ConnectionTimerTask):
    def __init__(self, connection_id: int , remote_connection_id: int):
        super().__init__(connection_id)
        self._remote_Connection_id = remote_connection_id

    def execute(self, connection: Connection):
        tRemoteConnection = (connection.connection_receiver.


                             mRemoteConnectionController.getRemoteConnection(self._remote_Connection_id))
        if tRemoteConnection == None:
            self.cancel()
            return
        try:
            if tRemoteConnection.isDead:
                self.cancel()
                return
            if pConnection.mTimeToDie:
                self.cancel()
                return
            if not tRemoteConnection.mHbIsActive:
                if pConnection.isLogFlagSet(DistributorApplicationConfiguration.LOG_RMTDB_EVENTS):
                    pConnection.log("Remote connction disconnected (no heartbeats) \n        " + tRemoteConnection.toString())
                tEvent = DistributorRemoveRemoteConnectionEvent(tRemoteConnection.mRemoteHostInetAddress, tRemoteConnection.mRemoteSenderId, tRemoteConnection.mMca.mInetAddress, tRemoteConnection.mMca.mPort, tRemoteConnection.mRemoteApplicationName, tRemoteConnection.mRemoteAppId)
                ClientDeliveryController.getInstance().queueEvent(pConnection._connection_id, tEvent)
                self.cancel()
                mRemoteConnectionController.removeRemoteConnection(RemoteConnection.this)
            else:
                tRemoteConnection.mHbIsActive = False
        except Exception as e:
            e.printStackTrace()

class CheckConfigurationTask(DistributorTimerTask):
    def __init__(self, pDistributorConnectionId, pRemoteConnectionId):
        super().__init__(pDistributorConnectionId)
        self.mRemoteConnectionId = pRemoteConnectionId

    def execute(self, pConnection):
        tRemoteConnection = pConnection.mConnectionReceiver.mRemoteConnectionController.getRemoteConnection(self.mRemoteConnectionId)
        if tRemoteConnection == None:
            self.cancel()
            return
        try:
            if tRemoteConnection.isDead:
                self.cancel()
                return
            if pConnection.mTimeToDie:
                self.cancel()
                return
            if not tRemoteConnection.mCfgIsActive:
                tRemoteConnection.isDead = True
                tRemoteConnection.mRemoteConnectionController.removeRemoteConnection(tRemoteConnection)
                if pConnection.isLogFlagSet(DistributorApplicationConfiguration.LOG_RMTDB_EVENTS):
                    pConnection.log("Remote connction disconnected (no configuration heartbeats) \n        " + tRemoteConnection.toString())
                tEvent = DistributorRemoveRemoteConnectionEvent(tRemoteConnection.mRemoteHostInetAddress, tRemoteConnection.mRemoteSenderId, tRemoteConnection.mMca.mInetAddress, tRemoteConnection.mMca.mPort, tRemoteConnection.mRemoteApplicationName, tRemoteConnection.mRemoteAppId)
                ClientDeliveryController.getInstance().queueEvent(pConnection._connection_id, tEvent)
                self.cancel()
            else:
                tRemoteConnection.mCfgIsActive = False
        except Exception as e:
            e.printStackTrace()