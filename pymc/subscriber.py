from __future__ import annotations

from typing import Callable
import threading

from pymc.aux.aux_uuid import Aux_UUID
from pymc.aux.distributor_exception import DistributorException
from pymc.connection_controller import ConnectionController
from pymc.event_api.event_api_subscribe import EventApiSubscribe
from pymc.event_api.events_to_clients import DistributorEvent


class SubscriptionHandleContext(object):

    def __init__(self, subject: str, handle: object):
        self.handle: object = handle
        self.subject: str = subject


class Subscriber(object):
    def __init__(self, connection_id: int,
                 event_callback: Callable[[DistributorEvent], None],
                 update_callback: Callable[[str, bytes, object, int, int], None]):
        self._id: int = Aux_UUID.getId()
        self._connection_id: int = connection_id
        self._update_callback = update_callback
        self._event_callback = event_callback
        self._subscriptions: dict[object, SubscriptionHandleContext] = dict()


    @property
    def get_id(self):
        return self._id

    @property
    def update_callback(self) -> Callable[[str, bytes, object, int, int], None]: # subject, data, callback_parameter, app_id, queue_length
        return self._update_callback

    def add_subscription(self, subject: str, callback_parameter: object) -> object:

        event: EventApiSubscribe = EventApiSubscribe(subscriber_id=self.get_id,
                                                     subject=subject,
                                                     callback_parameter=callback_parameter)

        return ConnectionController.get_instance().schedule_async_event( self._connection_id, event, wait=True)


