'''
Copyright 2023 Hoddmimes Solutions AB

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from __future__ import annotations
from pymc.aux.aux import Aux
from pymc.aux.distributor_exception import DistributorException
from pymc.aux.linked_list import LinkedList, ListItr
from pymc.msg.segment import Segment
from pymc.msg.xta_segment import XtaSegment
from pymc.msg.net_msg_retransmission import NetMsgRetransmissionNAK
from pymc.connection import ConnectionConfiguration
from pymc.connection_timers import ConnectionTimerTask, ConnectionTimerExecutor
from pymc.distributor_configuration import DistributorLogFlags
from pymc.aux.trace import Trace

class RetransQueItm(object):
    def __init__(self, segment: Segment, sequence_no: int):
        self.queue_time: int = Aux.current_seconds()
        self.segment: Segment = segment
        self.seqno: int = sequence_no
        self.in_progress: bool = False
        self.resent_count: int = 0
        self.cache_size: int = 0
        self.segment.hdr_msg_type = Segment.MSG_TYPE_RETRANSMISSION

    @classmethod
    def cast(cls, obj) -> RetransQueItm:
        if isinstance(obj, RetransQueItm):
            return obj
        else:
            raise DistributorException('object is not an instance of RetransQueItm')



class CleanRetransmissionQueueTask(ConnectionTimerTask):
    def __init__(self, connection_id: int):
        super().__init__(connection_id)

    def execute(self, connection: 'Connection', trace: Trace):
        t_removed_elements: int = 0
        t_cache_threshold_time = Aux.current_seconds() - connection.configuration.retrans_cache_life_time_sec
        t_cache: RetransmissionCache = connection.connection_sender.retransmission_cache
        if connection.is_logging_enabled(DistributorLogFlags.LOG_RETRANSMISSION_CACHE):
            t_first_item: RetransQueItm = t_cache.peakFirst
            t_last_item: RetransQueItm = t_cache.peakLast
            if t_first_item:
                t_time_diff = t_last_item.queue_time - t_first_item.queue_time   # Diff in seconds
                connection.log_info(
                    "RETRANSMISSON CACHE STATISTICS Connection: {}\n    size: {} elements: {} time-span: {} (sec)".
                        format(str(connection.ipmc), t_cache._cache_size, t_cache.queue_size, t_time_diff))
            else:
                connection.log_info(
                    "RETRANSMISSON CACHE STATISTICS Connection: {}\n    size: 0 elements: 0 time-span: 0 (sec)".
                    format(str(connection.ipmc)))

        _items_removed = 0
        _t_threshold_time = Aux.current_seconds() - t_cache._configuration.retrans_cache_life_time_sec
        _itr = ListItr(t_cache._queue)
        while _itr.has_next():
            t_que_itm: RetransQueItm = RetransQueItm.cast(_itr.next())
            if t_cache._configuration.retrans_cache_life_time_sec == 0 and t_cache._cache_size < t_cache._configuration.retrans_max_cache_bytes:
                return
            if (t_que_itm.queue_time > _t_threshold_time and t_cache._configuration.retrans_cache_life_time_sec > 0 and
                    t_cache._cache_size <= t_cache._configuration.retrans_max_cache_bytes):
                return

            if not t_que_itm.in_progress:
                _itr.remove()
                _items_removed += 1
                t_cache._cache_size -= t_que_itm.segment.length
                t_que_itm.segment = None



class RetransmissionCache(object):
    def __init__(self, sender: 'ConnectionSender'):
        self._connection: 'Connection' = sender.connection
        self._configuration: ConnectionConfiguration = sender.connection.configuration
        self._sender: 'ConnectionSender' = sender
        self._is_dead: bool = False
        self._queue: LinkedList = LinkedList()
        self._local_address = 0
        self._cache_size: int = 0
        self._clean_cache_task = CleanRetransmissionQueueTask(self._connection.connection_id)
        _interval_ms: int = self._connection.configuration.retrans_cache_clean_interval_sec * 1000
        ConnectionTimerExecutor.getInstance().queue(interval=_interval_ms,
                                                    task=self._clean_cache_task,
                                                    repeat=True)


    @property
    def local_address(self) -> int:
        if self._local_address == 0:
            from pymc.distributor import Distributor
            self._local_address = Distributor.get_instance().local_address
        return self._local_address

    @property
    def queue_size(self) -> int:
        return self._queue.size

    @property
    def peakFirst(self) -> RetransQueItm:
        return RetransQueItm.cast(self._queue.peekFirst())

    @property
    def peakLast(self) -> RetransQueItm:
        return RetransQueItm.cast(self._queue.peekLast())


    def close(self):
        self._clean_cache_task.cancel()
        self._queue.clear()

    def add_sent_update(self, segment: Segment):
        segment.hdr_msg_type = Segment.MSG_TYPE_RETRANSMISSION
        _queitm: RetransQueItm = RetransQueItm(segment=segment, sequence_no=segment.seqno)
        self._queue.add(_queitm)
        self._cache_size += segment.length
        self.micro_clean()

    def micro_clean(self):
        _itr: ListItr = ListItr(self._queue)
        while _itr.has_next():
            if self._cache_size <= self._configuration.retrans_max_cache_bytes:
                return
            else:
                _queitm: RetransQueItm = RetransQueItm.cast(_itr.next())
                _itr.remove()
                self._cache_size -= _queitm.segment.length
                _queitm.segment = None

    def get_retransmission_nak_sequence_numbers(self, pLowestRequestedSeqNo, pLowestSeqNoInCache) -> list[int]:
        _size = 0
        _NAKSeqNumbers = None
        if pLowestRequestedSeqNo < pLowestSeqNoInCache:
            return None
        _size = pLowestSeqNoInCache - pLowestRequestedSeqNo
        pNAKSeqNumbers = list(range(pLowestRequestedSeqNo, pLowestSeqNoInCache))
        return pNAKSeqNumbers

    def send_retransmission_nak(self, nak_seqno:list[int]):
        from pymc.distributor import Distributor
        tNAKMsg = NetMsgRetransmissionNAK(XtaSegment(self._configuration.small_segment_size))
        tNAKMsg.setHeader(message_type=Segment.MSG_TYPE_RETRANSMISSION_NAK,
                          segment_flags=Segment.FLAG_M_SEGMENT_END + Segment.FLAG_M_SEGMENT_START,
                          local_address=self._sender.local_address,
                          sender_id=self._sender.sender_id,
                          sender_start_time_sec=self._sender.sender_start_time,
                          app_id=Distributor.get_instance().app_id)

        tNAKMsg.set(mc_addr=self._sender.connection.mc_address,
                    mc_port=self._sender.connection.mc_port,
                    sender_id=self._sender.sender_id)
        tNAKMsg.setNakSeqNo(nak_seqno)
        tNAKMsg.encode()
        self._sender.send_segment(tNAKMsg._segment)

    def send_retransmissions(self, retrans_list: list[RetransQueItm]):
        for tQueItm in retrans_list:
            tQueItm.resent_count += 1
            if self._connection.is_logging_enabled(DistributorLogFlags.LOG_RETRANSMISSION_EVENTS):
                self._connection.log_info("RETRANSMISSION: XTA RE-SENDING Segment [{}] resent-count: {}".
                                          format(tQueItm.seqno, tQueItm.resent_count))

            self._sender.send_segment(tQueItm.segment)
            tQueItm.in_progress = False

    def retransmit(self, low_seqno: int, high_seqno: int):
        _retrans_list: list[RetransQueItm] = []
        nak_sequence_numbers = None

        if self._connection.is_logging_enabled(DistributorLogFlags.LOG_RETRANSMISSION_EVENTS):
            if self._queue.is_empty():
                self._connection.log_info("RETRANSMISSION: RCV Request for resending Segment [{}:{}] Cache is empty!!!".
                                          format(low_seqno, high_seqno))
            else:
                _first: RetransQueItm = RetransQueItm.cast(self._queue.peekFirst())
                _last: RetransQueItm = RetransQueItm.cast(self._queue.peekLast())
                self._connection.log_info(
                    "RETRANSMISSION: RCV Request for resending Segment [{}:{}] Cache Segment [{}:{}]".
                    format(low_seqno, high_seqno, _first.seqno, _last.seqno))
            if self._queue.is_empty():
                nak_sequence_numbers = self.get_retransmission_nak_sequence_numbers(low_seqno, high_seqno)
            else:
                _first: RetransQueItm = RetransQueItm.cast(self._queue.peekFirst())

                if low_seqno < _first.seqno:
                    nak_sequence_numbers = self.get_retransmission_nak_sequence_numbers(low_seqno, _first.seqno)
                _itr = ListItr(linked_list=self._queue, forward=False)
                while _itr.has_previous():
                    _que_itm: RetransQueItm = RetransQueItm.cast(_itr.previous())
                    if _que_itm.seqno < low_seqno:
                        break
                    if _que_itm.seqno >= low_seqno and _que_itm.seqno <= high_seqno:
                        _que_itm.in_progress = True
                        _retrans_list.append(_que_itm)
        if nak_sequence_numbers is not None:
            self.send_retransmission_nak(nak_sequence_numbers)
        if len(_retrans_list) > 0 and self._configuration.retrans_server_holdback_ms > 0:
            from pymc.queue_retrans_list_task import QueueRetransmissionListTask
            _task = QueueRetransmissionListTask(self._connection.connection_id, _retrans_list)
            ConnectionTimerExecutor.getInstance().queue(interval=self._configuration.retrans_server_holdback_ms, task=_task, repeat=False)
        elif len(_retrans_list) > 0 and self._configuration.retrans_server_holdback_ms <= 0:
            self.send_retransmissions(_retrans_list)


