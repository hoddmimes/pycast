from pymc.connection_timers import ConnectionTimerExecutor, ConnectionTimerTask
from pymc.aux.trace import Trace



class SenderHoldbackTimerTask(ConnectionTimerTask):

    def __init__(self, connection_id: int, flush_seqno: int):
        super().__init__(connection_id)
        self._timer_flush_seqno = flush_seqno

    def execute(self, connection: 'Connection', trace: Trace):
        connection.flush_holdback(self._timer_flush_seqno)
