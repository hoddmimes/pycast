from __future__ import annotations
from pymc.aux.linked_list import LinkedList, ListItr
from pymc.event_timers.clean_retransmission_queue_task import CleanRetransmissionQueueTask
from pymc.msg.segment import Segment
from pymc.msg.xta_segment import XtaSegment
from pymc.msg.net_msg_retransmission import NetMsgRetransmissionNAK
from pymc.connection import ConnectionConfiguration
from pymc.connection_timers import ConnectionTimerExecutor
from pymc.distributor_configuration import DistributorLogFlags
from pymc.queue_retransmission_list_task import QueueRetransmissionListTask
from pymc.retransmission_queue_item import RetransQueItm


class RetransmissionCache(object):
    def __init__(self, sender: 'ConnectionSender'):
        self._connection: 'Connection' = sender.connection
        self._configuration: ConnectionConfiguration = sender.connection.configuration
        self._sender: 'ConnectionSender' = sender
        self._is_dead: bool = False
        self._queue: LinkedList = LinkedList()
        self._cache_size: int = 0
        self._clean_cache_task = CleanRetransmissionQueueTask(self._connection.connection_id)
        _interval_ms: int = self._configuration.retrans_cache_clean_interval_sec * 1000
        ConnectionTimerExecutor.getInstance().queue(interval=_interval_ms,
                                                    task=self._clean_cache_task,
                                                    repeat=True)

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

    def addSentUpdate(self, segment: Segment):
        _queitm: RetransQueItm = RetransQueItm(segment=segment, sequence_no=segment.seqno)
        self._queue.add(_queitm)
        self._cache_size += segment.length
        self.microClean()

    def microClean(self):
        _itr: ListItr = ListItr(self._queue)
        while _itr.has_next():
            if self._cache_size <= self._configuration.retrans_max_cache_bytes:
                return
            else:
                _queitm: RetransQueItm = RetransQueItm.cast(_itr.next())
                _itr.remove()
                self._cache_size -= _queitm.segment.length
                _queitm.segment = None

    def getRetransmissionNAKSequenceNumbers(self, pLowestRequestedSeqNo, pLowestSeqNoInCache) -> list[int]:
        _size = 0
        _NAKSeqNumbers = None
        if pLowestRequestedSeqNo < pLowestSeqNoInCache:
            return None
        _size = pLowestSeqNoInCache - pLowestRequestedSeqNo
        pNAKSeqNumbers = list(range(pLowestRequestedSeqNo, pLowestSeqNoInCache))
        return pNAKSeqNumbers

    def sendRetransmissionNAK(self, nak_seqno:list[int]):
        tNAKMsg = NetMsgRetransmissionNAK(XtaSegment(self._configuration.small_segment_size))
        tNAKMsg.setHeader(message_type=Segment.MSG_TYPE_RETRANSMISSION_NAK,
                          segment_flags=Segment.FLAG_M_SEGMENT_END + Segment.FLAG_M_SEGMENT_START,
                          local_address=self._sender.mLocalAddress,
                          sender_id=self._sender.mSenderId,
                          sender_start_time_sec=self._sender.sender_start_time,
                          app_id=self._sender._connection.mDistributor.getAppId())

        tNAKMsg.set(mc_addr=self._sender.mMca.mInetAddress, mc_port=self._sender.mMca.mPort, sender_id=self._sender.mSenderId)
        tNAKMsg.setNakSeqNo(nak_seqno)
        tNAKMsg.encode()
        self._sender.send_segment(tNAKMsg._segment)

    def sendRetransmissions(self, retrans_list: list[RetransQueItm]):
        for tQueItm in retrans_list:
            tQueItm._resent_count += 1
            if self._connection.isLogFlagSet(DistributorLogFlags.LOG_RETRANSMISSION_EVENTS):
                self._connection.log_info("RETRANSMISSION: XTA RE-SENDING Segment [{}] resent-count: {}".
                                          format(tQueItm._seqno, tQueItm._resent_count))
            self._sender.send_segment(tQueItm.segment)
            tQueItm._in_progress = False

    def retransmit(self, low_seqno: int, high_seqno: int):
        tRetransList: list[RetransQueItm] = []
        tNAKSequenceNumbers = None

        if self._connection.isLogFlagSet(DistributorLogFlags.LOG_RETRANSMISSION_EVENTS):
            if self._queue.is_empty:
                self._connection.log_info("RETRANSMISSION: RCV Request for resending Segment [{}:{}] Cache is empty!".
                                          format(low_seqno, high_seqno))
            else:
                _first: RetransQueItm = RetransQueItm.cast(self._queue.peekFirst())
                _last: RetransQueItm = RetransQueItm.cast(self._queue.peekLast())
                self._connection.log_info(
                    "RETRANSMISSION: RCV Request for resending Segment [{}:{}] Cache Segment [{}:{}]".
                    format(low_seqno, high_seqno, _first._seqno, _last._seqno))
            if self._queue.is_empty:
                tNAKSequenceNumbers = self.getRetransmissionNAKSequenceNumbers(low_seqno, high_seqno)
            else:
                _first: RetransQueItm = RetransQueItm(self._queue.peekFirst())

                if low_seqno < _first._seqno:
                    tNAKSequenceNumbers = self.getRetransmissionNAKSequenceNumbers(low_seqno, _first._seqno)
                _itr = ListItr(linked_list=self._queue, forward=False)
                while _itr.has_next():
                    _que_itm: RetransQueItm = RetransQueItm.cast(_itr.next())
                    if _que_itm.seqno < low_seqno:
                        break
                    if _que_itm.seqno >= low_seqno and _que_itm.seqno <= high_seqno:
                        _que_itm.mInProgress = True
                        tRetransList.append(_que_itm)
        if tNAKSequenceNumbers is not None:
            self.sendRetransmissionNAK(tNAKSequenceNumbers)
        if len(tRetransList) > 0 and self._configuration.retrans_server_holdback_ms > 0:
            tTask = QueueRetransmissionListTask(self._connection.mConnectionId, tRetransList)
            ConnectionTimerExecutor.getInstance().queue(self._configuration.retrans_server_holdback_ms, tTask)
        elif len(tRetransList) > 0 and self._configuration.retrans_server_holdback_ms <= 0:
            self.sendRetransmissions(tRetransList)


