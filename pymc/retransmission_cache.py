from pymc.aux.aux import Aux
from pymc.msg.segment import Segment
from pymc.connection_sender import ConnectionSender
from pymc.connection import Connection, ConnectionConfiguration
from pymc.connection_timers import ConnectionTimerTask, ConnectionTimerExecutor
class RetransQueItm(object):
    def __init__(self, segment:Segment, sequence_no:int):
        self.mQueueTime:int = Aux.currentSeconds()
        self.mSegment:int = segment
        self.mSeqNo:int = sequence_no
        self.mInProgress:bool = False
        self.mResentCount:int = 0
        self.mSegment.setHeaderMessageType(Segment.MSG_TYPE_RETRANSMISSION)

class CleanRetransmissionQueueTask(ConnectionTimerTask):
        def __init__(self, connection_id:int):
            super().__init__(connection_id)

        def execute(self, pConnection):
            t_removed_elements:int = 0
            t_cache_threshold_time = Aux.currentSeconds() - pConnection.mConfiguration.retrans_cache_life_time_sec
            mCache = pConnection.mConnectionSender.mRetransmissionCache
            if mConnection.isLogFlagSet(DistributorApplicationConfiguration.LOG_RETRANSMISSION_CACHE):
                if len(mQueue) > 0:
                    tFirstItem = mQueue[0]
                    tLastItem = mQueue[-1]
                    tTimeDiff = tLastItem.mQueueTime - tFirstItem.mQueueTime  # Diff in seconds
                    mConnection.log("RETRANSMISSON CACHE STATISTICS Connection: " + mConnection.mIpmg.toString() + "\n" +
                                    "    size: " + str(mCacheSize) + " elements: " + str(len(mQueue)) + " time-span: " +
                                    str(tTimeDiff) + " (sec)")
                else:
                    mConnection.log("RETRANSMISSON CACHE STATISTICS Connection: " + mConnection.mIpmg.toString() + "\n" +
                                    "    size: 0 elements: 0 time-span: 0 (sec)")
            mItr = iter(mCache.mQueue)
            for tQueItm in mItr:
                if mCache.mConfiguration.getRetransmissionCacheLifeTime() == 0 and mCache.mCacheSize <= mCache.mConfiguration.getRetransmissionMaxCacheSize():
                    return
                elif tQueItm.mQueueTime > tCacheThresholdTime and mCache.mConfiguration.getRetransmissionCacheLifeTime() != 0 and mCache.mCacheSize <= mCache.mConfiguration.getRetransmissionMaxCacheSize():
                    return
                else:
                    if not tQueItm.mInProgress:
                        mItr.remove()
                        t_remove_elements += 1
                        mCache.mCacheSize -= tQueItm.mSegment.getLength()
                        tQueItm.mSegment = None
                        tQueItm = None


class RetransmissionCache(object):
    def __init__(self, sender:ConnectionSender):
        self.mConnection:Connection = sender.mConnection
        self.mConfiguration:ConnectionConfiguration = sender.mConnection.mConfiguration
        self.mSender:ConnectionSender = sender
        self.mIsDead:bool = False
        self.mQueue:list[RetransQueItm] = []
        self.mCacheSize:int = 0
        self.mCleanCacheTask = CleanRetransmissionQueueTask(self.mConnection.mConnectionId)
        tInterval = self.mConfiguration.getRetransmissionCacheCleanInterval()
        DistributorTimers.getInstance().queue(tInterval, tInterval, self.mCleanCacheTask)

    def close(self):
        self.mCleanCacheTask.cancel()
        self.mQueue.clear()

    def addSentUpdate(self, pSegment):
        with self.mQueue:
            self.mQueue.append(RetransQueItm(pSegment, pSegment.getSeqno()))
            self.mCacheSize += pSegment.getLength()
            self.microClean()

    def microClean(self):
        mItr = iter(self.mQueue)
        for tQueItm in mItr:
            if self.mCacheSize <= self.mConfiguration.getRetransmissionMaxCacheSize():
                return
            else:
                if not tQueItm.mInProgress:
                    mItr.remove()
                    self.mCacheSize -= tQueItm.mSegment.getLength()
                    tQueItm.mSegment = None
                    tQueItm = None

    def getRetransmissionNAKSequenceNumbers(self, pLowestRequestedSeqNo, pLowestSeqNoInCache):
        tSize = 0
        pNAKSeqNumbers = None
        if pLowestRequestedSeqNo < pLowestSeqNoInCache:
            return None
        tSize = pLowestSeqNoInCache - pLowestRequestedSeqNo
        pNAKSeqNumbers = list(range(pLowestRequestedSeqNo, pLowestSeqNoInCache))
        return pNAKSeqNumbers

    def sendRetransmissionNAK(self, pNAKSeqNumbers):
        tNAKMsg = NetMsgRetransmissionNAK(XtaSegment(self.mConfiguration.getSmallSegmentSize()))
        tNAKMsg.setHeader(Segment.MSG_TYPE_RETRANSMISSION_NAK,
                          Segment.FLAG_M_SEGMENT_END + Segment.FLAG_M_SEGMENT_START,
                          self.mSender.mLocalAddress,
                          self.mSender.mSenderId,
                          self.mSender.mConnectionStartTime & 0xffffffff,
                          self.mSender.mConnection.mDistributor.getAppId())
        tNAKMsg.set(self.mSender.mMca.mInetAddress, self.mSender.mMca.mPort, self.mSender.mSenderId)
        tNAKMsg.setNakSeqNo(pNAKSeqNumbers)
        tNAKMsg.encode()
        self.mSender.sendSegment(tNAKMsg.mSegment)
        tNAKMsg = None

    def sendRetransmissions(self, mRetransList):
        tItr = reversed(mRetransList)
        for tQueItm in tItr:
            tQueItm.mResentCount += 1
            if self.mConnection.isLogFlagSet(DistributorApplicationConfiguration.LOG_RETRANSMISSION_EVENTS):
                self.mConnection.log("RETRANSMISSION: XTA RE-SENDING Segment [" +
                                     str(tQueItm.mSeqNo) + "] ResentCount: " +
                                     str(tQueItm.mResentCount))
            self.mSender.sendSegment(tQueItm.mSegment)
            tQueItm.mInProgress = False

    def retransmit(self, pLowSeqNo, pHighSeqNo):
        tRetransList = []
        tNAKSequenceNumbers = None
        with self.mQueue:
            if self.mConnection.isLogFlagSet(DistributorApplicationConfiguration.LOG_RETRANSMISSION_EVENTS):
                if len(self.mQueue) == 0:
                    self.mConnection.log("RETRANSMISSION: RCV Request for resending Segment [" +
                                         str(pLowSeqNo) + ":" + str(pHighSeqNo) + "] Cache is EMPTY!")
                else:
                    self.mConnection.log("RETRANSMISSION: RCV Request for resending Segment [" +
                                         str(pLowSeqNo) + ":" + str(pHighSeqNo) + "] Cache First Segment: " +
                                         str(self.mQueue[0].mSeqNo) + " Last Segment: " +
                                         str(self.mQueue[-1].mSeqNo))
            if len(self.mQueue) == 0:
                tNAKSequenceNumbers = self.getRetransmissionNAKSequenceNumbers(pLowSeqNo, pHighSeqNo)
            else:
                if pLowSeqNo < self.mQueue[0].mSeqNo:
                    tNAKSequenceNumbers = self.getRetransmissionNAKSequenceNumbers(pLowSeqNo, self.mQueue[0].mSeqNo)
                tItr = reversed(self.mQueue)
                for tQueItm in tItr:
                    if tQueItm.mSeqNo < pLowSeqNo:
                        break
                    if tQueItm.mSeqNo >= pLowSeqNo and tQueItm.mSeqNo <= pHighSeqNo:
                        tQueItm.mInProgress = True
                        tRetransList.append(tQueItm)
        if tNAKSequenceNumbers is not None:
            self.sendRetransmissionNAK(tNAKSequenceNumbers)
        if len(tRetransList) > 0 and self.mConfiguration.getRetransmissionServerHoldback() > 0:
            tTask = QueueRetransmissionListTask(self.mConnection.mConnectionId, tRetransList)
            DistributorTimers.getInstance().queue(self.mConfiguration.getRetransmissionServerHoldback(), tTask)
        elif len(tRetransList) > 0 and self.mConfiguration.getRetransmissionServerHoldback() <= 0:
            self.sendRetransmissions(tRetransList)

    class QueueRetransmissionListTask(DistributorTimerTask):
        def __init__(self, pDistributoConnectionId, pRetransList):
            super().__init__(pDistributoConnectionId)
            self.mRetransList = pRetransList

        def execute(self, pConnection):
            if pConnection.mConnectionSender.mRetransmissionCache.mIsDead:
                return
            pConnection.mConnectionSender.mRetransmissionCache.sendRetransmissions(self.mRetransList)
            self.mRetransList = None


