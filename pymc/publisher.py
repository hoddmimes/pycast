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
from typing import Callable
from pymc.aux.aux import Aux
from logging import Logger

from pymc.aux.trace import Trace
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

    def publish(self, subject: str, data_bytes: bytes, data_len: int = None):
        if data_len is None:
            _data = bytes(data_bytes)
        else:
            _data = bytes(data_bytes[:data_len])

        trcctx: Trace = Trace(verbose=False)
        _xta_update = XtaUpdate(subject, _data, trcctx )

        _connection: 'Connection' = ConnectionController.get_instance().get_connection(self._connection_id)
        trcctx.add("publish got Connection")
        if not _connection:
            raise DistributorException("Distributor connection is closed or no longer valid")

        with _connection:
            trcctx.add("publish locked Connection")
            _connection.checkStatus()
            _xta_time_usec = _connection.publishUpdate(_xta_update)
            trcctx.add("after publishedUpdate")

            if self._is_flood_regulated:
                _wait_time: int = _connection.eval_outgoing_traffic_flow(_xta_update.size)
                if _wait_time > 0:
                    if _connection.is_(DistributorLogFlags.LOG_TRAFFIC_FLOW_EVENTS):
                        self.cLogger.info("outgoing flow regulated, wait: {} ms)  xta_time: {}".format(_wait_time, _xta_time_usec))
                    Aux.sleep_ms(_wait_time)
            trcctx.add("publish complete")
        trcctx.dump()
        return _xta_time_usec

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
