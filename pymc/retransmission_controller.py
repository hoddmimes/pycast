import logging
from collections import deque
from threading import Timer

class RetransmissionController:
    def __init__(self, pConnection):
        self.cLogger = logging.getLogger(__name__)
        self.mConnection = pConnection
        self.mNaggingMonitor = self.NaggingMonitorTask(pConnection._connection_id, pConnection._configuration)
        self.mRetransmissionRequestQueue = deque()
        if pConnection._configuration.getNaggingWindowInterval() > 0:
            tInterval = pConnection._configuration.getNaggingWindowInterval()
            Timer(tInterval, self.mNaggingMonitor).start()

    def close(self):
        if not self.mRetransmissionRequestQueue:
            return
        with self.mRetransmissionRequestQueue:
            for item in self.mRetransmissionRequestQueue:
                item.cancel()
            self.mRetransmissionRequestQueue.clear()
        self.mNaggingMonitor.cancel()

    def createRetransmissionRequest(self, pRemoteConnection, pLowSeqNo, pHighSeqNo):
        tRqstTask = self.RetransmissionRequestItem(self.mConnection._connection_id, pRemoteConnection.mRemoteConnectionId, pLowSeqNo, pHighSeqNo)
        self.mRetransmissionRequestQueue.append(tRqstTask)
        Timer(0, self.mConnection._configuration.getRetransmissionTimeout(), tRqstTask).start()

    def updateRetransmissions(self, pSegment):
        if not self.mRetransmissionRequestQueue:
            return
        with self.mRetransmissionRequestQueue:
            for item in self.mRetransmissionRequestQueue:
                item.adjustSeqNo(pSegment.getSeqno())

    def processRetransmissionNAK(self, pSegment):
        if not self.mRetransmissionRequestQueue:
            return
        tMsg = NetMsgRetransmissionNAK(pSegment)
        tMsg.decode()
        tNakSeqNo = tMsg.getNakSeqNo()
        tRqst = None
        with self.mRetransmissionRequestQueue:
            for i in range(len(tNakSeqNo)):
                for item in self.mRetransmissionRequestQueue:
                    tRqst = item
                    if tNakSeqNo[i] >= tRqst.mLowSeqNo and tNakSeqNo[i] <= tRqst.mHighSeqNo:
                        tRemoteConnection = self.mConnection.mConnectionReceiver.mRemoteConnectionController.getConnection(pSegment)
                        tRqst.requestNakSmoked(tRemoteConnection, tNakSeqNo[i])
                        self.mRetransmissionRequestQueue.remove(item)

    class RetransmissionRequestItem:
        def __init__(self, pDistributorConnectionId, pRemoteConnectionId, pLowSeqNo, pHighSeqNo):
            self.mRemoteConnectionId = pRemoteConnectionId
            self.mLowSeqNo = pLowSeqNo
            self.mHighSeqNo = pHighSeqNo
            self.mRetries = 0
            self.mServedList = []
            self.mServedListIndex = 0

        def queueRetransmissionRqstMessage(self, pConnection, pRemoteConnection):
            tRqstMsg = NetMsgRetransmissionRqst(XtaSegment(pConnection._configuration.getSmallSegmentSize()))
            tRqstMsg.setHeader(
                Segment.MSG_TYPE_RETRANSMISSION_RQST,
                Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END,
                pConnection.mConnectionSender.mLocalAddress,
                pConnection.mConnectionSender.mSenderId,
                pConnection.mConnectionSender.mConnectionStartTime & 0xffffffff,
                pConnection.mDistributor.getAppId()
            )
            tRqstMsg.set(
                pConnection.mConnectionSender.mLocalAddress,
                self.mLowSeqNo,
                self.mHighSeqNo,
                pConnection.mConnectionSender.mLocalAddress.getHostName(),
                pConnection.mApplicationConfiguration.getApplicationName(),
                pRemoteConnection.mRemoteSenderId,
                pRemoteConnection.mRemoteStartTime & 0xffffffff
            )
            pConnection.mRetransmissionStatistics.updateOutStatistics(
                pConnection.mIpmg.mInetAddress,
                pConnection.mIpmg.mPort,
                pRemoteConnection.mRemoteHostInetAddress
            )
            tRqstMsg.encode()
            pConnection.mConnectionSender.send_segment(tRqstMsg._segment)

        def requestNakSmoked(self, tRemoteConnection, pNakSeqNo):
            tEvent = DistributorRetransmissionNAKErrorEvent(
                self.mConnection.mIpmg.mInetAddress,
                self.mConnection.mIpmg.mPort
            )
            if self.mConnection.isLogFlagSet(DistributorApplicationConfiguration.LOG_RETRANSMISSION_EVENTS):
                self.mConnection.log(
                    f"RETRANSMISSION: RCV NAK (NakSeqNo: {pNakSeqNo})  Remote Addr: {tRemoteConnection.mRemoteHostAddressString} Remote Sender Id: {tRemoteConnection.mRemoteSenderId} LowSeqNo: {self.mLowSeqNo} HighSeqNo: {tRemoteConnection.mHighiestSeenSeqNo}"
                )
            ClientDeliveryController.get_instance().queue_event(self.mConnection._connection_id, tEvent)

        def adjustSeqNo(self, pSeqNo):
            if pSeqNo > self.mHighSeqNo or pSeqNo < self.mLowSeqNo:
                return
            if pSeqNo in self.mServedList:
                return
            self.mServedList.append(pSeqNo)
            self.mServedListIndex += 1
            if pSeqNo == self.mHighSeqNo:
                self.mHighSeqNo -= 1
            if pSeqNo == self.mLowSeqNo:
                self.mLowSeqNo += 1

        def execute(self, pConnection):
            tResend = False
            tFailed = False
            tRemoteConnection = pConnection.mConnectionReceiver.mRemoteConnectionController.getRemoteConnection(self.mRemoteConnectionId)
            try:
                if pConnection.mTimeToDie:
                    self.cancel()
                    return
                if self.mServedListIndex == len(self.mServedList):
                    self.mRetransmissionRequestQueue.remove(self)
                    self.cancel()
                    return
                elif self.mRetries > pConnection._configuration.getRetransmissionRetries():
                    tFailed = True
                else:
                    tResend = True
                if tResend:
                    if self.mConnection.isLogFlagSet(DistributorApplicationConfiguration.LOG_RETRANSMISSION_EVENTS):
                        self.mConnection.log(
                            f"RETRANSMISSION: XTA REQUEST RETRANSMISSION Segments [{self.mLowSeqNo}:{self.mHighSeqNo}] Retry: [{self.mRetries}] Remote Addr: {tRemoteConnection.mRemoteHostAddressString} Remote Sender Id: {tRemoteConnection.mRemoteSenderId} ({self.mServedListIndex}) served out of ({len(self.mServedList)}) requested"
                        )
                    self.queueRetransmissionRqstMessage(pConnection, tRemoteConnection)
                    self.mRetries += 1
                elif tFailed:
                    self.cancel()
                    with self.mRetransmissionRequestQueue:
                        self.mRetransmissionRequestQueue.remove(self)
                    tEvent = DistributorTooManyRetransmissionRetriesErrorEvent(
                        self.mConnection.mIpmg.mInetAddress,
                        self.mConnection.mIpmg.mPort
                    )
                    if self.mConnection.isLogFlagSet(DistributorApplicationConfiguration.LOG_RETRANSMISSION_EVENTS):
                        self.mConnection.log(
                            f"RETRANSMISSION: RCV TO MANY RETRANSMISSION  Remote Addr: {tRemoteConnection.mRemoteHostAddressString} Remote Sender Id: {tRemoteConnection.mRemoteSenderId} LowSeqNo: {self.mLowSeqNo} HighSeqNo: {self.mHighSeqNo}"
                        )
                    ClientDeliveryController.get_instance().queue_event(self.mConnection._connection_id, tEvent)
            except Exception as e:
                print(e)

    class NaggingMonitorTask:
        def __init__(self, DistributorConnectionId, pConfiguration):
            self.mIntervalCount = 0
            self.mLastIntervalCount = 0
            self.mConsequtiveTicks = 0
            self.mCfgWindowInterval = pConfiguration.getNaggingWindowInterval()
            self.mCfgCheckInterval = pConfiguration.getNaggingCheckInterval()
            self.mCfgMaxRetransmissions = pConfiguration.getNaggingMaxRetransmissions()

        def clear(self):
            self.mIntervalCount = 0
            self.mLastIntervalCount = 0
            self.mConsequtiveTicks = 0

        def execute(self, pConnection):
            try:
                if self.mIntervalCount > self.mLastIntervalCount:
                    self.mConsequtiveTicks += self.mCfgWindowInterval
                    if self.mConsequtiveTicks >= self.mCfgCheckInterval:
                        if self.mCfgMaxRetransmissions == 0 or (self.mCfgMaxRetransmissions > 0 and self.mIntervalCount >= self.mCfgMaxRetransmissions):
                            tEvent = DistributorNaggingErrorEvent(pConnection.mIpmg.mInetAddress, pConnection.mIpmg.mPort)
                            ClientDeliveryController.get_instance().queue_event(pConnection._connection_id, tEvent)
                        else:
                            self.clear()
                else:
                    self.clear()
            except Exception as e:
                self.mConnection.log_throwable(e)
