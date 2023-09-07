from __future__ import annotations

import threading
from typing import Callable
from pymc.distributor_interfaces import ConnectionBase
from pymc.distributor_configuration import DistributorLogFlags
from pymc.distributor_events import DistributorNewRemoteConnectionEvent, DistributorEvent
from pymc.client_controller import ClientDeliveryController
from pymc.msg.segment import Segment
from pymc.remote_connection import RemoteConnection


class RemoteConnectionController(object):
    def __init__(self, connection):
        self._remote_connections: dict[int, RemoteConnection] = {}
        self._connection = connection
        self._mutex: threading.Lock = threading.Lock()

    def close(self):
        with self._mutex:
            for _rmt_conn in self._remote_connections.values():
                _rmt_conn.cancel()
            self._remote_connections.clear()

    def triggerRemoteConfigurationNotifications(self):
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
            ClientDeliveryController.get_instance().queue_event(self._connection.connection_id(), tEvent)

    def getRemoteConnection(self, segment: Segment) -> RemoteConnection | None:
        with self._mutex:
            return self._remote_connections.get(segment.__hash__())

    def processConfigurationMessage(self, segment: Segment):
        with self._mutex:
            _remote_connection = self._remote_connections.get(segment.__hash__())
            if _remote_connection is None:
                _remote_connection = RemoteConnection(segment, self, self._connection)
                self._remote_connections[segment.__hash__()] = _remote_connection
                if self._connection.is_logging_enable(DistributorLogFlags.LOG_RMTDB_EVENTS):
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
                ClientDeliveryController.get_instance().queue_event(self._connection.connection_id(), _event)
            _remote_connection.is_configuration_active = True
            return _remote_connection

    def getConnection(self, segment: Segment):
        with self._mutex:
            _remote_connection = self._remote_connections.get(segment.__hash__())
            if _remote_connection is not None:
                _remote_connection.is_heartbeat_active = True
            return _remote_connection

    def removeRemoteConnection(self, remote_connection: RemoteConnection):
        with self._mutex:
            _key_to_remove: int = None
            for _k,_v in self._remote_connections.items():
                if _v == remote_connection:
                    _key_to_remove = _k
                    break

            if _key_to_remove:
                self._remote_connections.pop(_key_to_remove, None)

    def processHeartbeatMessage(self, segment: Segment):
        with self._remote_connections:
            _remote_connection = self._remote_connections.get(segment.__hash__())
        if _remote_connection is not None:
            _remote_connection.process_heartbeat_message(segment)

    def processUpdateSegment(self, segment: Segment):
        _remote_connection = self._remote_connections.get(segment.__hash__())
        if _remote_connection is not None:
            _remote_connection.is_heartbeat_active = True
            _remote_connection.processUpdateSegment(segment)


class SegmentBatch:
    def __init__(self, first_rcv_segment_in_batch):
        self.mList = [first_rcv_segment_in_batch]

    def addSegment(self, segment: Segment):
        self.mList.append(segment)
