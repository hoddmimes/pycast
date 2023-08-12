import random

from distributor_interfaces import ConnectionReceiverBase
from logging import Logger
from threading import Thread
from pymc.aux.aux import Aux, AuxThread
from pymc.connection import Connection
from pymc.ipmc import IPMC
from pymc.aux.log_manager import LogManager
from pymc.msg.segment import Segment
from pymc.msg.net_msg import NetMsg


## =====================================================================
## ConnectionReceiver
## ======================================================================

class ConnectionReceiver(ConnectionReceiverBase):
    _cLogger: Logger = None


    def __init__(self, connection:Connection):
        self.mLogger = LogManager.getInstance().getLogger('ConnectionReceiver')
        self.mConnection = connection
        self.mConfiguration = connection.mConfiguration
        self.mRemoteConnectionController = RemoteConnectionController(connection)
        self.mReceiverThreads:list[Thread] = []
        for _i in range(connection.mConfiguration.receiver_thread):
            _thr = Thread( target=self.mcaReader )
            self.mReceiverThreads.append( _thr )

    def randomError(self, promille) -> bool:
        x:int = random.randrange(0,1000)
        if (promille <= x):
            return True
        else:
            return False


    def triggerRemoteConfigurationNotifications(self, pCallback):
        self.mRemoteConnectionController.triggerRemoteConfigurationNotifications(pCallback)

    def checkVersion(self, pSegment):
        tMajorVersion = ((NetMsg.VERSION >> 8) & 0xff)
        tMinorVersion = (NetMsg.VERSION & 0xff)
        tMajorMsgVersion = ((pSegment.getHeaderVersion() >> 8) & 0xff)
        tMinorMsgVersion = (pSegment.getHeaderVersion() & 0xff)
        if (tMajorVersion != tMajorMsgVersion):
            self.logInfo("Received a segment with incompatible version Segment: {}.{} Distributor: {}.{}".
                         format(tMajorMsgVersion, tMinorMsgVersion, tMajorVersion, tMinorVersion)
            return False
        else:
            return True

    def close(self):
        for i in range(len(self.mReceiverThreads)):
            with self.mReceiverThreads[i]:
                self.mReceiverThreads[i].interrupt()

    def isLogFlagSet(self, pLogFlag):
        if (self.mConnection.isLogFlagSet(pLogFlag)):
            return True
        return False

    def processConfigurationMsg(self, pSegment):
        self.mRemoteConnectionController.processConfigurationMessage(pSegment)
        if (self.isLogFlagSet(DistributorApplicationConfiguration.LOG_DATA_PROTOCOL_RCV)):
            tMsg = NetMsgConfiguration(pSegment)
            tMsg.decode()
            cLogger.info("PROTOCOL [RCV] " + tMsg.toString())

    def processHeartbeatMsg(self, pSegment):
        self.mRemoteConnectionController.processHeartbeatMessage(pSegment)
        if (self.isLogFlagSet(DistributorApplicationConfiguration.LOG_DATA_PROTOCOL_RCV)):
            tMsg = NetMsgHeartbeat(pSegment)
            tMsg.decode()
            cLogger.info("PROTOCOL [RCV] " + tMsg.toString())

    def processUpdateMsg(self, pSegment):
        if ((self.mConfiguration.getFakeRcvErrorRate() > 0) and (self.randomError(self.mConfiguration.getFakeRcvErrorRate()))):
            if (self.mConnection.isLogFlagSet(DistributorApplicationConfiguration.LOG_RETRANSMISSION_EVENTS)):
                self.mConnection.log("RETRANSMISSION:  RCV SIMULATED  Error Segment [" + pSegment.getSeqno() + "] dropped")
        else:
            self.mRemoteConnectionController.processUpdateSegment(pSegment)
            if (self.isLogFlagSet(DistributorApplicationConfiguration.LOG_DATA_PROTOCOL_RCV)):
                tMsg = NetMsgUpdate(pSegment)
                tMsg.decode()
                if (pSegment.getHeaderMessageType() == Segment.MSG_TYPE_UPDATE):
                    cLogger.info("PROTOCOL [RCV] <UPDATE>" + tMsg.toString())
                else:
                    cLogger.info("PROTOCOL [RCV] <RETRANSMISSION>" + tMsg.toString())

    def processRetransmissionNAK(self, pSegment):
        self.mConnection.mRetransmissionController.processRetransmissionNAK(pSegment)
        if (self.isLogFlagSet(DistributorApplicationConfiguration.LOG_DATA_PROTOCOL_RCV)):
            tMsg = NetMsgRetransmissionNAK(pSegment)
            tMsg.decode()
            cLogger.info("PROTOCOL [RCV] " + tMsg.toString())

    def processRetransmissionRqst(self, pSegment):
        tMsg = NetMsgRetransmissionRqst(pSegment)
        tMsg.decode()
        self.mConnection.mConnectionSender.retransmit(tMsg)
        if (self.isLogFlagSet(DistributorApplicationConfiguration.LOG_DATA_PROTOCOL_RCV)):
            tMsg.decode()
            cLogger.info("PROTOCOL [RCV] " + tMsg.toString())

    def processReceivedSegment(self, pSegment):
        if (pSegment.getHeaderVersion() != NetMsg.VERSION):
            if (not self.checkVersion(pSegment)):
                return
        if (self.isLogFlagSet(DistributorApplicationConfiguration.LOG_SEGMENTS_EVENTS)):
            tNetMsg = NetMsg(pSegment)
            tNetMsg.decode()
            cLogger.info("RCV Segment: " + tNetMsg.toString())
        if (pSegment.getHeaderMessageType() == Segment.MSG_TYPE_CONFIGURATION):
            self.processConfigurationMsg(pSegment)
        elif (pSegment.getHeaderMessageType() == Segment.MSG_TYPE_HEARTBEAT):
            self.processHeartbeatMsg(pSegment)
        elif (pSegment.getHeaderMessageType() == Segment.MSG_TYPE_RETRANSMISSION):
            self.processUpdateMsg(pSegment)
        elif (pSegment.getHeaderMessageType() == Segment.MSG_TYPE_RETRANSMISSION_NAK):
            self.processRetransmissionNAK(pSegment)
        elif (pSegment.getHeaderMessageType() == Segment.MSG_TYPE_RETRANSMISSION_RQST):
            self.processRetransmissionRqst(pSegment)
        elif (pSegment.getHeaderMessageType() == Segment.MSG_TYPE_UPDATE):
            self.processUpdateMsg(pSegment)

    def processReceiveSegmentBatch(self, pRcvSegmentBatch):
        tUpdates = pRcvSegmentBatch.getUpdates(self.mConnection.mConnectionId)
        if (len(tUpdates) == 1):
            ClientDeliveryController.getInstance().queueUpdate(self.mConnection.mConnectionId, tUpdates[0])
        else:
            tRcvUpdateList = []
            for i in range(len(tUpdates)):
                tRcvUpdateList.append(tUpdates[i])
            ClientDeliveryController.getInstance().queueUpdate(self.mConnection.mConnectionId, tRcvUpdateList)

    def logInfo(self, msg):
        self._cLogger.info( msg )

    def logWarning(self, msg):
        self._cLogger.warning( msg )

    def logError(self, msg):
        self._cLogger.error( msg )

    def logThrowable(self, exception ):
        self._cLogger.exception( exception )



    class ReceiverThread(AuxThread):
        def __init__(self, ipmc:IPMC, connection_id:int, index:int, segment_size:int):
            super().__init__()
            self.mIpmc = ipmc
            self.mIndex = index
            self.mSegmentSize = segment_size
            self.mConnectionId = connection_id

        def run(self):
            tInetSocketAddress = None
            self.setName("DIST_RECEIVER_" + str(self.mIndex) + ":" + str(self.mMca))
            while (True):
                tByteBuffer = bytearray(self.mSegmentSize)
                try:
                    tInetSocketAddress = InetSocketAddress(mMca.receive(tByteBuffer))
                except Exception as e:
                    if (self.mConnection.mTimeToDie):
                        return
                    self.mConnection.log("Failed to receive segment, reason: " + str(e))
                    self.mConnection.logThrowable(e)
                    tEvent = DistributorCommunicationErrorEvent("[RECEIVE]", mMca.mInetAddress, mMca.mPort, str(e))
                    tAsyncEvent = AsyncEventSignalEvent(tEvent)
                    DistributorConnectionController.queueAsyncEvent(self.mDistributorConnectionId, tAsyncEvent)
                if (self.mConnection.mTimeToDie):
                    return
                tRcvSegment = RcvSegment(tByteBuffer)
                tRcvSegment.setFromAddress(tInetSocketAddress.getAddress())
                tRcvSegment.setFromPort(tInetSocketAddress.getPort())
                tRcvSegment.decode()
                tAsyncEvent = AsyncEventReceiveSegment(tRcvSegment)
                DistributorConnectionController.queueAsyncEvent(self.mDistributorConnectionId, tAsyncEvent)

