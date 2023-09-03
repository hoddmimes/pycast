from __future__ import annotations
import random

from pymc.aux.aux import Aux
from pymc.connection_configuration import ConnectionConfiguration
from pymc.distributor_interfaces import ConnectionReceiverBase, ConnectionBase
from pymc.client_controller import ClientDeliveryController
from pymc.msg.rcv_update import RcvUpdate
from pymc.remote_connection import RemoteConnection
from pymc.remote_connection_controller import RemoteConnectionController
from pymc.distributor_configuration import DistributorLogFlags
from pymc.msg.rcv_segment import RcvSegmentBatch
from pymc.msg.segment import Segment
from pymc.msg.net_msg import NetMsg
from pymc.msg.net_msg_configuration import NetMsgConfiguration
from pymc.msg.net_msg_heartbeat import NetMsgHeartbeat
from pymc.msg.net_msg_update import NetMsgUpdate
from pymc.msg.net_msg_retransmission import NetMsgRetransmissionRqst, NetMsgRetransmissionNAK
from pymc.ipmc_receiver_thread import IpmcReceiverThread

"""
=====================================================================
    ConnectionReceiver
======================================================================
"""


class ConnectionReceiver(ConnectionReceiverBase):

    def __init__(self, connection: ConnectionBase):
        self._connection: ConnectionBase = connection
        self._start_time = Aux.currentSeconds()
        self._configuration: ConnectionConfiguration = connection.configuration()
        self._remote_connection_controller = RemoteConnectionController(connection)
        self._rcv_threads: list[IpmcReceiverThread] = []
        for _i in range(self._configuration.receiver_threads):
            _thr = IpmcReceiverThread(logger=connection.logger(),
                                      ipmc=connection.ipmc(),
                                      connection_id=connection.connection_id(),
                                      index=(_i + 1),
                                      segment_size=self._configuration.segment_size)
            self._rcv_threads.append(_thr)
            _thr.start()

    def triggerRemoteConfigurationNotifications(self, callback):
        self._remote_connection_controller.triggerRemoteConfigurationNotifications(callback)

    def checkVersion(self, segment: Segment):
        _major = ((NetMsg.VERSION >> 8) & 0xff)
        _minor = (NetMsg.VERSION & 0xff)
        _msg_major = (segment.hdr_version >> 8) & 0xff
        _msg_minor = (segment.hdr_version & 0xff)
        if _major != _msg_major:
            self.logInfo("Received a segment with incompatible version Segment: {}.{} Distributor: {}.{}".
                         format(_msg_major, _msg_minor, _major, _minor))
            return False
        else:
            return True

    def close(self):
        for _thr in self._rcv_threads:
            _thr.stop()

    def isLogFlagSet(self, log_flag):
        if self._connection.is_logging_enabled(log_flag):
            return True
        return False

    def processConfigurationMsg(self, segment: Segment):
        self._remote_connection_controller.processConfigurationMessage(segment)
        if self.isLogFlagSet(DistributorLogFlags.LOG_DATA_PROTOCOL_RCV):
            _msg = NetMsgConfiguration(segment)
            _msg.decode()
            self.logInfo("PROTOCOL [RCV] {}".format(_msg))

    def processHeartbeatMsg(self, segment: Segment):
        self._remote_connection_controller.processHeartbeatMessage(segment)
        if self.isLogFlagSet(DistributorLogFlags.LOG_DATA_PROTOCOL_RCV):
            _msg = NetMsgHeartbeat(segment)
            _msg.decode()
            self.logInfo("PROTOCOL [RCV] {}".format(_msg))

    def processUpdateMsg(self, segment: Segment):
        _msg = NetMsgUpdate(segment)
        _msg.decode()

        if self._configuration.fake_rcv_error_rate > 0 and random_error(self._configuration.fake_rcv_error_rate):
            if self._connection.is_logging_enabled(DistributorLogFlags.LOG_RETRANSMISSION_EVENTS):
                self.logInfo("RETRANSMISSION:  RCV SIMULATED  Error Segment [{}] dropped".format(_msg.sequence_no))
        else:
            self._remote_connection_controller.processUpdateSegment(segment)
            if self.isLogFlagSet(DistributorLogFlags.LOG_DATA_PROTOCOL_RCV):
                if segment.hdr_msg_type == Segment.MSG_TYPE_UPDATE:
                    self.logInfo("PROTOCOL [RCV] <UPDATE> {}".format(_msg))
                else:
                    self.logInfo("PROTOCOL [RCV] <RETRANSMISSION> {}".format(_msg))

    def processRetransmissionNAK(self, segment: Segment):
        self._connection.retransmission_controller.processRetransmissionNAK(segment)
        if self.isLogFlagSet(DistributorLogFlags.LOG_DATA_PROTOCOL_RCV):
            _msg = NetMsgRetransmissionNAK(segment)
            _msg.decode()
            self.logInfo("PROTOCOL [RCV] {}".format(_msg))

    def processRetransmissionRqst(self, segment: Segment):
        _msg = NetMsgRetransmissionRqst(segment)
        _msg.decode()
        self._connection.connection_sender.retransmit(_msg)
        if self.isLogFlagSet(DistributorLogFlags.LOG_DATA_PROTOCOL_RCV):
            _msg.decode()
            self.logInfo("PROTOCOL [RCV] {}".format(_msg))


    def processReceivedSegment(self, segment: Segment):
        if segment.hdr_version != NetMsg.VERSION:
            if not self.checkVersion(segment):
                return
        if self.isLogFlagSet(DistributorLogFlags.LOG_SEGMENTS_EVENTS):
            _net_msg = NetMsg(segment)
            _net_msg.decode()
            self.logInfo("RCV Segment: {}".format(_net_msg))
        if segment.hdr_msg_type == Segment.MSG_TYPE_CONFIGURATION:
            self.processConfigurationMsg(segment)
        elif segment.hdr_msg_type == Segment.MSG_TYPE_HEARTBEAT:
            self.processHeartbeatMsg(segment)
        elif segment.hdr_msg_type == Segment.MSG_TYPE_RETRANSMISSION:
            self.processUpdateMsg(segment)
        elif segment.hdr_msg_type == Segment.MSG_TYPE_RETRANSMISSION_NAK:
            self.processRetransmissionNAK(segment)
        elif segment.hdr_msg_type == Segment.MSG_TYPE_RETRANSMISSION_RQST:
            self.processRetransmissionRqst(segment)
        elif segment.hdr_msg_type == Segment.MSG_TYPE_UPDATE:
            self.processUpdateMsg(segment)

    def processReceiveSegmentBatch(self, rcv_segment_batch: RcvSegmentBatch):
        _updates: list[RcvUpdate] = rcv_segment_batch.getUpdates(self._connection.connection_id())
        ClientDeliveryController.get_instance().queue_updates(self._connection.connection_id(), _updates)

    def logInfo(self, msg):
        self._connection.logInfo(msg)

    def logWarning(self, msg):
        self._connection.logWarning(msg)

    def logError(self, msg):
        self._connection.logError(msg)

    def logThrowable(self, exception):
        self._connection.logThrowable(exception)

    def get_remote_connection(self, remote_connection_id: int) -> RemoteConnection:
        return self._remote_connection_controller.getRemoteConnection(remote_connection_id);

def random_error(promille: int) -> bool:
    x: int = random.randrange(0, 1000)
    if promille <= x:
        return True
    else:
        return False
