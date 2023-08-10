
from pymc.connection import Connection
from pymc.distributor_interfaces import DistributorBase, AsyncEvent
from pymc.connection_configuration import ConnectionConfiguration
import threading



class ConnectionController(object):
    cMutexAccess:threading.RLock = threading.RLock()
    cMutexRemove:threading.RLock = threading.RLock()
    cConnections:dict[int, Connection] = {}


    @staticmethod
    def getConnection( connectionId:int  ) -> Connection:
        with ConnectionController.cMutexAccess:
            return ConnectionController.cConnections.get(connectionId, None )

    @staticmethod
    def createConnection( distributor:DistributorBase, connectionConfiguration:ConnectionConfiguration ) -> Connection:

        with ConnectionController.cMutexRemove and ConnectionController.cMutexAccess:
            for tConn in ConnectionController.cConnections.values():
             if tConn.mIpmc.mGroupAddr == connectionConfiguration.mca and tConn.mIpmc.mPort == connectionConfiguration.mca_port:
                 ConnectionController.cMutexRemove.release()
                 ConnectionController.cMutexAccess.release()
                 raise Exception("Connection for multicast group: {} port: {} has already been created".format(tConn.mIpmc.mGroupAddr, connectionConfiguration.mca_port ))

            try:
                tConn = Connection( distributor, connectionConfiguration)
            except Exception as e:
                raise e

            return tConn


    @staticmethod
    def getAndLockConnection( connectionId: int ) -> Connection:
        with ConnectionController.cMutexAccess:
            tConn:Connection = ConnectionController.getConnection( connectionId )
            if tConn:
                tConn.lock()
        return tConn

    @staticmethod
    def unlockConnection( connection:Connection):
        connection.unlock()

    @staticmethod
    def removeConnection( connectionId:int ):
        with ConnectionController.cMutexRemove and ConnectionController.cMutexAccess:
            ConnectionController.cConnections.pop( connectionId )



    @staticmethod
    def queueAyncEvent( connectionId:int, asyncEvent: AsyncEvent ) -> bool:
        with ConnectionController.cMutexAccess:
            tConn = ConnectionController.getConnection( connectionId )
            if not tConn:
                return False
            tConn.queueAsyncEvent( asyncEvent )
            return True
