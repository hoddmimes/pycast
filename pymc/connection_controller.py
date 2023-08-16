from pymc.connection import Connection
from pymc.distributor_interfaces import DistributorBase, AsyncEvent
from pymc.connection_configuration import ConnectionConfiguration
import threading


class ConnectionController(object):
    cMutexAccess: threading.RLock = threading.RLock()
    cMutexRemove: threading.RLock = threading.RLock()
    cConnections: dict[int, Connection] = {}

    @staticmethod
    def getConnection(connection_id: int) -> Connection:
        with ConnectionController.cMutexAccess:
            return ConnectionController.cConnections.get(connection_id, None)

    @staticmethod
    def createConnection(distributor: DistributorBase, connection_configuration: ConnectionConfiguration) -> Connection:

        with ConnectionController.cMutexRemove and ConnectionController.cMutexAccess:
            for t_conn in ConnectionController.cConnections.values():
                if t_conn.mIpmc.mGroupAddr == connection_configuration.mca and t_conn.mIpmc.mPort == connection_configuration.mca_port:
                    ConnectionController.cMutexRemove.release()
                    ConnectionController.cMutexAccess.release()
                    raise Exception("Connection for multicast group: {} port: {} has already been created".format(
                        t_conn.mIpmc.mGroupAddr, connection_configuration.mca_port))

            try:
                t_conn = Connection(distributor, connection_configuration)
            except Exception as e:
                raise e

            return t_conn

    @staticmethod
    def getAndLockConnection(connection_id: int) -> Connection:
        with ConnectionController.cMutexAccess:
            t_conn: Connection = ConnectionController.getConnection(connection_id)
            if t_conn:
                t_conn.lock()
        return t_conn

    @staticmethod
    def unlockConnection(connection: Connection):
        connection.unlock()

    @staticmethod
    def removeConnection(connection_is: int):
        with ConnectionController.cMutexRemove and ConnectionController.cMutexAccess:
            ConnectionController.cConnections.pop(connection_is)

    @staticmethod
    def queueAyncEvent(connection_id: int, async_event: AsyncEvent) -> bool:
        with ConnectionController.cMutexAccess:
            t_conn: Connection = ConnectionController.getConnection(connection_id)
            if not t_conn:
                return False
            t_conn.queueAsyncEvent(async_event)
            return True
