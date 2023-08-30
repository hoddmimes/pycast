import logging
import threading
from queue import Queue
import uuid

class DistributorConnection(threading.Thread):
    class RunningStateType:
        INIT = 0
        RUNNING = 1
        CLOSED = 2
        ERROR = 3

    def __init__(self, pDistributor, pConfiguration, pApplicationConfiguration, pCmaConnection=False):
        super().__init__()
        self.mLogger = logging.getLogger(self.__class__.__name__)
        self.mMutext = threading.Lock()
        self.mState = self.RunningStateType.INIT
        self.mIsCmaConnection = pCmaConnection
        self.mConnectionId = uuid.uuid4().int
        self.mTimeToDie = False
        self.mDistributor = pDistributor
        self.mConfiguration = pConfiguration
        self.mApplicationConfiguration = pApplicationConfiguration
        self.mAsynchEventQueue = Queue()
        self.mRetransmissionStatistics = RetransmissionStatistics()
        self.mPublishers = []
        self.mSubscribers = []

        self.mTrafficStatisticsTask = TrafficStatisticTimerTask(self.mConnectionId)
        DistributorTimers.getInstance().queue(1000, 1000, self.mTrafficStatisticsTask)

        self.mIpmg = Ipmg(pConfiguration.getMca(), pConfiguration.getMcaNetworkInterface(), pConfiguration.getMcaPort(), pConfiguration.getIpBufferSize(), pConfiguration.getTTL())
        self.mMcaConnectionId = self.mIpmg.getMcaConnectionId()

        self.mConnectionReceiver = ConnectionReceiver(self)

        self.mConnectionSender = ConnectionSender(self)

        self.mRetransmissionController = RetransmissionController(self)
        self.mSubscriptionFilter = DistributorSubscriptionFilter()
        ClientDeliveryController.getInstance().addSubscriptionFilter(self.mConnectionId, self.mSubscriptionFilter)
        if self.mConfiguration.getStatisticsLogInterval() > 0:
            self.mLogStatisticTask = LogStatisticsTimerTask(self.mConnectionId)
            DistributorTimers.getInstance().queue(self.mConfiguration.getStatisticsLogInterval(), self.mConfiguration.getStatisticsLogInterval(), self.mLogStatisticTask)
        else:
            self.mLogStatisticTask = None
        if isLogFlagSet(DistributorApplicationConfiguration.LOG_CONNECTION_EVENTS):
            self.log("Open Connection (" + self.mIpmg.toString() + ") using sender id: " + self.mConnectionSender.mSenderId)
        self.mState = self.RunningStateType.RUNNING
        self.start()

    def pushOutConfiguration(self):
        tMsg = NetMsgConfiguration(XtaSegment(self.mConfiguration.getSmallSegmentSize()))
        tMsg.setHeader(Segment.MSG_TYPE_CONFIGURATION,
                       Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END,
                       self.mConnectionSender.mLocalAddress,
                       self.mConnectionSender.mSenderId,
                       int(self.mConnectionSender.mConnectionStartTime & 0xffffffff),
                       self.mDistributor.getAppId())
        tMsg.set(self.mIpmg.mInetAddress,
                 self.mIpmg.mPort,
                 self.mConnectionSender.mSenderId,
                 self.mConnectionSender.mConnectionStartTime,
                 int(self.mConfiguration.getHearbeatInterval()),
                 int(self.mConfiguration.getConfigurationInterval()),
                 self.mConnectionSender.mLocalAddress,
                 self.mApplicationConfiguration.getApplicationName())
        tMsg.encode()
        self.mConnectionSender.send_segment(XtaSegment(tMsg._segment))
        tMsg = None


def createPublisher(pEventCallback):
    tFloodRegulated = True if mConfiguration.getMaxBandwidth() > 0 else False
    tPublisher = DistributorPublisher(mConnectionId, self.mDistributor.getAppId(), tFloodRegulated, pEventCallback)
    mPublishers.append(tPublisher)
    pushOutConfiguration()
    if pEventCallback is not None:
        ClientDeliveryController.getInstance().addEventListener(mConnectionId, pEventCallback)
        self.mConnectionReceiver.triggerRemoteConfigurationNotifications(pEventCallback)
    return tPublisher

def lock():
    mMutext.lock()

def unlock():
    mMutext.unlock()

def getMcaConnectionId():
    return mMcaConnectionId

def close():
    lock()
    if mTimeToDie:
        return
    ClientDeliveryController.getInstance().removeSubscriptionFilter(mConnectionId, mSubscriptionFilter)
    DistributorConnectionController.removeConnection(mConnectionId)
    mState = RunningStateType.CLOSED
    mTimeToDie = True
    mLogStatisticTask.cancel()
    mTrafficStatisticsTask.cancel()
    if isLogFlagSet(DistributorApplicationConfiguration.LOG_CONNECTION_EVENTS):
        log("Close Connection (" + mIpmg.toString() + ")  using sender id: " + self.mConnectionSender.mSenderId)
    mRetransmissionController.close()
    mRetransmissionController = None
    mConnectionSender.close()
    mConnectionSender = None
    mConnectionReceiver.close()
    mConnectionReceiver = None
    mIpmg.close()
    mIpmg = None
    mSubscriptionFilter.remove(None)
    mSubscriptionFilter = None
    unlock()

def checkStatus():
    if mState == RunningStateType.RUNNING:
        return
    elif mState == RunningStateType.CLOSED:
        raise DistributorException("Connection is not in a running state, has been closed.")
    elif mState == RunningStateType.ERROR:
        if mLastKnownError is not None:
            raise DistributorException("Connection in error state, not in a trustworthy state, last error signale: \n   " + mLastKnownError)
        else:
            raise DistributorException("Connection in error state, not in a trustworthy state")

def getMcAddress():
    return mIpmg.mInetAddress.getHostAddress()

def getMcPort():
    return mIpmg.mPort

def getConnectionId():
    return mConnectionId


def deliveryUpdate(pUpdate, pQueueLength):
    if mTimeToDie:
        return
    mSubscriptionFilter.match(pUpdate.getSubjectName(), pUpdate.getData(), pUpdate.getAppId(), pQueueLength)
    pUpdate = None

def evalTrafficFlow(pClientFlowContext):
    mConnectionSender.evalTrafficFlow(pClientFlowContext)

def removePublisher(pPublisher):
    if mTimeToDie:
        raise DistributorException("Distrbutor Connection (" + mIpmg.toString() + ") has been closed.")
    mPublishers.remove(pPublisher)
    if pPublisher.mEventCallback != None:
        ClientDeliveryController.getInstance().removeEventListener(mConnectionId, pPublisher.mEventCallback)

def removeSubscriber(pSubscriber):
    if mTimeToDie:
        raise DistributorException("Connection (" + mIpmg.toString() + ") has been closed.")
    mSubscribers.remove(pSubscriber)
    if pSubscriber.mEventCallback != None:
        ClientDeliveryController.getInstance().removeEventListener(mConnectionId, pSubscriber.mEventCallback)

def addSubscription(pSubscriber, pSubjectName, pCallbackObject):
    if mTimeToDie:
        raise DistributorException("Connection (" + mIpmg.toString() + ") has been closed.")
    if isLogFlagSet(DistributorApplicationConfiguration.LOG_SUBSCRIPTION_EVENTS):
        log("ADD Subscription: " + pSubjectName + " connection: " + mIpmg.toString())
    return mSubscriptionFilter.queue(pSubjectName, pSubscriber.mUpdateCallback, pCallbackObject)

def removeSubscription(pHandle, pSubjectName):
    if mTimeToDie:
        raise DistributorException("Connection (" + mIpmg.toString() + ") has been closed.")
    if isLogFlagSet(DistributorApplicationConfiguration.LOG_SUBSCRIPTION_EVENTS):
        log("REMOVE Subscription: " + pSubjectName + " connection: " + mIpmg.toString())
    mSubscriptionFilter.remove(pHandle)

def updateOutRetransmissionStatistics(pMca, pDestinationAddress):
    mRetransmissionStatistics.updateOutStatistics(pMca.mInetAddress, pMca.mPort, pDestinationAddress)

def updateInRetransmissionStatistics(pMca, tMsg, pToThisNode):
    mRetransmissionStatistics.updateInStatistics(pMca.mInetAddress, pMca.mPort, tMsg.getHeaderLocalSourceAddress(), pToThisNode)

def queueAsyncEvent(pAsyncEvent):
    mAsynchEventQueue.append(pAsyncEvent)

def run():
    tAsyncEvent = None
    tEventList = []
    setName("AsynchThread: " + mIpmg.toString())
    while mState == RunningStateType.RUNNING or mState == RunningStateType.INIT:
        try:
            tAsyncEvent = mAsynchEventQueue.pop(0)
        except InterruptedException:
            pass
        mMutext.lock()
        try:
            if mState != RunningStateType.RUNNING:
                mAsynchEventQueue.clear()
                return
            if tAsyncEvent != None:
                tAsyncEvent.execute(this)
            if len(mAsynchEventQueue) > 0:
                tEventList.clear()
                tEventList.extend(mAsynchEventQueue[:60])
                mAsynchEventQueue = mAsynchEventQueue[60:]
                for i in range(len(tEventList)):
                    if mState != RunningStateType.RUNNING:
                        mAsynchEventQueue.clear()
                        return
                    tEventList[i].execute(this)
        finally:
            mMutext.unlock()

class LogStatisticsTimerTask(DistributorTimerTask):
    def __init__(self, DistributorConnectionId):
        super(DistributorConnectionId)
        self.mDistributorConnectionId = DistributorConnectionId

    def getLogFileName(self, tConnection):
        tFilename = ""
        tSDF = SimpleDateFormat("-yyyy-MM-dd-HHmmss")
        if tConnection._configuration.getStatisticFilename() == None:
            tFilename = tConnection.mApplicationConfiguration.getApplicationName().replaceAll("[\\/:*?\"<>|]","_") + "-Statistics-" + tConnection.mIpmg.mInetAddress.getHostAddress() + "_" + tConnection.mIpmg.mPort + tSDF.format(new Date()) + ".log"
        else:
            tIndex = tConnection._configuration.getStatisticFilename().lastIndexOf(".")
            if tIndex > 0:
                tFilename = tConnection._configuration.getStatisticFilename().substring(0, tIndex) + "-" + tSDF.format(new Date()) + tConnection.mIpmg.mInetAddress.getHostAddress() + "_" + tConnection.mIpmg.mPort + tSDF.format(new Date()) + tConnection._configuration.getStatisticFilename().substring(tIndex, tConnection._configuration.getStatisticFilename().length())
            else:
                tFilename = tConnection._configuration.getStatisticFilename()
        return tFilename

    def execute(self, tConnection):
        tSB = StringBuilder(512)
        if tConnection.mTimeToDie:
            return
        try:
            tSB.append("Traffic Statistics MCA " + tConnection.mIpmg.toString() + "\n")
            tSB.append("\t XTA Byte Rate          " + tConnection.mTrafficStatisticsTask.mXtaBytes.getValueSec() + "\n")
            tSB.append("\t XTA Segment Rate       " + tConnection.mTrafficStatisticsTask.mXtaMsgs.getValueSec() + "\n")
            tSB.append("\t XTA Update Rate        " + tConnection.mTrafficStatisticsTask.mXtaUpdates.getValueSec() + "\n")
            tSB.append("\t XTA Total Segments     " + tConnection.mTrafficStatisticsTask.getTotalXtaSegments() + "\n")
            tSB.append("\t XTA Total Updates      " + tConnection.mTrafficStatisticsTask.getTotalXtaUpdates() + "\n")
            tSB.append("\t XTA Avg snd time (usec)" + tConnection.mTrafficStatisticsTask.getXtaAvgIOXTimeUsec() + "\n")
            tSB.append("\t RCV Byte Rate          " + tConnection.mTrafficStatisticsTask.mRcvBytes.getValueSec() + "\n")
            tSB.append("\t RCV Segment Rate       " + tConnection.mTrafficStatisticsTask.mRcvMsgs.getValueSec() + "\n")
            tSB.append("\t RCV Update Rate        " + tConnection.mTrafficStatisticsTask.mRcvUpdates.getValueSec() + "\n")
            tSB.append("\t RCV Total Segments     " + tConnection.mTrafficStatisticsTask.getTotalRcvSegments() + "\n")
            tSB.append("\t RCV Total Updates      " + tConnection.mTrafficStatisticsTask.getTotalRcvUpdates() + "\n")
            tSB.append("\t Delivery Queue         " + ClientDeliveryController.getInstance().getQueueLength() + "\n")
            tSB.append("\t Maximum Memory         " + Runtime.getRuntime().maxMemory() + "\n")
            tSB.append("\t Total Memory           " + Runtime.getRuntime().totalMemory() + "\n")
            tSB.append("\t Free Memory            " + Runtime.getRuntime().freeMemory() + "\n")
            tSB.append("\t Used Memory            " + (Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory()) + "\n")
            mLogger.info(tSB.toString())
        except Exception as e:
            System.out.println("Opps failed to log statistics data, reason:  " + e.getMessage())

def flushHoldback(pFlushHoldbackSeqno):
    mConnectionSender.flushHoldback(pFlushHoldbackSeqno)

def publishUpdate(pXtaUpdate):
    return mConnectionSender.publishUpdate(pXtaUpdate)

def logThrowable(e):
    mLogger.error("[Distributor mca: " + mIpmg.toString() + "]", e)

def isLogFlagSet(pLogFlag):
    return mApplicationConfiguration.isLogFlagEnabled(pLogFlag)

def log(pMessage):
    mLogger.info("[mca: " + mIpmg.toString() + "] " + pMessage)