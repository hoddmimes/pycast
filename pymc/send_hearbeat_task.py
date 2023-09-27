from pymc.connection_timer_task import ConnectionTimerTask
from pymc.msg.net_msg_heartbeat import NetMsgHeartbeat
from pymc.msg.segment import Segment
from pymc.msg.xta_segment import XtaSegment
from pymc.aux.trace import Trace


class SendHeartbeatTask(ConnectionTimerTask):
    def __init__(self, connection_id):
        super().__init__(connection_id)
        self._connection_is_sending = False

    def data_has_been_published(self):
        self._connection_is_sending = True

    def execute(self, connection: 'Connection', trace: Trace):
        if connection.is_time_to_die:
            super().cancel()
            return
        if len(connection.publishers) == 0:
            return
        if not self._connection_is_sending:
            self.send_heartbereat(connection)
        self._connection_is_sending = False

    def send_heartbereat(self, connection: 'Connection'):
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
