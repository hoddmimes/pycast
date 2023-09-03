from __future__ import annotations
from typing import Callable
from abc import ABC, abstractmethod

from pymc.aux.distributor_exception import DistributorException
from pymc.distributor_events import DistributorEvent
from pymc.msg.rcv_update import RcvUpdate

from pymc.subscription import SubscriptionFilter


class SubscriptionFiltersCntx(object):
    def __init__(self, connection_id: int, subscription_filter: SubscriptionFilter):
        self._connection_id: int = connection_id
        self._subscription_filter: SubscriptionFilter = subscription_filter

    @property
    def connection_id(self) -> int:
        return self._connection_id

    @property
    def subscription_filter(self) -> SubscriptionFilter:
        return self._subscription_filter


class EventCallbackCntx(object):

    def __init__(self, connection_id: int, callback: Callable[[DistributorEvent], None]):
        self._connection_id: int = connection_id
        self._callback: Callable[[DistributorEvent], None] = callback

    @property
    def connection_id(self) -> int:
        return self._connection_id

    @property
    def callback(self) -> Callable[[DistributorEvent], None]:
        return self._callback


class ClientEvent(ABC):
    UPDATE = 1
    APPEVENT = 2
    DEDICATED_APPEVENT = 3

    def __init__(self, event_type: int, connection_id: int):
        if event_type < 1 or event_type > 3:
            raise DistributorException('Invalid ClientEventType ({})'.format(type))
        self._event_type = event_type
        self._connection_id = connection_id

    @abstractmethod
    def rcv_update_count(self):
        pass

    @property
    def event_type(self) -> int:
        return self._event_type

    @property
    def connection_id(self) -> int:
        return self._connection_id

    @classmethod
    def cast(cls, obj: object) -> ClientEvent:
        if isinstance(obj, ClientEvent):
            return obj
        else:
            raise Exception("object can no be cast to {}".format(cls.__name__))


class ClientUpdateEvent(ClientEvent):
    def __init__(self, connection_id: int, arg):
        super().__init__(ClientEvent.UPDATE, connection_id)
        if isinstance(arg, list):
            self._rcv_update_list: list[RcvUpdate] = arg
            self._rcv_update: RcvUpdate = None
            self._rcv_update_count: int = len(arg)
        elif isinstance(arg, RcvUpdate):
            self._rcv_update: RcvUpdate = arg
            self._rcv_update_list: list[RcvUpdate] = None
            self._rcv_update_count: int = 1

    def rcv_update_count(self):
        return self._rcv_update_count

    @property
    def rcv_update(self) -> RcvUpdate:
        return self._rcv_update

    @property
    def rcv_update_list(self) -> list[RcvUpdate]:
        return self._rcv_update_list

    @classmethod
    def cast(cls, obj: object) -> ClientUpdateEvent:
        if isinstance(obj, ClientUpdateEvent):
            return obj
        else:
            raise Exception("object can no be cast to {}".format(cls.__name__))


class ClientAppEvent(ClientEvent):
    def __init__(self, connection_id: int, event: DistributorEvent):
        super().__init__(ClientEvent.APPEVENT, connection_id)
        self._event = event

    def rcv_update_count(self):
        return 1

    @property
    def event(self) -> DistributorEvent:
        return self._event

    @classmethod
    def cast(cls, obj: object) -> ClientAppEvent:
        if isinstance(obj, ClientAppEvent):
            return obj
        else:
            raise Exception("object can no be cast to {}".format(cls.__name__))


class ClientDedicatedAppEvent(ClientEvent):
    def __init__(self, connection_id: int, event: DistributorEvent, callback: Callable[[DistributorEvent], None]):
        super().__init__(ClientEvent.DEDICATED_APPEVENT, connection_id)
        self._event: DistributorEvent = event
        self._event_callback_if = callback

    def rcv_update_count(self):
        return 1

    @property
    def event_callback_if(self) -> Callable[[DistributorEvent], None]:
        return self._event_callback_if

    @property
    def event(self) -> DistributorEvent:
        return self._event

    @classmethod
    def cast(cls, obj: object) -> ClientDedicatedAppEvent:
        if isinstance(obj, ClientDedicatedAppEvent):
            return obj
        else:
            raise Exception("object can no be cast to {}".format(cls.__name__))