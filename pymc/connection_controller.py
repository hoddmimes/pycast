'''
Copyright 2023 Hoddmimes Solutions AB

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from __future__ import annotations
from pymc.aux.aux import Aux
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


    @property
    def connections(self) -> int:
        return len(self._connections)

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

    def web_get_all_subscription(self) -> list[list]:
        _conn_subscr_list : list[list] = []
        with self._mutex:
            for _conn in self._connections.values():
                with _conn:
                    _conn_subscr_list.append(_conn.get_web_subscription_subjects(address_data=True))
        return _conn_subscr_list


    def web_get_connection_subscriptions(self, mc_addr_str: str, mc_port_str: str) -> list[str]:
        _conn = self.find_connection( Aux.ip_addr_str_to_int(mc_addr_str), int(mc_port_str))
        return _conn.get_web_subscription_subjects(address_data=False)


    def web_get_subscription_count(self) -> list[str]:
        _active_subscriptions: int = 0
        from pymc.connection import Connection
        with self._mutex:
            for _conn in self._connections.values():
                with _conn:
                    _active_subscriptions += _conn.get_active_subscriptions_count
        _lst = ['active subscriptions', str(_active_subscriptions)]
        return _lst

    def get_web_connection_attributes(self) -> list[list]:
        _conn_list = []
        from pymc.connection import Connection
        with self._mutex:
            for _conn in self._connections.values():
                with _conn:
                    _conn_list.append(_conn.get_web_connection_attributes())
        return _conn_list

    def get_web_remote_connection_attributes(self) -> list[list]:
        _conn_list = []
        from pymc.connection import Connection
        with self._mutex:
            for _conn in self._connections.values():
                with _conn:
                    _rmt_conn_arr = _conn.get_web_remote_connections_attributes()
                    for _rmt_conn_attr_arr in _rmt_conn_arr:
                        _conn_list.append(_rmt_conn_attr_arr)
        return _conn_list

    def find_connection(self, mc_addr: int, mc_port: int) -> 'Connection' | None:
        with self._mutex:
            for _conn in self._connections.values():
                if _conn.mc_address == mc_addr and _conn.mc_port == mc_port:
                    return _conn
        return None

    def get_web_connection_statistics_attributes(self, mc_addr: int, mc_port: int) -> 'TrafficStatisticTimerTask':
        _conn = self.find_connection(mc_addr, mc_port)
        if _conn is None:
            return "Oppps no such connection with mc-address {} and mc-port {}".format(Aux.ip_addr_int_to_str(mc_addr), mc_port)
        else:
            return _conn.get_traffic_statistics()