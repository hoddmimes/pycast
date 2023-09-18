from pymc.event_timers.connection_timer_event import ConnectionTimerEvent


class SenderHoldbackTimerTask(ConnectionTimerEvent):

    def __init__(self, connection_id: int, flush_seqno: int):
        super().__init__(connection_id)
        self._timer_flush_seqno = flush_seqno

    def execute(self, connection: 'Connection'):
        connection.flush_holdback(self._timer_flush_seqno)
