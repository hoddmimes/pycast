import socket
import datetime
import uuid
from collections import deque

class RemoteConnection:
    cSDF = datetime.datetime.now().strftime("%H:%M:%S.%f")

    def __init__(self, pSegment, pController, pConnection):
        self.mRemoteConnectionId = uuid.uuid4()
        self.mConnection = pConnection
        self.mHashCode = hash(pSegment)
        tMsg = NetMsgConfiguration(pSegment)
        tMsg.decode()
        self.mRemoteAppId = pSegment.getHeaderAppId()
        self.mConnectTime = self.cSDF
        self.mRemoteHostAddressString = str(tMsg.getHostAddress())
        self.mRemoteHostInetAddress = tMsg.getHostAddress()
        self.mRemoteSenderId = tMsg.getSenderId()
        self.mRemoteStartTime = tMsg.getSenderStartTime()
        self.mHeartbeatInterval = tMsg.getHeartbeatInterval()
        self.mConfigurationInterval = tMsg.getConfigurationInterval()
        self.mRemoteApplicationName = tMsg.getApplicationName()
        self.mRemoteHostName = tMsg.getHostAddress().getHostName()
        self.mConfiguration = pConnection.mConfiguration
        self.mMca = pConnection.mIpmg
        self.mRemoteConnectionController = pController
        self.mRetransmissionController = pConnection.mRetransmissionController
        self.mRcvSegmentBatch = None
        self.mHbIsActive = True
        self.mCfgIsActive = True
        self.isDead = False
        self.mStartSynchronized = False
        self.mNextExpectedSeqno = 0
        self.mHighiestSeenSeqNo = 0
        self.mCheckHeartbeatTask = CheckHeartbeatTask(mConnection.mConnectionId, mRemoteConnectionId)
        self.mCheckConfigurationTask = CheckConfigurationTask(mConnection.mConnectionId, mRemoteConnectionId)
        tInterval = ((mConfiguration.getHearbeatMaxLost() + 1) * mHeartbeatInterval)
        DistributorTimers.getInstance().queue( tInterval, tInterval, mCheckHeartbeatTask )
        tInterval = ((mConfiguration.getConfigurationMaxLost() + 1) * mConfigurationInterval)
        DistributorTimers.getInstance().queue( tInterval, tInterval, mCheckConfigurationTask )

    def __str__(self):
        return "[ Host: " + self.mRemoteHostAddressString + " Name: " + self.mRemoteHostName + " SndrId: " + self.mRemoteSenderId + " Appl: " + self.mRemoteApplicationName + "\n        StartTime: " + hex(self.mRemoteStartTime) + " ConnTime: " + self.mConnectTime + " HashCode: " + hex(self.mHashCode) + "\n         HbIntvl: " + self.mHeartbeatInterval + " CfgIntvl: " + self.mConfigurationInterval + " LclMca : " + self.mMca + "]"

    def processHeartbeatMsg(self, pSegment):
        tMsg = NetMsgHeartbeat(pSegment)
        tMsg.decode()
        self.mHbIsActive = True
        if (self.mStartSynchronized) and (self.mHighiestSeenSeqNo < tMsg.getSeqNo()):
            self.mRetransmissionController.createRetransmissionRequest(self, self.mHighiestSeenSeqNo + 1, tMsg.getSeqNo())
            self.mHighiestSeenSeqNo = tMsg.getSeqNo()

    def checkMessageSequence(self, tMsg):
        if self.mStartSynchronized:
            tRcvSeqno = tMsg.getSequenceNumber()
            if tRcvSeqno == self.mNextExpectedSeqno:
                return NetMsg.SequenceNumberActions.SYNCH
            elif tRcvSeqno > self.mNextExpectedSeqno:
                return NetMsg.SequenceNumberActions.HIGHER
            else:
                return NetMsg.SequenceNumberActions.LOWER
        else:
            if (tMsg.getHeaderSegmentFlags() & Segment.FLAG_M_SEGMENT_START) != 0:
                self.mStartSynchronized = True
                self.mHighiestSeenSeqNo = tMsg.getSequenceNumber() - 1
                self.mNextExpectedSeqno = self.mHighiestSeenSeqNo + 1
                return NetMsg.SequenceNumberActions.SYNCH
            else:
                return NetMsg.SequenceNumberActions.IGNORE

    def segmentToRcvSegmentBatch(self, pSegment):
        if self.mRcvSegmentBatch == None:
            self.mRcvSegmentBatch = RcvSegmentBatch(pSegment)
        else:
            self.mRcvSegmentBatch.addSegment(pSegment)
        if pSegment.isEndSegment():
            self.mConnection.mConnectionReceiver.processReceiveSegmentBatch(self.mRcvSegmentBatch)
            self.mRcvSegmentBatch = None

    def processPendingReceiverQueue(self):
        while True:
            if len(self.mPendingReceiverQueue) == 0:
                return
            tMsg = NetMsgUpdate(self.mPendingReceiverQueue[0])
            tMsg.decode()
            if tMsg.getSequenceNumber() == self.mNextExpectedSeqno:
                self.mNextExpectedSeqno += 1
                tRcvSegment = self.mPendingReceiverQueue.pop(0)
                if self.mConnection.isLogFlagSet(DistributorApplicationConfiguration.LOG_RETRANSMISSION_EVENTS):
                    self.mConnection.log("RETRANSMISSION: RCV Process message from pending queue Segment [" + tRcvSegment.getSeqno() + "] QueueSize: " + len(self.mPendingReceiverQueue))
                self.segmentToRcvSegmentBatch(tRcvSegment)
            else:
                return

    def processUpdateSegment(pSegment):
        if len(mConnection.mSubscribers) == 0:
            mStartSynchronized = False
            mHighiestSeenSeqNo = 0
            return
    tMsg = NetMsgUpdate(pSegment)
    tMsg.decode()
    tAction = checkMessageSequence(tMsg)
    if pSegment.getHeaderMessageType() == Segment.MSG_TYPE_RETRANSMISSION:
        mRetransmissionController.updateRetransmissions(pSegment)
    if tAction == NetMsg.SequenceNumberActions.SYNCH:
        if pSegment.getHeaderMessageType() == Segment.MSG_TYPE_RETRANSMISSION and mConnection.isLogFlagSet(DistributorApplicationConfiguration.LOG_RETRANSMISSION_EVENTS):
            mConnection.log("RETRANSMISSION: RCV Retransmission Segment [" + pSegment.getSeqno() + "]")
        mNextExpectedSeqno += 1
        if pSegment.getSeqno() > mHighiestSeenSeqNo:
            mHighiestSeenSeqNo = pSegment.getSeqno()
        segmentToRcvSegmentBatch(pSegment)
        if not mPendingReceiverQueue.isEmpty():
            processPendingReceiverQueue()
    elif tAction == NetMsg.SequenceNumberActions.IGNORE:
        return
    elif tAction == NetMsg.SequenceNumberActions.LOWER:
        return
    elif tAction == NetMsg.SequenceNumberActions.HIGHER:
        if pSegment.getSeqno() > (mHighiestSeenSeqNo + 1):
            mRetransmissionController.createRetransmissionRequest(this, mHighiestSeenSeqNo + 1, pSegment.getSeqno() - 1)
        mHighiestSeenSeqNo = pSegment.getSeqno()
        if mConnection.isLogFlagSet(DistributorApplicationConfiguration.LOG_RETRANSMISSION_EVENTS):
            mConnection.log("RETRANSMISSION: RCV Message To Pending Queue Segment [" + pSegment.getSeqno() + "]")
        mRetransmissionController.updateRetransmissions(pSegment)
        segmentToPendingReceiverQueue(pSegment)

class CheckHeartbeatTask(DistributorTimerTask):
    def __init__(self, pDistributorConnectionId, pRemoteConnectionId):
        super().__init__(pDistributorConnectionId)
        self.mRemoteConnectionId = pRemoteConnectionId

    def execute(self, pConnection):
        tRemoteConnection = pConnection.mConnectionReceiver.mRemoteConnectionController.getRemoteConnection(self.mRemoteConnectionId)
        if tRemoteConnection == None:
            self.cancel()
            return
        try:
            if tRemoteConnection.isDead:
                self.cancel()
                return
            if pConnection.mTimeToDie:
                self.cancel()
                return
            if not tRemoteConnection.mHbIsActive:
                if pConnection.isLogFlagSet(DistributorApplicationConfiguration.LOG_RMTDB_EVENTS):
                    pConnection.log("Remote connction disconnected (no heartbeats) \n        " + tRemoteConnection.toString())
                tEvent = DistributorRemoveRemoteConnectionEvent(tRemoteConnection.mRemoteHostInetAddress, tRemoteConnection.mRemoteSenderId, tRemoteConnection.mMca.mInetAddress, tRemoteConnection.mMca.mPort, tRemoteConnection.mRemoteApplicationName, tRemoteConnection.mRemoteAppId)
                ClientDeliveryController.getInstance().queueEvent(pConnection.mConnectionId, tEvent)
                self.cancel()
                mRemoteConnectionController.removeRemoteConnection(RemoteConnection.this)
            else:
                tRemoteConnection.mHbIsActive = False
        except Exception as e:
            e.printStackTrace()

class CheckConfigurationTask(DistributorTimerTask):
    def __init__(self, pDistributorConnectionId, pRemoteConnectionId):
        super().__init__(pDistributorConnectionId)
        self.mRemoteConnectionId = pRemoteConnectionId

    def execute(self, pConnection):
        tRemoteConnection = pConnection.mConnectionReceiver.mRemoteConnectionController.getRemoteConnection(self.mRemoteConnectionId)
        if tRemoteConnection == None:
            self.cancel()
            return
        try:
            if tRemoteConnection.isDead:
                self.cancel()
                return
            if pConnection.mTimeToDie:
                self.cancel()
                return
            if not tRemoteConnection.mCfgIsActive:
                tRemoteConnection.isDead = True
                tRemoteConnection.mRemoteConnectionController.removeRemoteConnection(tRemoteConnection)
                if pConnection.isLogFlagSet(DistributorApplicationConfiguration.LOG_RMTDB_EVENTS):
                    pConnection.log("Remote connction disconnected (no configuration heartbeats) \n        " + tRemoteConnection.toString())
                tEvent = DistributorRemoveRemoteConnectionEvent(tRemoteConnection.mRemoteHostInetAddress, tRemoteConnection.mRemoteSenderId, tRemoteConnection.mMca.mInetAddress, tRemoteConnection.mMca.mPort, tRemoteConnection.mRemoteApplicationName, tRemoteConnection.mRemoteAppId)
                ClientDeliveryController.getInstance().queueEvent(pConnection.mConnectionId, tEvent)
                self.cancel()
            else:
                tRemoteConnection.mCfgIsActive = False
        except Exception as e:
            e.printStackTrace()