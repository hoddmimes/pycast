from pymc.aux.aux import Aux
from pymc.aux.linked_list import LinkedList, ListItr
from pymc.msg.segment import Segment
from pymc.msg.xta_segment import XtaSegment
from pymc.connection_sender import ConnectionSender
from pymc.msg.net_msg_retransmission import NetMsgRetransmissionNAK
from pymc.connection import Connection, ConnectionConfiguration
from pymc.connection_timers import ConnectionTimerTask, ConnectionTimerExecutor
from pymc.distributor_configuration import DistributorLogFlags


class RetransQueItm(object):
    def __init__(self, segment: Segment, sequence_no: int):
        self.mQueueTime: int = Aux.currentSeconds()
        self.mSegment: Segment = segment
        self.mSeqNo: int = sequence_no
        self.mInProgress: bool = False
        self.mResentCount: int = 0
        self.mCacheSize: int = 0
        self.mSegment.setHeaderMessageType(Segment.MSG_TYPE_RETRANSMISSION)


class CleanRetransmissionQueueTask(ConnectionTimerTask):
    def __init__(self, connection_id: int):
        super().__init__(connection_id)

    def execute(self, connection: Connection):
        t_removed_elements: int = 0
        t_cache_threshold_time = Aux.currentSeconds() - connection.mConfiguration.retrans_cache_life_time_sec
        t_cache: RetransmissionCache = connection.mConnectionSender.mRetransmissionCache
        if connection.isLoggingEnabled(DistributorLogFlags.LOG_RETRANSMISSION_CACHE):
            t_first_item: RetransQueItm = t_cache.mQueue.peekFirst()
            t_last_item: RetransQueItm = t_cache.mQueue.peekLast()
            if t_first_item:
                t_time_diff = t_first_item.mQueueTime - t_last_item.mQueueTime  # Diff in seconds
                connection.logInfo(
                    "RETRANSMISSON CACHE STATISTICS Connection: {}\n    size: {} elements: {} time-span: {} (sec)".
                    format(str(connection.mIpmc), t_cache.mCacheSize, t_cache.mQueue.size(), t_time_diff))
            else:
                connection.logInfo(
                    "RETRANSMISSON CACHE STATISTICS Connection: {}\n    size: 0 elements: 0 time-span: 0 (sec)".
                    format(str(connection.mIpmc)))

        _items_removed = 0
        _t_threshold_time = Aux.currentSeconds() - t_cache.mConfiguration.retrans_cache_life_time_sec
        _itr = ListItr(t_cache.mQueue)
        while _itr.has_next():
            t_que_itm: RetransQueItm = _itr.next()
            if t_cache.mConfiguration.retrans_cache_life_time_sec == 0 and t_cache.mCacheSize < t_cache.mConfiguration.retrans_max_cache_bytes:
                return
            if (t_que_itm.mQueueTime > _t_threshold_time and t_cache.mConfiguration.retrans_cache_life_time_sec > 0 and
                    t_cache.mCacheSize <= t_cache.mConfiguration.retrans_max_cache_bytes):
                return

            if not t_que_itm.mInProgress:
                _itr.remove()
                _items_removed += 1
                t_cache.mCacheSize -= t_que_itm.mSegment.getLength()
                t_que_itm.mSegment = None

class QueueRetransmissionListTask(ConnectionTimerTask):
    def __init__(self, connection_id:int, retrans_list:list[RetransQueItm]):
        super().__init__(connection_id)
        self.mRetransList = list(reversed(retrans_list))

    def execute(self, connection: Connection):
        if connection.mConnectionSender.mRetransmissionCache.mIsDead:
            return
        connection.mConnectionSender.mRetransmissionCache.sendRetransmissions(self.mRetransList)
        self.mRetransList = None

class RetransmissionCache(object):
    def __init__(self, sender: ConnectionSender):
        self.mConnection: Connection = sender.mConnection
        self.mConfiguration: ConnectionConfiguration = sender.mConnection._configuration
        self.mSender: ConnectionSender = sender
        self.mIsDead: bool = False
        self.mQueue: LinkedList = LinkedList()
        self.mCacheSize: int = 0
        self.mCleanCacheTask = CleanRetransmissionQueueTask(self.mConnection.mConnectionId)
        _interval_ms: int = self.mConfiguration.retrans_cache_clean_interval_sec * 1000
        ConnectionTimerExecutor.getInstance().queue(interval=_interval_ms,
                                                    task=self.mCleanCacheTask,
                                                    repeat=True)

    def close(self):
        self.mCleanCacheTask.cancel()
        self.mQueue.clear()

    def addSentUpdate(self, segment: Segment):
        _queitm: RetransQueItm = RetransQueItm(segment=segment, sequence_no=segment.getSeqno())
        self.mQueue.add(_queitm)
        self.mCacheSize += segment.getLength()
        self.microClean()

    def microClean(self):
        _itr: ListItr = ListItr(self.mQueue)
        while _itr.has_next():
            if self.mCacheSize <= self.mConfiguration.retrans_max_cache_bytes:
                return
            else:
                _queitm: RetransQueItm = _itr.next()
                _itr.remove()
                self.mCacheSize -= _queitm.mSegment.getLength()
                _queitm.mSegment = None

    def getRetransmissionNAKSequenceNumbers(self, pLowestRequestedSeqNo, pLowestSeqNoInCache) -> list[int]:
        _size = 0
        _NAKSeqNumbers = None
        if pLowestRequestedSeqNo < pLowestSeqNoInCache:
            return None
        _size = pLowestSeqNoInCache - pLowestRequestedSeqNo
        pNAKSeqNumbers = list(range(pLowestRequestedSeqNo, pLowestSeqNoInCache))
        return pNAKSeqNumbers

    def sendRetransmissionNAK(self, nak_seqno:list[int]):
        tNAKMsg = NetMsgRetransmissionNAK(XtaSegment(self.mConfiguration.small_segment_size))
        tNAKMsg.setHeader(messageType=Segment.MSG_TYPE_RETRANSMISSION_NAK,
                          segmentFlags=Segment.FLAG_M_SEGMENT_END + Segment.FLAG_M_SEGMENT_START,
                          localAddress=self.mSender.mLocalAddress,
                          senderId=self.mSender.mSenderId,
                          senderStartTime=self.mSender.mConnectionStartTime & 0xffffffff,
                          appId=self.mSender.mConnection.mDistributor.getAppId())

        tNAKMsg.set( mc_addr=self.mSender.mMca.mInetAddress, mc_port=self.mSender.mMca.mPort, sender_id=self.mSender.mSenderId)
        tNAKMsg.setNakSeqNo(nak_seqno)
        tNAKMsg.encode()
        self.mSender.send_segment(tNAKMsg._segment)

    def sendRetransmissions(self, retrans_list: list[RetransQueItm]):
        for tQueItm in retrans_list:
            tQueItm.mResentCount += 1
            if self.mConnection.isLogFlagSet(DistributorLogFlags.LOG_RETRANSMISSION_EVENTS):
                self.mConnection.logInfo("RETRANSMISSION: XTA RE-SENDING Segment [{}] resent-count: {}".
                                         format(tQueItm.mSeqNo, tQueItm.mResentCount))
            self.mSender.send_segment(tQueItm.mSegment)
            tQueItm.mInProgress = False

    def retransmit(self, low_seqno: int, high_seqno: int):
        tRetransList: list[RetransQueItm] = []
        tNAKSequenceNumbers = None

        if self.mConnection.isLogFlagSet(DistributorLogFlags.LOG_RETRANSMISSION_EVENTS):
            if self.mQueue.isEmpty():
                self.mConnection.logInfo("RETRANSMISSION: RCV Request for resending Segment [{}:{}] Cache is empty!".
                                         format(low_seqno, high_seqno))
            else:
                _first: RetransQueItm = self.mQueue.peekFirst()
                _last: RetransQueItm = self.mQueue.peekLast()
                self.mConnection.logInfo(
                    "RETRANSMISSION: RCV Request for resending Segment [{}:{}] Cache Segment [{}:{}]".
                    format(low_seqno, high_seqno, _first.mSeqNo, _last.mSeqNo))
            if self.mQueue.isEmpty():
                tNAKSequenceNumbers = self.getRetransmissionNAKSequenceNumbers(low_seqno, high_seqno)
            else:
                _first: RetransQueItm = self.mQueue.peekFirst()

                if low_seqno < _first.mSeqNo:
                    tNAKSequenceNumbers = self.getRetransmissionNAKSequenceNumbers(low_seqno, _first.mSeqNo)
                _itr = ListItr( linked_list=self.mQueue, forward=False )
                while _itr.has_next():
                    _que_itm = _itr.next()
                    if _que_itm.mSeqNo < low_seqno:
                        break
                    if _que_itm.mSeqNo >= low_seqno and _que_itm.mSeqNo <= high_seqno:
                        _que_itm.mInProgress = True
                        tRetransList.append(_que_itm)
        if tNAKSequenceNumbers is not None:
            self.sendRetransmissionNAK(tNAKSequenceNumbers)
        if len(tRetransList) > 0 and self.mConfiguration.retrans_server_holdback_ms > 0:
            tTask = QueueRetransmissionListTask(self.mConnection.mConnectionId, tRetransList)
            ConnectionTimerExecutor.getInstance().queue(self.mConfiguration.retrans_server_holdback_ms, tTask)
        elif len(tRetransList) > 0 and self.mConfiguration.retrans_server_holdback_ms <= 0:
            self.sendRetransmissions(tRetransList)


