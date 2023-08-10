from __future__ import annotations
import logging
import threading
from time import perf_counter
from pymc.aux.blocking_queue import BlockingQueue
from pymc.aux.distributor_exception import DistributorException
from pymc.aux.aux_uuid import Aux_UUID
from pymc.aux.log_manager import LogManager

from pymc.distributor_interfaces import AsyncEvent
from pymc.distributor_interfaces import DistributorBase
from pymc.distributor_interfaces import ConnectionBase, PublisherBase, SubscriberBase

from pymc.connection_configuration import ConnectionConfiguration
from pymc.msg.net_msg_update import NetMsgUpdate
from pymc.msg.segment import Segment
from pymc.msg.xta_update import XtaUpdate
from pymc.ipmc import IPMC


class Connection(ConnectionBase):
    def __init__(self,  distributor:DistributorBase, configuration: ConnectionConfiguration):
        self.mConnectionId:int = Aux_UUID.getId()
        self.mTimeToDie:bool = False
        self.mPublishers:[PublisherBase] = []
        self.mSubscribers:[SubscriberBase] = []
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

    def getMcPort(self) ->int:
        self.mIpmc.mPort

    def getMcAddress(self) ->int:
        self.mIpmc.mGroupAddr

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

    def getConnectionId(self) -> int:
        return self.mConnectionId
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

    def send(self, segment: Segment ) ->int:
        _start_time = perf_counter()
        self.mIpmc.send(segment.getEncoder().getBytes())
        return int((perf_counter()  - _start_time) * 1000000) # return usec


    def getConfiguration(self):
        return self.mConfiguration

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



