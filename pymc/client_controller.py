from __future__ import annotations
from typing import Callable
import threading

from pymc.aux.aux import Aux
from pymc.aux.blocking_queue import BlockingQueue
from pymc.aux.distributor_exception import DistributorException
from pymc.clients_events import SubscriptionFiltersCntx, EventCallbackCntx, ClientUpdateEvent, ClientDedicatedAppEvent
from pymc.clients_events import ClientAppEvent, ClientEvent
from pymc.distributor_events import DistributorEvent
from pymc.msg.generated.net_messages import QueueSizeItem
from pymc.msg.rcv_update import RcvUpdate
from pymc.subscription import SubscriptionFilter


class ClientDeliveryController(object):
    _cInstance: ClientDeliveryController = None

    @staticmethod
    def get_instance() -> ClientDeliveryController:
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

    def add_subscription_filter(self, connection_id: int, subscription_filter: SubscriptionFilter):
        with self._lock:
            _cntx = SubscriptionFiltersCntx(connection_id, subscription_filter)
            self._subscription_filters_list.append(_cntx)

    def remove_subscription_filter(self, connection_id: int, subscription_filter: SubscriptionFilter):
        with self._lock:
            for _sfc in self._subscription_filters_list:
                if _sfc.connection_id == connection_id and subscription_filter == _sfc.subscription_filter:
                    self._subscription_filters_list.remove(_sfc)

    def add_event_listner(self, connection_id: int, callback: Callable[[DistributorEvent], None]):
        with self._lock:
            self._event_callback_listeners.append(EventCallbackCntx(connection_id, callback))

    def remove_event_listner(self, connection_id: int, callback: Callable[[DistributorEvent], None]):
        with self._lock:
            for _elc in self._event_callback_listeners:
                if _elc.connection_id == connection_id and callback == _elc.callback:
                    self._event_callback_listeners.remove(_elc)

    def queue_update(self, connection_id: int, rcv_update: RcvUpdate):
        with self._lock:
            self._queue_length += 1
            if self._queue_length > self._peak_length:
                self._peak_length = self._queue_length
                self._peak_time = Aux.current_milliseconds()

        self._queue.add(ClientUpdateEvent(connection_id, rcv_update))

    def queue_updates(self, connection_id: int, update_list: list[RcvUpdate]):
        with self._lock:
            for _upd in update_list:
                self._queue_length += 1
                if self._queue_length > self._peak_length:
                    self._peak_length = self._queue_length
                    self._peak_time = Aux.current_milliseconds()
                self._queue.add(ClientUpdateEvent(connection_id, _upd))

    def queue_event_dedicated(self, connection_id: int, event: DistributorEvent,
                              callback: Callable[[DistributorEvent], None]):
        with self._lock:
            self._queue_length += 1
            if self._queue_length > self._peak_length:
                self._peak_length = self._queue_length
                self._peak_time = Aux.current_milliseconds()
        self._queue.add(ClientDedicatedAppEvent(connection_id, event, callback))

    def queue_event(self, connection_id: int, event: DistributorEvent):
        with self._lock:
            self._queue_length += 1
            if self._queue_length > self._peak_length:
                self._peak_length = self._queue_length
                self._peak_time = Aux.current_milliseconds()
        self._queue.add(ClientAppEvent(connection_id, event))

    def getQueueLength(self):
        return self._queue_length

    def get_queue_size(self) -> QueueSizeItem:
        with self._lock:
            _item: QueueSizeItem = QueueSizeItem()
            _item.set_peak_size(self._peak_length)
            _item.set_peak_time(Aux.time_string(self._peak_time))
            _item.set_size(self._queue_length)
            return _item

    def get_subscription_filter(self, connection_id: int) -> SubscriptionFilter | None:
        for _sfc in self._subscription_filters_list:
            if _sfc.connection_id == connection_id:
                return _sfc.subscription_filter
        return None

    def process_event(self, event: ClientEvent):
        with self._lock:
            if event.event_type == ClientEvent.UPDATE:
                _filter = self.get_subscription_filter(event.connection_id)
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
            self.process_event(_event)

            if not self._queue.is_empty():
                _evtlst: list[ClientEvent] = self._queue.drain(30)
                if _evtlst:
                    for _cltevt in _evtlst:
                        self.process_event(_cltevt)
