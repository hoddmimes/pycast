from __future__ import annotations
import logging
import threading
from abc import ABC, abstractmethod

from aux import Aux
from aux import DistributorException
from aux import ListItr
from aux import LogManager
from aux import BlockingQueue
from distributor_interfaces import AsyncEvent
from distributor_interfaces import DistributorBase
from distributor_interfaces import ConnectionBase
from distributor_interfaces import ConnectionSenderBase
from distributor_interfaces import ConnectionReceiverBase
from msg.pycast_messages import XtaUpdate, NetMsgUpdate
from ipmc import IPMC



########################################################################################################################
#   ConnectionConfiguration
########################################################################################################################

class ConnectionConfiguration():

    def __init__(self, mca:str='224.44.44.44', mca_port:int=4444, eth_device=''):
        self.ttl = 32
        self.mca = mca
        self.mca_port= mca_port
        self.eth_device = eth_device

        self.ipBufferSize = 128000
        self.segment_size = 8192
        self.smallsegment_size = 512

        self.configuration_interval_ms = 15000
        self.configuration_max_lost = 3

        self.heartbeat_interval_ms = 3000
        self.heartbeat_max_lost = 10

        self.max_bandwidth_bytes = 0
        self.retrans_server_holdback_ms = 20
        self.retrans_timeout_ms = 800
        self.retrans_max_retries = 10
        self.retrans_max_cache_bytes = 10000000
        self.retrans_cache_life_time_sec = 60
        self.retrans_cache_clean_interval_sec = 2

        self.flow_rate_calculate_interval_ms = 100

        self.send_holdback_delay_ms = 0
        self.send_holdback_threshold = 100

        self.fake_xta_error_rate = 0
        self.fake_rcv_error_rate = 0

        self.nagging_window_interval_ms = 4000
        self.nagging_check_interval_ms = 60000

        self.statistic_interval_sec = 0

########################################################################################################################
#   ConnectionSender
########################################################################################################################


class ConnectionSender(ConnectionSenderBase):

    def __init__(self, connectionBase: ConnectionBase):
        self.mConnection:ConnectionBase = connectionBase
        self.mCurrentUpdate:NetMsgUpdate = None

    def publishUpdate( self, xtaUpdate:XtaUpdate):
        return self.updateToSegment(xtaUpdate);


    def smallUpdateToSegment(xtaUpdate:XtaUpdate):
        if (!mCurrentUpdate.addUpdate(pXtaUpdate)) {
            queueCurrentUpdate(Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END);
        if (!mCurrentUpdate.addUpdate(pXtaUpdate)) {
        throw new DistributorException("Update did not fit into segment (" + pXtaUpdate.getSize() + " bytes)");
        }
        }
        }

        void largeUpdateToSegments(XtaUpdate pXtaUpdate) {
            int pOffset = 0;
        int pSegmenCount = 0;

        /**
        * If we have updates in the current segment, queue and get a new
                                                                     * segment
                                                                     */
                                                                     queueCurrentUpdate(Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END);

        mCurrentUpdate.addLargeUpdateHeader(pXtaUpdate.mSubjectName, mConnection.mDistributor.getAppId(), pXtaUpdate.mData.length );

        while (pOffset < pXtaUpdate.mData.length) {
        pOffset += mCurrentUpdate.addLargeData(pXtaUpdate.mData, pOffset);
        mCurrentUpdate.mUpdateCount = 1;
        if (pSegmenCount == 0) {
        queueCurrentUpdate(Segment.FLAG_M_SEGMENT_START);
        } else if (pOffset == pXtaUpdate.mData.length) {
        queueCurrentUpdate(Segment.FLAG_M_SEGMENT_END);
        } else {
        queueCurrentUpdate(Segment.FLAG_M_SEGMENT_MORE);
        }
        pSegmenCount++;
        }
        }

########################################################################################################################
#   ConnectionReceiver
########################################################################################################################

class ConnectionReceiver(ConnectionReceiverBase):
    pass



########################################################################################################################
#   Connection
########################################################################################################################

class Connection(ConnectionBase):
    def __init__(self,  distributor:DistributorBase, configuration: ConnectionConfiguration):
        self.mId:int = Aux.getUUID()
        self.mDistributor:DistributorBase = distributor
        self.mConfiguration:ConnectionConfiguration = configuration
        self.mLogger:logging.Logger = LogManager.getLogger('DistributorConnection')
        self.mLastKnownError = None
        self.mState:int  = self.STATE_INIT
        self.mMutex:threading.Rlock = threading.RLock()
        self.mAsyncEventQueue:BlockingQueue = BlockingQueue()
        self.mIpmc = IPMC(configuration.eth_device, configuration.ttl, configuration.ipBufferSize)
        self.mIpmc.open(configuration.mca, configuration.mca_port)
        self.mIpmc.startReader( self.mcaReadComplete(), self.mcaReadException())
        self.mWorkingThread = threading.Thread( target=self.connectionWorker, args=[self], name="connection-working")

    def lock(self):
        self.mMutex.acquire()

    def unlock(self):
        self.mMutex.release()

    def mcaReadComplete(self, data, addr):
        pass

    def queueAyncEvent(self, asyncEvent:AsyncEvent ):
        self.mAsyncEventQueue.add( asyncEvent )

    def mcaReadException(self, exception: Exception):
        self.mLogger.fatal("MCA {} read exception {}".format(self.toString(), str(exception)))

    def toString(self) -> str:
        return "mca: " + self.mConfiguration.mca + " mca_port: " + str(self.mConfiguration.mca_port)

    def publishUpdate(self, xtaUpdate: XtaUpdate):
        self.mConnectionSender.publishUpdate( xtaUpdate )

    def checkStatus(self):
        if self.mState == ConnectionBase.STATE_RUNNING:
            return

        if self.mState == ConnectionBase.CLOSED:
            raise DistributorException("Connection is not in a running state, has been closed.")

        if self.mState == ConnectionBase.ERROR:
            if not self.mLastKnownError:
                raise DistributorException( "Connection in error state, not in a trustworthy state, last error signale:\n   {}".format(self.mLastKnownError))
            else:
                raise DistributorException( "Connection in error state, not in a trustworthy state");


    def workingThread(self, args ):
        while self.mState == ConnectionBase.STATE_RUNNING or self.mState == ConnectionBase.STATE_INIT:
            tAsyncEvent:AsyncEvent = self.mAsyncEventQueue.take()

            self.mMutex.acquire()

            if not self.mState == ConnectionBase.RUNNING:
                self.mMutex.release()
                self.mAsynchEventQueue.clear()
                return;

            # Execute Async Event
            tAsyncEvent.execute()

            if not self.mAsyncEventQueue.isEmpty():
                tEventList:list = self.mAsyncEventQueue.drain(60)
                for tAsyncEvent in tEventList:
                    if self.mState == ConnectionBase.STATE_RUNNING:
                        tAsyncEvent.execute()
            self.mMutex.release()




########################################################################################################################
#   ConnectionController
########################################################################################################################

class ConnectionController(object):
    cLogger:logging.Logger = LogManager.getLogger('ConnectionController')
    cMutexAccess:threading.RLock = threading.RLock()
    cMutexRemove:threading.RLock = threading.RLock()
    cConnections:Aux.LinkedList = Aux.LinkedList()


    @staticmethod
    def getConnection( connectionId:int  ):
        ConnectionController.cMutexAccess.acquire()
        itr = ListItr( ConnectionController.cConnections )
        while itr.has_next():
            tConn:Connection = itr.next();
            if tConn.mId == connectionId:
                ConnectionController.cMutexAccess.release()
                return tConn

        ConnectionController.cMutexAccess.release()
        return None
    @staticmethod
    def createConnection( distributor:DistributorBase, connectionConfiguration:ConnectionConfiguration ) -> Connection:

        ConnectionController.cMutexRemove.acquire()
        ConnectionController.cMutexAccess.acquire()
        itr = ListItr( ConnectionController.cConnections )
        while itr.has_next():
            tConn:Connection = itr.next();
            if tConn.mIpmc.mGroupAddr == connectionConfiguration.mca and tConn.mIpmc.mPort == connectionConfiguration.mca_port:
                ConnectionController.cMutexRemove.release()
                ConnectionController.cMutexAccess.release()
                raise Exception("Connection for multicast group: {} port: {} has already been created".format(tConn.mIpmc.mGroupAddr, connectionConfiguration.mca_port ))
        try:
            tConn = Connection( distributor, connectionConfiguration)
        except Exception as e:
            ConnectionController.cMutexRemove.release()
            ConnectionController.cMutexAccess.release()
            raise e
        ConnectionController.cMutexRemove.release()
        ConnectionController.cMutexAccess.release()
        return tConn


    @staticmethod
    def getAndLockConnection( connectionId: int ) -> Connection:
        ConnectionController.cMutexAccess.acquire()
        tConn:Connection = ConnectionController.getConnection( connectionId )
        if tConn:
            tConn.lock()
        ConnectionController.cMutexAccess.release()
        return tConn

    @staticmethod
    def unlockConnection( connection:Connection):
        connection.unlock()

    @staticmethod
    def removeConnection( connectionId:int ):
        ConnectionController.cMutexRemove.acquire()
        ConnectionController.cMutexAccess.acquire()

        itr:ListItr = ListItr( ConnectionController.cConnections )
        while itr.has_next():
            tConn:Connection = itr.next()
            if tConn.mId == connectionId:
                itr.remove()
                ConnectionController.cMutexRemove.release()
                ConnectionController.cMutexAccess.release()
                return
        ConnectionController.cMutexRemove.release()
        ConnectionController.cMutexAccess.release()



    @staticmethod
    def queueAyncEvent( connectionId:int, asyncEvent: AsyncEvent ) -> bool:
        ConnectionController.cMutexAccess.acquire()
        tConn = ConnectionController.getConnection( connectionId )
        if not tConn:
            ConnectionController.cMutexAccess.release()
            return False
        tConn.queueAsyncEvent( asyncEvent )
        ConnectionController.cMutexAccess.release()
        return True
