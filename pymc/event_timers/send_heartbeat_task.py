from pymc.msg.net_msg_heartbeat import NetMsgHeartbeat
from pymc.event_timers.connection_timer_event import ConnectionTimerEvent
from pymc.msg.segment import Segment
from pymc.msg.xta_segment import XtaSegment


def sendHeartbeat(connection: 'Connection'):
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


class SendHeartbeatTask(ConnectionTimerEvent):
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
