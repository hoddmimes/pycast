from __future__ import annotations
import random
from typing import Callable

from pymc.aux.aux import Aux
from pymc.aux.distributor_exception import DistributorException
from pymc.connection_configuration import ConnectionConfiguration
from pymc.client_controller import ClientDeliveryController
from pymc.msg.rcv_update import RcvUpdate
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


class ConnectionReceiver(object):

    def __init__(self, connection: 'Connection'):
        self._connection: 'Connection' = connection
        self._start_time = Aux.current_seconds()
        self._configuration: ConnectionConfiguration = connection.configuration
        from pymc.remote_connection_controller import RemoteConnectionController
        self._remote_connection_controller = RemoteConnectionController(connection)
        self._rcv_threads: list[IpmcReceiverThread] = []
        for _i in range(self._configuration.receiver_threads):
            _thr = IpmcReceiverThread(logger=connection.logger,
                                      ipmc=connection.ipmc,
                                      connection_id=connection.connection_id,
                                      index=(_i + 1),
                                      segment_size=self._configuration.segment_size)
            self._rcv_threads.append(_thr)
            _thr.start()

    def triggerRemoteConfigurationNotifications(self, callback: Callable[['DistributorEvent'], None]):
        self._remote_connection_controller.triggerRemoteConfigurationNotifications(callback)

    def checkVersion(self, segment: Segment):
        _major = ((NetMsg.VERSION >> 8) & 0xff)
        _minor = (NetMsg.VERSION & 0xff)
        _msg_major = (segment.hdr_version >> 8) & 0xff
        _msg_minor = (segment.hdr_version & 0xff)
        if _major != _msg_major:
            self._connection.log_info("Received a segment with incompatible version Segment: {}.{} Distributor: {}.{}".
                          format(_msg_major, _msg_minor, _major, _minor))
            return False
        else:
            return True

    def close(self):
        for _thr in self._rcv_threads:
            _thr.stop()



    def processConfigurationMsg(self, segment: Segment):
        self._remote_connection_controller.processConfigurationMessage(segment)
        if self._connection.is_logging_enabled(DistributorLogFlags.LOG_DATA_PROTOCOL_RCV):
            _msg = NetMsgConfiguration(segment)
            _msg.decode()
            self._connection.log_info("PROTOCOL [RCV] [CONFIGURATION] {}".format(_msg))

    def processHeartbeatMsg(self, segment: Segment):
        self._remote_connection_controller.process_heartbeat_message(segment)
        if self._connection.is_logging_enabled(DistributorLogFlags.LOG_DATA_PROTOCOL_RCV):
            _msg = NetMsgHeartbeat(segment)
            _msg.decode()
            self._connection.log_info("PROTOCOL [RCV] [HEARTBEAT] {}".format(_msg))

    def processUpdateMsg(self, segment: Segment):
        _msg = NetMsgUpdate(segment)
        _msg.decode()

        if self._configuration.fake_rcv_error_rate > 0 and random_error(self._configuration.fake_rcv_error_rate):
            if self._connection.is_logging_enabled(DistributorLogFlags.LOG_RETRANSMISSION_EVENTS):
                self._connection.log_info("RETRANSMISSION: RCV SIMULATED  Error Segment [{}] dropped".format(_msg.sequence_no))
        else:
            self._remote_connection_controller.process_update_segment(segment)
            if self._connection.is_logging_enabled(DistributorLogFlags.LOG_DATA_PROTOCOL_RCV):
                if segment.hdr_msg_type == Segment.MSG_TYPE_UPDATE:
                    self._connection.log_info("PROTOCOL [RCV] [UPDATE] {}".format(_msg))
                else:
                    self._connection.log_info("PROTOCOL [RCV] [RETRANSMISSION] {}".format(_msg))

    def processRetransmissionNAK(self, segment: Segment):
        self._connection.retransmission_controller.processRetransmissionNAK(segment)
        if self._connection.is_logging_enabled(DistributorLogFlags.LOG_DATA_PROTOCOL_RCV):
            _msg = NetMsgRetransmissionNAK(segment)
            _msg.decode()
            self._connection.log_info("PROTOCOL [RCV] [RETRANS-NAK] {}".format(_msg))

    def processRetransmissionRqst(self, segment: Segment):
        _msg = NetMsgRetransmissionRqst(segment)
        _msg.decode()
        self._connection.connection_sender.retransmit(_msg)
        if self._connection.is_logging_enabled(DistributorLogFlags.LOG_DATA_PROTOCOL_RCV):
            _msg.decode()
            self._connection.log_info("PROTOCOL [RCV] [RETRANS_RQST] {}".format(_msg))

    def process_received_segment(self, segment: Segment):
        if segment.hdr_version != NetMsg.VERSION:
            if not self.checkVersion(segment):
                return
        if self._connection.is_logging_enabled(DistributorLogFlags.LOG_SEGMENTS_EVENTS):
            _net_msg = NetMsg(segment)
            _net_msg.decode()
            self._connection.log_info("RCV Segment: {}".format(_net_msg))

        match segment.hdr_msg_type:
            case Segment.MSG_TYPE_UPDATE:
                self.processUpdateMsg(segment)
            case Segment.MSG_TYPE_CONFIGURATION:
                self.processConfigurationMsg(segment)
            case Segment.MSG_TYPE_HEARTBEAT:
                self.processHeartbeatMsg(segment)
            case Segment.MSG_TYPE_RETRANSMISSION:
                self.processUpdateMsg(segment)
            case Segment.MSG_TYPE_RETRANSMISSION_NAK:
                self.processRetransmissionNAK(segment)
            case Segment.MSG_TYPE_RETRANSMISSION_RQST:
                self.processRetransmissionRqst(segment)
            case _:
                raise DistributorException("unknown received message type: {}".format(segment.hdr_msg_type))

    def process_receive_segment_batch(self, rcv_segment_batch: RcvSegmentBatch):
        _updates: list[RcvUpdate] = rcv_segment_batch.getUpdates(self._connection.connection_id)
        ClientDeliveryController.get_instance().queue_updates(self._connection.connection_id, _updates)

    def get_remote_connection_by_id(self, remote_connection_id: int) -> 'RemoteConnection':
        return self._remote_connection_controller.get_remote_connection_by_id(remote_connection_id);

    def remove_remote_connection(self, remote_connection: 'RemoteConnection'):
        self._remote_connection_controller.remove_remote_connection(remote_connection);


def random_error(promille: int) -> bool:
    x: int = random.randrange(0, 1000)
    if promille <= x:
        return True
    else:
        return False
