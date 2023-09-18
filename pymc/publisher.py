from __future__ import annotations
from typing import Callable
from logging import Logger

from pymc.aux.aux_uuid import Aux_UUID
from pymc.aux.distributor_exception import DistributorException
from pymc.aux.log_manager import LogManager
from pymc.connection_controller import ConnectionController
from pymc.event_api.events_to_clients import DistributorEvent
from pymc.event_api.event_api_publish import EventApiPublish
from pymc.event_timers.traffic_statistics_task import DistributorPublisherStatisticsIf


class Publisher(object):
    cLogger: Logger = None

    def __init__(self, connection_id: int,
                 app_id: int,
                 is_flood_regulated: bool,
                 distributor_event_callback: Callable[[DistributorEvent], None]):
        self._connection_id = connection_id
        self._app_id = app_id
        self._id = Aux_UUID.getId()
        self._is_flood_regulated = is_flood_regulated
        self._callback: Callable[[DistributorEvent], None] = distributor_event_callback
        if Publisher.cLogger is None:
            Publisher.cLogger = LogManager.get_instance().get_logger('Publisher')

    def publish(self, subject: str, data_bytes: bytes| bytearray, data_len: int = None):
        if data_len is None:
            _data = bytes(data_bytes)
        else:
            _data = bytes(data_bytes[:data_len])

        event = EventApiPublish(subject, _data)
        ConnectionController.get_instance().schedule_async_event( self._connection_id, event)









    @property
    def get_id(self) -> int:
        return self._id

    def close(self):
        _connection: Connection = ConnectionController.get_instance().get_and_lock_connection(self._connection_id)

        if _connection is None:
            raise DistributorException("Distributor connection is closed or no longer valid")
        _connection.check_status()
        _connection.remove_publisher(self)

        ConnectionController.get_instance().unlockConnection(_connection)

    def getStatistics(self) -> DistributorPublisherStatisticsIf:
        _connection: Connection = ConnectionController.get_instance().get_and_lock_connection(self._connection_id)

        if _connection is None:
            raise DistributorException("Distributor connection is closed or no longer valid")
        _connection.check_status()
        _statistics: DistributorPublisherStatisticsIf = _connection.get_traffic_statistics()
        ConnectionController.get_instance().unlockConnection(_connection)
        return _statistics
