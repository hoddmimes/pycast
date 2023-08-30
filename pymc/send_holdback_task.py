from pymc.connection_timers import ConnectionTimerExecutor, ConnectionTimerTask
from pymc.connection import Connection


class SenderHoldbackTimerTask(ConnectionTimerTask):

    def __init__(self, connection_id: int, flush_seqno: int):
        super().__init__(connection_id)
        self._timer_flush_seqno = flush_seqno

    def execute(self, connection: Connection):
        connection.flushHoldback(self._timer_flush_seqno)
