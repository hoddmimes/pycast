from __future__ import annotations
from typing import Callable
from pymc.aux.aux import Aux
from logging import Logger

from pymc.aux.aux_uuid import Aux_UUID
from pymc.aux.distributor_exception import DistributorException
from pymc.aux.log_manager import LogManager
from pymc.connection_controller import ConnectionController
from pymc.distributor_events import DistributorEvent
from pymc.msg.xta_update import XtaUpdate
from pymc.distributor_configuration import DistributorLogFlags
from pymc.traffic_statistics import DistributorPublisherStatisticsIf


class Publisher(object):
    cLogger: Logger = None

    def __init__(self, connection_id: int, app_id: int, is_flood_regulated: bool,
                 distributor_event_callback: Callable[[DistributorEvent], None]):
        self._connection_id = connection_id
        self._app_id = app_id
        self._id = Aux_UUID.getId()
        self._is_flood_regulated = is_flood_regulated
        self._callback: Callable[[DistributorEvent], None] = distributor_event_callback
        if Publisher.cLogger is None:
            self.cLogger = LogManager.get_instance().get_logger('Publisher')

    def publish(self, subject: str, data_bytes: bytearray, data_len: int = None):
        if data_len is None:
            _data = bytes(data_bytes)
        else:
            _data = bytes(data_bytes[:data_len])

        _connection: 'Connection' = ConnectionController.get_instance().get_connection(self._connection_id)

        if not _connection:
            raise DistributorException("Distributor connection is closed or no longer valid")

        with _connection:
            _connection.checkStatus()
            _xta_update = XtaUpdate(subject, _data)
            _xta_time = _connection.publishUpdate(_xta_update)

            if self._is_flood_regulated:
                _wait_time: int = _connection.eval_outgoing_traffic_flow(_xta_update.size)
                if _wait_time > 0:
                    if _connection.is_(DistributorLogFlags.LOG_TRAFFIC_FLOW_EVENTS):
                        self.cLogger.info("outgoing flow regulated, wait: {} ms)  xta_time: {}".format(_wait_time, _xta_time))
                    Aux.sleep_ms(_wait_time)

        return _xta_time

    @property
    def get_id(self) -> int:
        return self._id

    def close(self):
        _connection: 'Connection' = ConnectionController.get_instance().get_connection(self._connection_id)

        if _connection is None:
            raise DistributorException("Distributor connection is closed or no longer valid")
        with _connection:
            _connection.checkStatus()
            _connection.remove_publisher(self)


    def getStatistics(self) -> DistributorPublisherStatisticsIf:
        _connection: 'Connection' = ConnectionController.get_instance().get_connection(self._connection_id)

        if _connection is None:
            raise DistributorException("Distributor connection is closed or no longer valid")

        with _connection:
            _connection.checkStatus()
            _statistics: DistributorPublisherStatisticsIf = _connection.get_traffic_statistics()
            return _statistics
