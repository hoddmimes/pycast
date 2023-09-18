from __future__ import annotations

from abc import ABC
from typing import Callable
import threading

from pymc.aux.aux_uuid import Aux_UUID
from pymc.aux.distributor_exception import DistributorException
from pymc.connection_controller import ConnectionController
from pymc.distributor_events import DistributorEvent




class SubscriptionHandleContext(object):

    def __init__(self, subject: str, handle: object):
        self.handle: object = handle
        self.subject: str = subject


class Subscriber(object):
    def __init__(self, connection_id: int,
                 event_callback: Callable[[DistributorEvent], None],
                 update_callback: Callable[[str, bytes, object, int, int], None]):
        self._id = Aux_UUID.getId()
        self._connection_id = connection_id
        self._update_callback = update_callback
        self._event_callback = event_callback
        self._mutex: threading.RLock
        self._subscriptions: dict[object, SubscriptionHandleContext] = dict()


    @property
    def get_id(self):
        return self._id

    @property
    def update_callback(self) -> Callable[[str, bytes, object, int, int], None]: # subject, data, callback_parameter, app_id, queue_length
        return self._update_callback

    def add_subscription(self, subject: str, callback_parameter: object):
        _connection = ConnectionController.get_instance().get_connection(self._connection_id)
        if _connection is None:
            raise DistributorException("Distributor connects is closed or no longer valid")

        with _connection:
            _connection.checkStatus();
            _handle: object = _connection.add_subscription(self, subject, callback_parameter)
            return _handle
