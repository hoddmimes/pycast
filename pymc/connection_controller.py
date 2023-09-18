from __future__ import annotations

from pymc.aux.distributor_exception import DistributorException
from pymc.connection_configuration import ConnectionConfiguration
import threading


class ConnectionController(object):
    _instance: ConnectionController = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    @staticmethod
    def get_instance() -> ConnectionController:
        if not ConnectionController._instance:
            ConnectionController._instance = ConnectionController()
        return ConnectionController._instance

    def __init__(self):
        self._mutex: threading.RLock = threading.RLock()
        self._connections: dict[int, 'Connection'] = {}


    def get_connection(self, connection_id: int) -> 'Connection':
        with self._mutex:
            return self._connections.get(connection_id, None)

    def create_connection(self, connection_configuration: ConnectionConfiguration) -> 'Connection':
        with self._mutex:
            for _conn in self._connections.values():
                if _conn.mc_address == connection_configuration.mca and _conn.mc_port == connection_configuration.mca_port:
                    raise DistributorException(
                        "Connection for multicast group: {} port: {} has already been created".format(
                            _conn.mc_address, _conn.mc_port))

            try:
                from pymc.connection import Connection
                _conn = Connection(connection_configuration)
                self._connections[_conn.connection_id] = _conn
            except Exception as e:
                raise e

            return _conn



    def remove_connection(self, connection_id: int):
        with self._mutex:
            self._connections.pop(connection_id)

    def queue_async_event(self, connection_id: int, async_event: 'AsyncEvent') -> bool:
        from pymc.connection import Connection
        with self._mutex:
            _conn: Connection = self.get_connection(connection_id)
            if not _conn:
                return False
            _conn.queueAsyncEvent(async_event)
            return True
