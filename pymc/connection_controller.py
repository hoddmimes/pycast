from __future__ import annotations

from typing import Any

from pymc.aux.distributor_exception import DistributorException
from pymc.connection_configuration import ConnectionConfiguration
from pymc.event_loop import ConnectionEvent
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
        self._mutex: threading.Lock = threading.Lock()
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

    def schedule_async_event(self, connection_id: int, async_event: 'ConnectionEvent', wait: bool = False) -> Any:
        from pymc.connection import Connection
        _conn: Connection = self.get_connection(connection_id)
        if not _conn:
            return None
        if not wait:
            _conn.schedule_async_event(async_event)
            return True
        else:
            return _conn.schedule_async_event_wait(async_event)
