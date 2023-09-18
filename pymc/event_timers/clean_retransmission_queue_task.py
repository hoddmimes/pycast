from pymc.aux.aux import Aux
from pymc.aux.linked_list import ListItr
from pymc.distributor_configuration import DistributorLogFlags
from pymc.event_timers.connection_timer_event import ConnectionTimerEvent
from pymc.retransmission_queue_item import RetransQueItm


class CleanRetransmissionQueueTask(ConnectionTimerEvent):
    def __init__(self, connection_id: int):
        super().__init__(connection_id)
        self._retransmission_cache_queue_length: int = 0
        self._first_time: str = ''
        self._last_time: str = ''

    def __str__(self):
        return ("Cache queue-size {} first-item {} last-item {}"
                .format(self._retransmission_cache_queue_length, self._first_time, self._last_time))
    def execute(self, connection: 'Connection'):
        t_removed_elements: int = 0
        t_cache_threshold_time = Aux.current_seconds() - connection.configuration.retrans_cache_life_time_sec
        from pymc.retransmission_cache import RetransmissionCache
        t_cache: RetransmissionCache = connection.connection_sender.retransmission_cache
        t_first_item: RetransQueItm = t_cache.peakFirst
        t_last_item: RetransQueItm = t_cache.peakLast

        self._first_time = Aux.time_string(t_first_item.queue_time_sec)
        self._last_time = Aux.time_string(t_last_item.queue_time_sec)
        self._retransmission_cache_queue_length = t_cache.queue_size

        if connection.is_logging_enabled(DistributorLogFlags.LOG_RETRANSMISSION_CACHE):
            if t_first_item:
                t_time_diff = t_first_item._queue_time - t_last_item._queue_time  # Diff in seconds
                connection.log_info(
                    "RETRANSMISSON CACHE STATISTICS Connection: {}\n    size: {} elements: {} time-span: {} (sec)".
                    format(str(connection.mIpmc), t_cache._cache_size, t_cache.queue_size, t_time_diff))
            else:
                connection.log_info(
                    "RETRANSMISSON CACHE STATISTICS Connection: {}\n    size: 0 elements: 0 time-span: 0 (sec)".
                    format(str(connection.mIpmc)))

        _items_removed = 0
        _t_threshold_time = Aux.current_seconds() - t_cache._configuration.retrans_cache_life_time_sec
        _itr = ListItr(t_cache._queue)
        while _itr.has_next():
            t_que_itm: RetransQueItm = RetransQueItm.cast(_itr.next())
            if t_cache._configuration.retrans_cache_life_time_sec == 0 and t_cache._cache_size < t_cache._configuration.retrans_max_cache_bytes:
                return
            if (t_que_itm._queue_time > _t_threshold_time and t_cache._configuration.retrans_cache_life_time_sec > 0 and
                    t_cache._cache_size <= t_cache._configuration.retrans_max_cache_bytes):
                return

            if not t_que_itm._in_progress:
                _itr.remove()
                _items_removed += 1
                t_cache._cache_size -= t_que_itm.segment.length
                t_que_itm.segment = None