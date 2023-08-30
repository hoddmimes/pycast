from __future__ import annotations
from typing import Callable
from abc import ABC, abstractmethod
import threading
from pymc.subscription import SubscriptionFilter
from pymc.distributor_events import DistributorEvent
from pymc.msg.rcv_update import RcvUpdate
from pymc.aux.aux import Aux
from pymc.aux.blocking_queue import BlockingQueue
from pymc.msg.generated.NetMessage import QueueSizeItem
from pymc.aux.distributor_exception import DistributorException


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


class ClientDeliveryController(object):
    _cInstance: ClientDeliveryController = None

    @staticmethod
    def getInstance() -> ClientDeliveryController:
        if not ClientDeliveryController._cInstance:
            ClientDeliveryController._cInstance = ClientDeliveryController()
        return ClientDeliveryController._cInstance

    def __init__(self):
        self._lock = threading.Lock()
        self._subscription_filters_list: list[SubscriptionFiltersCntx] = []
        self._event_callback_listeners: list[EventCallbackCntx] = []
        self._queue_length: int = 0
        self._peak_length: int = 0
        self._peak_time: int = 0
        self._queue: BlockingQueue = BlockingQueue()
        self._thread = threading.Thread(target=self.run_process_event, name="process-client-events")
        self._thread.start()

    def addSubscriptionFilter(self, connection_id: int, subscription_filter: SubscriptionFilter):
        with self._lock:
            _cntx = SubscriptionFiltersCntx(connection_id, subscription_filter)
            self._subscription_filters_list.append(_cntx)

    def removeSubscriptionFilter(self, connection_id: int, subscription_filter: SubscriptionFilter):
        with self._lock:
            for _sfc in self._subscription_filters_list:
                if _sfc.connection_id == connection_id and subscription_filter == _sfc.subscription_filter:
                    self._subscription_filters_list.remove(_sfc)

    def addEventListner(self, connection_id: int, callback: Callable[[DistributorEvent], None]):
        with self._lock:
            self._event_callback_listeners.append(EventCallbackCntx(connection_id, callback))

    def removeEventListner(self, connection_id: int, callback: Callable[[DistributorEvent], None]):
        with self._lock:
            for _elc in self._event_callback_listeners:
                if _elc.connection_id == connection_id and callback == _elc.callback:
                    self._event_callback_listeners.remove(_elc)

    def queueUpdate(self, connection_id: int, rcv_update: RcvUpdate):
        with self._lock:
            self._queue_length += 1
            if self._queue_length > self._peak_length:
                self._peak_length = self._queue_length
                self._peak_time = Aux.currentMilliseconds()

        self._queue.add(ClientUpdateEvent(connection_id, rcv_update))

    def queueUpdates(self, connection_id: int, update_list: list[RcvUpdate]):
        with self._lock:
            for _upd in update_list:
                self._queue_length += 1
                if self._queue_length > self._peak_length:
                    self._peak_length = self._queue_length
                    self._peak_time = Aux.currentMilliseconds()
                self._queue.add(ClientUpdateEvent(connection_id, _upd))

    def queueEventDedicated(self, connection_id: int, event: DistributorEvent,
                            callback: Callable[[DistributorEvent], None]):
        with self._lock:
            self._queue_length += 1
            if self._queue_length > self._peak_length:
                self._peak_length = self._queue_length
                self._peak_time = Aux.currentMilliseconds()
        self._queue.add(ClientDedicatedAppEvent(connection_id, event, callback))

    def queueEvent(self, connection_id: int, event: DistributorEvent):
        with self._lock:
            self._queue_length += 1
            if self._queue_length > self._peak_length:
                self._peak_length = self._queue_length
                self._peak_time = Aux.currentMilliseconds()
        self._queue.add(ClientAppEvent(connection_id, event))

    def getQueueLength(self):
        return self._queue_length

    def getQueueSize(self) -> QueueSizeItem:
        with self._lock:
            _item: QueueSizeItem = QueueSizeItem()
            _item.setPeakSize(self._peak_length)
            _item.setPeakTime(Aux.time_string(self._peak_time))
            _item.setSize(self._queue_length)
            return _item

    def getSubscriptionFilter(self, connection_id: int) -> SubscriptionFilter | None:
        for _sfc in self._subscription_filters_list:
            if _sfc.connection_id == connection_id:
                return _sfc.subscription_filter
        return None

    def processEvent(self, event: ClientEvent):
        with self._lock:
            if event.event_type == ClientEvent.UPDATE:
                _filter = self.getSubscriptionFilter(event.connection_id)
                _updevt: ClientUpdateEvent = ClientUpdateEvent.cast(event)
                if _filter:
                    if _updevt.rcv_update:
                        _filter.match(_updevt.rcv_update.subject, _updevt.rcv_update.data,
                                      _updevt.rcv_update.app_ip, (self._queue_length - 1))
                        self._queue_length -= 1
                    elif _updevt.rcv_update_list:
                        for _upd in _updevt.rcv_update_list:
                            _filter.match(_upd.subject, _upd.data, _upd.app_ip, (self._queue_length - 1))
                            self._queue_length -= 1
            elif event.event_type == ClientEvent.APPEVENT:
                _appevt: ClientAppEvent = ClientAppEvent.cast(event)
                for _evtlst in self._event_callback_listeners:
                    if _evtlst.connection_id == _appevt.connection_id:
                        _evtlst.callback(_appevt.event)
                self._queue_length -= 1

            elif event.event_type == ClientEvent.DEDICATED_APPEVENT:
                _appevt: ClientDedicatedAppEvent = ClientDedicatedAppEvent.cast(event)
                _appevt.event_callback_if(_appevt.event)
                self._queue_length -= 1

            else:
                raise DistributorException('unknown client event ({}'.format(event.event_type))

    def run_process_event(self):
        while True:
            _event: ClientEvent = ClientEvent.cast(self._queue.take())
            self.processEvent(_event)

            if not self._queue.is_empty():
                _evtlst: list[ClientEvent] = self._queue.drain(30)
                if _evtlst:
                    for _cltevt in _evtlst:
                        self.processEvent(_cltevt)
