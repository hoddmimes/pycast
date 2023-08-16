import random

from distributor_interfaces import ConnectionReceiverBase
from logging import Logger
from threading import Thread
from pymc.aux.aux import Aux, AuxThread
from pymc.aux.distributor_exception import DistributorTheadExitException, DistributorException
from pymc.connection import Connection
from pymc.distributor_events import DistributorCommunicationErrorEvent, AsyncEvent
from pymc.ipmc import IPMC
from pymc.msg.segment import Segment
from pymc.msg.rcv_segment import RcvSegment
from pymc.msg.net_msg import NetMsg


## =====================================================================
## ConnectionReceiver
## ======================================================================

class ConnectionReceiver(ConnectionReceiverBase):

    def __init__(self, connection:Connection):
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
        self.mConnection.logInfo( msg )

    def logWarning(self, msg):
        self.mConnection.logWarning( msg )

    def logError(self, msg):
        self.mConnection.logError( msg )

    def logThrowable(self, exception ):
        self.mConnection.logThrowable( exception )



    class ReceiverThread(AuxThread):
        def __init__(self, logger:Logger, ipmc:IPMC, connection_id:int, index:int, segment_size:int):
            super().__init__()
            self.mIpmc = ipmc
            self.mIndex = index
            self.mLogger  = logger
            self.mSegmentSize = segment_size
            self.mConnectionId = connection_id

        def run(self):
            t_data_addr = None
            self.setName("DIST_RECEIVER_" + str(self.mIndex) + ":" + str(self.mMca))
            while (True):
                tByteBuffer = bytearray(self.mSegmentSize)
                try:
                    t_data_addr = self.mIpmc.read()
                    t_data = t_data_addr[0]
                    t_mc_addr = t_data_addr[1][0]
                    t_mc_port = t_data_addr[1][1]
                except Exception as e:
                    if self.mConnection.mTimeToDie:
                        return
                    e = DistributorException("IPMC read failure", e)
                    self.mLogger.exception( e )
                    tEvent = DistributorCommunicationErrorEvent("[RECEIVE]",
                                                                self.mIpmc.mMcAddr,
                                                                self.mIpmc.mMcPort,
                                                                str(e))
                    tAsyncEvent = AsyncEventSignalEvent(tEvent)
                    DistributorConnectionController.queueAsyncEvent(self.mDistributorConnectionId, tAsyncEvent)



                if (self.mConnection.mTimeToDie):
                    return
                tRcvSegment = RcvSegment(t_data)
                tRcvSegment.setFromAddress(Aux.ipAddrStrToInt( t_mc_addr))
                tRcvSegment.setFromPort(t_mc_port)
                tRcvSegment.decode()
                tAsyncEvent:AsyncEventReceiveSegment = AsyncEventReceiveSegment(tRcvSegment)
                DistributorConnectionController.queueAsyncEvent(self.mDistributorConnectionId, tAsyncEvent)

