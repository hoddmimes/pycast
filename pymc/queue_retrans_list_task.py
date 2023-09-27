from pymc.connection_timer_task import ConnectionTimerTask
from pymc.retransmission_cache import RetransQueItm
from pymc.aux.trace import Trace


class QueueRetransmissionListTask(ConnectionTimerTask):
    def __init__(self, connection_id: int, retrans_list: list[RetransQueItm]):
        super().__init__(connection_id)
        self._retrans_list = list(reversed(retrans_list))

    def execute(self, connection: 'Connection', trace: Trace):
        connection.connection_sender.retransmission_cache.send_retransmissions(self._retrans_list)
        self._retrans_list = None
