from __future__ import annotations

from pymc.aux.distributor_exception import DistributorException
from pymc.connection import Connection
from pymc.distributor_events import AsyncEvent
from pymc.distributor_interfaces import DistributorBase
from pymc.connection_configuration import ConnectionConfiguration
import threading


class ConnectionController(object):
    _instance: ConnectionController = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    @staticmethod
    def getInstance() -> ConnectionController:
        if not ConnectionController._instance:
            ConnectionController._instance = ConnectionController()
        return ConnectionController._instance

    def __init__(self):
        self._mutex_access: threading.RLock = threading.RLock()
        self._mutex_Remove: threading.RLock = threading.RLock()
        self._connections: dict[int, Connection] = {}

    def getConnection(self, connection_id: int) -> Connection:
        with self._mutex_access:
            return self._connections.get(connection_id, None)

    def createConnection(self, distributor: DistributorBase,
                         connection_configuration: ConnectionConfiguration) -> Connection:

        with self._mutex_Remove and self._mutex_access:
            for _conn in self._connections.values():
                if _conn.mc_address == connection_configuration.mca and _conn.mc_port == connection_configuration.mca_port:
                    raise DistributorException(
                        "Connection for multicast group: {} port: {} has already been created".format(
                            _conn.mc_address, _conn.mc_port))

            try:
                _conn = Connection(distributor, connection_configuration)
            except Exception as e:
                raise e

            return _conn

    def getAndLockConnection(self, connection_id: int) -> Connection:
        with self._mutex_access:
            _conn: Connection = self.getConnection(connection_id)
            if _conn:
                _conn.lock()
        return _conn

    def unlockConnection(self, connection: Connection):
        connection.unlock()

    def removeConnection(self, connection_id: int):
        with self._mutex_Remove and self._mutex_access:
            self._connections.pop(connection_id)

    def queueAsyncEvent(self, connection_id: int, async_event: AsyncEvent) -> bool:
        with self._mutex_access:
            _conn: Connection = self.getConnection(connection_id)
            if not _conn:
                return False
            _conn.queueAsyncEvent(async_event)
            return True
