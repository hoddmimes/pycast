import logging
import socket
from java.util import ArrayList, Vector
from java.net import InetAddress, UnknownHostException

class DistributorManagementController(DistributorEventCallbackIf, DistributorUpdateCallbackIf):
    cLogger = logging.getLogger("DistributorManagementController")
    cConsoleSubjectControlTopic = "/DistCtlMsg001"

    def __init__(self, pDistributor, pApplicationConfiguration):
        self.mDistributor = pDistributor
        self.mApplicationConfiguration = pApplicationConfiguration
        tConfiguration = DistributorConnectionConfiguration(
            self.mApplicationConfiguration.getCMA(),
            self.mApplicationConfiguration.getCMAPort()
        )
        tConfiguration.setMcaNetworkInterface(self.mApplicationConfiguration.getCMAInterface())
        tConfiguration.setCmaConnection(True)
        self.mConnection = pDistributor.create_connection(tConfiguration)
        self.mPublisher = pDistributor.create_publisher(self.mConnection, self)
        self.mSubscriber = pDistributor.create_subscriber(self.mConnection, None, self)
        self.mSubscriber.addSubscription(self.cConsoleSubjectControlTopic, None)
        self.mLocalHostName = "localhost"
        try:
            self.mLocalHostName = InetAddress.getLocalHost().getHostName()
        except UnknownHostException as e:
            e.printStackTrace()

    def distributorEventCallback(self, pDistributorEvent):
        pass

    def sendResponse(self, pNetMsg):
        tEncoder = MessageBinEncoder()
        try:
            pNetMsg.setIsRequestMessage(False)
            pNetMsg.setTimestamp(System.currentTimeMillis())
            pNetMsg.encode(tEncoder)
            self.mPublisher.publish(self.cConsoleSubjectControlTopic, tEncoder.getBytes())
        except Exception as e:
            self.cLogger.error(e)

    def getLocalAddresses(self, pDistributorConnections):
        tLocalHostAddresses = ArrayList()
        tLocalHostAddressString = None
        for i in range(len(pDistributorConnections)):
            tConn = pDistributorConnections.get(i)
            tLocalHostAddressString = tConn.mConnectionSender.mLocalAddress.toString()[1:]
            tFound = False
            for j in range(len(tLocalHostAddresses)):
                if tLocalHostAddresses.get(j).equals(tLocalHostAddressString):
                    tFound = True
                    break
            if not tFound:
                tLocalHostAddresses.queue(tLocalHostAddressString)
        sb = StringBuilder()
        for i in range(len(tLocalHostAddresses)):
            sb.append(tLocalHostAddresses.get(i) + ", ")
        tStr = sb.toString()
        return tStr.substring(0, (tStr.length() - 2))

    def serveDistExploreDomainRqst(self, pNetMsg):
        tConnectedConnections = DistributorConnectionController.getDistributorConnection()
        tResponse = DistExploreDomainRsp()
        tResponse.setDistributor(DistDomainDistributorEntry())
        tResponse.getDistributor().setApplicationId(self.mDistributor.getAppId())
        tResponse.getDistributor().setApplicationName(self.mApplicationConfiguration.getApplicationName())
        tResponse.getDistributor().setDistributorId(self.mDistributor.getDistributorId())
        tResponse.getDistributor().setHostname(self.mLocalHostName)
        tResponse.getDistributor().setStartTime(self.mDistributor.getStartTime())
        tResponse.getDistributor().setHostaddress(self.getLocalAddresses(tConnectedConnections))
        if tConnectedConnections.size() == 0:
            tResponse.getDistributor().setConnections(DistDomainConnectionEntry[0])
        else:
            tConnections = Vector()
            for i in range(len(tConnectedConnections)):
                tEntry = DistDomainConnectionEntry()
                tConnection = tConnectedConnections.get(i)
                tEntry.setConnectionId(tConnection._connection_id)
                tEntry.setMcaAddress(tConnection.mIpmg.mInetAddress.getHostAddress().toString())
                tEntry.setMcaPort(tConnection.mIpmg.mPort)
                tEntry.setSubscriptions(tConnection.mSubscriptionFilter.getActiveSubscriptions())
                tEntry.setInRetransmissions(tConnection.mRetransmissionStatistics.total_in)
                tEntry.setOutRetransmissions(tConnection.mRetransmissionStatistics.total_out)
                tConnections.queue(tEntry)
            tResponse.getDistributor().setConnections(tConnections)
        tNetRsp = DistNetMsg()
        tNetRsp.setMessage(MessageWrapper(tResponse))
        tNetRsp.setRequestId(pNetMsg.getRequestId())
        self.sendResponse(tNetRsp)

    def serveDistExploreDistributorRqst(self, pNetMsg):
        tRequest = pNetMsg.getMessage().getWrappedMessage()
        if tRequest.getDistributorId() != self.mDistributor.getDistributorId():
            return
        tConnectedConnections = DistributorConnectionController.getDistributorConnection()
        tResponse = DistExploreDistributorRsp()
        tResponse.setDistributor(DistributorEntry())
        tResponse.getDistributor().setApplicationName(self.mApplicationConfiguration.getApplicationName())
        tResponse.getDistributor().setApplicationId(self.mDistributor.getAppId())
        tResponse.getDistributor().setConnections(tConnectedConnections.size())
        tResponse.getDistributor().setDistributorId(self.mDistributor.getDistributorId())
        tResponse.getDistributor().setHostaddress(self.getLocalAddresses(tConnectedConnections))
        tResponse.getDistributor().setHostname(self.mLocalHostName)
        tResponse.getDistributor().setMemFree(Runtime.getRuntime().freeMemory())
        tResponse.getDistributor().setMemMax(Runtime.getRuntime().maxMemory())
        tResponse.getDistributor().setMemUsed(Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory())
        tResponse.getDistributor().setStartTime(self.mDistributor.getStartTime())
        for i in range(len(tConnectedConnections)):
            tConnection = tConnectedConnections.get(i)
            tResponse.getDistributor().setInRetransmissions(tResponse.getDistributor().getInRetransmissions() + tConnection.mRetransmissionStatistics.total_in)
            tResponse.getDistributor().setOutRetransmissions(tResponse.getDistributor().getOutRetransmissions() + tConnection.mRetransmissionStatistics.total_out)
            tResponse.getDistributor().setSubscriptions(tConnection.mSubscriptionFilter.getActiveSubscriptions())
        tNetRsp = DistNetMsg()
        tNetRsp.setMessage(MessageWrapper(tResponse))
        tNetRsp.setRequestId(pNetMsg.getRequestId())
        self.sendResponse(tNetRsp)

def serveDistExploreConnectionRqst(pNetMsg):
    tRequest = pNetMsg.getMessage().getWrappedMessage()
    tResponse = None
    tConnection = None
    tFound = False
    if tRequest.getDistributorId() != mDistributor.getDistributorId():
        return
    tConnectedConnections = DistributorConnectionController.getDistributorConnection()
    for i in range(len(tConnectedConnections)):
        tConnection = tConnectedConnections[i]
        if tConnection._connection_id == tRequest.getConnectionId():
            tFound = True
            break
    if not tFound:
        return
    tResponse = DistExploreConnectionRsp()
    tResponse.setConnection(ConnectionEntry())
    tResponse.get_connection().setConnectionId(tConnection.getConnectionId())
    tResponse.get_connection().setMcaAddress(tConnection.mIpmg.mInetAddress.getHostAddress())
    tResponse.get_connection().setMcaPort(tConnection.mIpmg.mPort)
    tResponse.get_connection().setOutRetransmissions(tConnection.mRetransmissionStatistics.total_out)
    tResponse.get_connection().setInRetransmissions(tConnection.mRetransmissionStatistics.total_in)
    tResponse.get_connection().setDeliverUpdateQueue(ClientDeliveryController.get_instance().get_queue_size())
    tResponse.get_connection().setPublishers(tConnection.mPublishers.size())
    tResponse.get_connection().setSubscribers(tConnection.mSubscribers.size())
    tResponse.get_connection().setRcvTotalBytes(tConnection.mTrafficStatisticsTask.getTotalRcvBytes())
    tResponse.get_connection().setRcvTotalSegments(tConnection.mTrafficStatisticsTask.getTotalRcvSegments())
    tResponse.get_connection().setRcvTotalUpdates(tConnection.mTrafficStatisticsTask.getTotalRcvUpdates())
    tResponse.get_connection().setRcvBytes(tConnection.mTrafficStatisticsTask.getRcvBytesInfo())
    tResponse.get_connection().setRcvBytes1min(tConnection.mTrafficStatisticsTask.getRcvBytes1MinInfo())
    tResponse.get_connection().setRcvBytes5min(tConnection.mTrafficStatisticsTask.getRcvBytes5MinInfo())
    tResponse.get_connection().setRcvSegments(tConnection.mTrafficStatisticsTask.getRcvMsgsInfo())
    tResponse.get_connection().setRcvSegments1min(tConnection.mTrafficStatisticsTask.getRcvMsgs1MinInfo())
    tResponse.get_connection().setRcvSegments5min(tConnection.mTrafficStatisticsTask.getRcvMsgs5MinInfo())
    tResponse.get_connection().setRcvUpdates(tConnection.mTrafficStatisticsTask.getRcvUpdatesInfo())
    tResponse.get_connection().setRcvUpdates1min(tConnection.mTrafficStatisticsTask.getRcvUpdates1MinInfo())
    tResponse.get_connection().setRcvUpdates5min(tConnection.mTrafficStatisticsTask.getRcvUpdates5MinInfo())
    tResponse.get_connection().setXtaTotalBytes(tConnection.mTrafficStatisticsTask.getTotalXtaBytes())
    tResponse.get_connection().setXtaTotalSegments(tConnection.mTrafficStatisticsTask.getTotalXtaSegments())
    tResponse.get_connection().setXtaTotalUpdates(tConnection.mTrafficStatisticsTask.getTotalXtaUpdates())
    tResponse.get_connection().setXtaBytes(tConnection.mTrafficStatisticsTask.getXtaBytesInfo())
    tResponse.get_connection().setXtaBytes1min(tConnection.mTrafficStatisticsTask.getXtaBytes1MinInfo())
    tResponse.get_connection().setXtaBytes5min(tConnection.mTrafficStatisticsTask.getXtaBytes5MinInfo())
    tResponse.get_connection().setXtaSegments(tConnection.mTrafficStatisticsTask.getXtaMsgsInfo())
    tResponse.get_connection().setXtaSegments1min(tConnection.mTrafficStatisticsTask.getXtaMsgs1MinInfo())
    tResponse.get_connection().setXtaSegments5min(tConnection.mTrafficStatisticsTask.getXtaMsgs5MinInfo())
    tResponse.get_connection().setXtaUpdates(tConnection.mTrafficStatisticsTask.getXtaUpdatesInfo())
    tResponse.get_connection().setXtaUpdates1min(tConnection.mTrafficStatisticsTask.getXtaUpdates1MinInfo())
    tResponse.get_connection().setXtaUpdates5min(tConnection.mTrafficStatisticsTask.getXtaUpdates5MinInfo())
    tResponse.get_connection().setSubscriptions(tConnection.mSubscriptionFilter.getActiveSubscriptions())
    tNetRsp = DistNetMsg()
    tNetRsp.setMessage(MessageWrapper(tResponse))
    tNetRsp.setRequestId(pNetMsg.getRequestId())
    sendResponse(tNetRsp)

def serveDistExploreRetransmissionsRqst(pNetMsg):
    tRequest = pNetMsg.getMessage().getWrappedMessage()
    tConnection = None
    tFound = False
    if tRequest.getDistributorId() != mDistributor.getDistributorId():
        return
    tConnectedConnections = DistributorConnectionController.getDistributorConnection()
    for i in range(len(tConnectedConnections)):
        tConnection = tConnectedConnections[i]
        if tConnection._connection_id == tRequest.getConnectionId():
            tFound = True
            break
    if not tFound:
        return
    tNetRsp = DistNetMsg()
    tResponse = tConnection.mRetransmissionStatistics.getRetransmissonsInfo()
    tResponse.setMcaAddress(tConnection.mIpmg.mInetAddress.getHostAddress())
    tResponse.setMcaPort(tConnection.mIpmg.mPort)
    tNetRsp.setMessage(MessageWrapper(tResponse))
    tNetRsp.setRequestId(pNetMsg.getRequestId())
    sendResponse(tNetRsp)

def serveDistTriggerConfigurationRqst(pNetMsg):
    tConnectedConnections = DistributorConnectionController.getDistributorConnection()
    for tConn in tConnectedConnections:
        tConn.push_out_configuration()

def serveDistExploreSubscriptionsRqst(pNetMsg):
    tRequest = pNetMsg.getMessage().getWrappedMessage()
    tConnection = None
    tFound = False
    if tRequest.getDistributorId() != mDistributor.getDistributorId():
        return
    tConnectedConnections = DistributorConnectionController.getDistributorConnection()
    for i in range(len(tConnectedConnections)):
        tConnection = tConnectedConnections[i]
        if tConnection._connection_id == tRequest.getConnectionId():
            tFound = True
            break
    if not tFound:
        return
    tResponse = DistExploreSubscriptionsRsp()
    tResponse.setMcaAddress(tConnection.mIpmg.mInetAddress.getHostAddress())
    tResponse.setMcaPort(tConnection.mIpmg.mPort)
    tResponse.setSubscriptions(tConnection.mSubscriptionFilter.getActiveSubscriptionsStrings())
    tNetRsp = DistNetMsg()
    tNetRsp.setMessage(MessageWrapper(tResponse))
    tNetRsp.setRequestId(pNetMsg.getRequestId())
    sendResponse(tNetRsp)

def distributorUpdate(pSubjectName, pData, pCallbackParameter, pAppId, pDeliveryQueueLength):
    tDecoder = MessageBinDecoder(pData)
    tNetMsg = DistNetMsg()
    tNetMsg.decode(tDecoder)
    tMessage = tNetMsg.getMessage().getWrappedMessage()
    if tMessage == None:
        return
    if isinstance(tMessage, DistExploreDomainRqst):
        serveDistExploreDomainRqst(tNetMsg)
    if isinstance(tMessage, DistTriggerCofigurationRqst):
        serveDistTriggerConfigurationRqst(tNetMsg)
    if isinstance(tMessage, DistExploreDistributorRqst):
        serveDistExploreDistributorRqst(tNetMsg)
    if isinstance(tMessage, DistExploreConnectionRqst):
        serveDistExploreConnectionRqst(tNetMsg)
    if isinstance(tMessage, DistExploreRetransmissionsRqst):
        serveDistExploreRetransmissionsRqst(tNetMsg)
    if isinstance(tMessage, DistExploreSubscriptionsRqst):
        serveDistExploreSubscriptionsRqst(tNetMsg)