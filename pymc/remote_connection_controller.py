from __future__ import annotations

import threading
from typing import Callable
from pymc.distributor_configuration import DistributorLogFlags
from pymc.distributor_events import DistributorNewRemoteConnectionEvent, DistributorEvent
from pymc.client_controller import ClientDeliveryController
from pymc.msg.segment import Segment
from pymc.remote_connection import RemoteConnection

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



class RemoteConnectionController(object):
    def __init__(self, connection):
        self._remote_connections: dict[int, RemoteConnection] = {}
        self._connection = connection


    def close(self):
        for _rmt_conn in self._remote_connections.values():
            _rmt_conn.cancel()
        self._remote_connections.clear()

    def trigger_remote_configuration_notifications(self, callback: Callable[['DistributorEvent'], None] ):
        for _rmt_conn in self._remote_connections.values():
            tEvent = DistributorNewRemoteConnectionEvent(
                _rmt_conn.remote_host_address,
                _rmt_conn.mc_address,
                _rmt_conn.mc_port,
                _rmt_conn.remote_application_name,
                _rmt_conn.remote_application_id,
                _rmt_conn.remote_sender_id,
                _rmt_conn.remote_start_time
            )
            ClientDeliveryController.get_instance().queue_event_dedicated(self._connection.connection_id, tEvent, callback)

    def get_remote_connection(self, segment: Segment) -> RemoteConnection | None:
        return self._remote_connections.get(segment.__hash__())

    def get_remote_connection_by_id(self, remote_connection_id: int) -> RemoteConnection | None:
        for _rmt_conn in self._remote_connections.values():
            if _rmt_conn._remote_connection_id == remote_connection_id:
                return _rmt_conn
        return None

    def get_remote_connections(self) -> list[RemoteConnection]:
        _connetions = []
        for _rmt_conn in self._remote_connections.values():
            _connetions.append(_rmt_conn)
        return _connetions

    def process_configuration_message(self, segment: Segment):
        _remote_connection = self._remote_connections.get(segment.__hash__())
        if _remote_connection is None:
            _remote_connection = RemoteConnection(segment, self, self._connection)
            self._remote_connections[segment.__hash__()] = _remote_connection
            if self._connection.is_logging_enabled(DistributorLogFlags.LOG_RMTDB_EVENTS):
                self._connection.log_info("Remote Connection [CREATED] ({})\n    {}"
                                          .format(hex(segment.__hash__()), _remote_connection))
            _event = DistributorNewRemoteConnectionEvent(
                _remote_connection.remote_host_address,
                _remote_connection.mc_address,
                _remote_connection.mc_port,
                _remote_connection.remote_application_name,
                _remote_connection.remote_application_id,
                _remote_connection.remote_sender_id,
                _remote_connection.remote_start_time)
            ClientDeliveryController.get_instance().queue_event(self._connection.connection_id, _event)
        _remote_connection.is_configuration_active = True
        return _remote_connection

    def get_connection(self, segment: Segment):
        _remote_connection = self._remote_connections.get(segment.__hash__())
        if _remote_connection is not None:
            _remote_connection.is_heartbeat_active = True
        return _remote_connection

    def remove_remote_connection(self, remote_connection: RemoteConnection):
        _key_to_remove: int = None
        for _k,_v in self._remote_connections.items():
            if _v == remote_connection:
                _key_to_remove = _k
                break

        if _key_to_remove:
            self._remote_connections.pop(_key_to_remove, None)

    def process_heartbeat_message(self, segment: Segment):
        _remote_connection = self._remote_connections.get(segment.__hash__())
        if _remote_connection is not None:
            _remote_connection.process_heartbeat_message(segment)

    def process_update_segment(self, segment: Segment):
        _remote_connection = self._remote_connections.get(segment.__hash__())
        if _remote_connection is not None:
            _remote_connection.is_heartbeat_active = True
            _remote_connection.process_update_segment(segment)


class SegmentBatch:
    def __init__(self, first_rcv_segment_in_batch):
        self.mList = [first_rcv_segment_in_batch]

    def add_segment(self, segment: Segment):
        self.mList.append(segment)
