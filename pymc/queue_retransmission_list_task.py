from pymc.event_timers.connection_timer_event import ConnectionTimerEvent
from pymc.retransmission_queue_item import RetransQueItm


class QueueRetransmissionListTask(ConnectionTimerEvent):
    def __init__(self, connection_id:int, retrans_list:list[RetransQueItm]):
        super().__init__(connection_id)
        self.mRetransList = list(reversed(retrans_list))

    def execute(self, connection: 'Connection'):
        if connection.mConnectionSender.mRetransmissionCache._is_dead:
            return
        connection.mConnectionSender.mRetransmissionCache.sendRetransmissions(self.mRetransList)
        self.mRetransList = None