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


    def __init__(self, connection_id:int, subscription_filter:SubscriptionFilter):
        self.connection_id:int = connection_id
        self.subscription_filter:SubscriptionFilter = subscription_filter


class EventCallbackCntx(object):

    def __init__(self, connection_id:int, callback:Callable[ [DistributorEvent], None]):
        self.connection_id:int = connection_id
        self.callback : Callable[ [DistributorEvent], None] = callback


class ClientEvent(ABC):
    UPDATE = 1
    APPEVENT = 2
    DEDICATED_APPEVENT = 3

    def __init__(self, type, connection_id):
        if type < 1 or type > 3:
            raise DistributorEvent('Invalid ClientEventType ({})'.format(type))
        self.mEventType = type
        self.mDistributorConnectionId = connection_id

    @abstractmethod
    def getElementCount(self):
        pass

class ClientUpdateEvent(ClientEvent):
    def __init__(self, connection_id:int, arg):
        super().__init__(ClientEvent.UPDATE, connection_id)
        if isinstance(arg,list):
            self.mRcvUpdateList:list[RcvUpdate] = arg
            self.mRcvUpdate:RcvUpdate = None
            self.nRcvUpdateCount:int  = len( arg )
        elif isinstance( arg, RcvUpdate):
            self.mRcvUpdate:RcvUpdate = arg
            self.mRcvUpdateListlist:list[RcvUpdate] = None
            self.nRcvUpdateCount:int = 1

    def getElementCount(self):
       return self.mRcvUpdateCount

class ClientAppEvent(ClientEvent):
    def __init__(self, connection_id:int, pEvent:DistributorEvent):
        super().__init__(ClientEvent.APPEVENT, connection_id)
        self.mEvent = pEvent

    def getEventCount(self):
        return 1

class ClientDedicatedAppEvent(ClientEvent):
    def __init__(self, connection_id, event:DistributorEvent,  callback:Callable[ [DistributorEvent], None]):
        super().__init__(ClientEvent.DEDICATED_APPEVENT, connection_id)
        self.mEvent:DistributorEvent = event
        self.mEventCallbackIf = callback

    def getEventCount(self):
        return 1

class ClientDeliveryController(object):

    _cInstance:ClientDeliveryController = None

    @staticmethod
    def getInstance() -> ClientDeliveryController:
        if not ClientDeliveryController._cInstance:
            ClientDeliveryController._cInstance = ClientDeliveryController()
        return ClientDeliveryController._cInstance

    def __init__(self):
        self.mLock = threading.Lock()
        self.mSubscriptionFiltersList:list[SubscriptionFiltersCntx] = []
        self.mEventCallbackListeners:list[EventCallbackCntx] = []
        self.mQueueLength:int = 0
        self.mPeakLength:int = 0
        self.mPeakTime:int = 0
        self.mQueue:BlockingQueue = BlockingQueue()
        self.mLock = threading.Lock()
        self.thread = threading.Thread( self.run_process_event, name="process-client-events" )
        self.thread.start()

    def addSubscriptionFilter(self, connection_id:int, subscription_filter:SubscriptionFilter ):
        with self.mLock:
            _cntx = SubscriptionFiltersCntx( connection_id, subscription_filter )
            self.mSubscriptionFiltersList.append( _cntx )

    def removeSubscriptionFilter(self, connection_id: int, subscription_filter:SubscriptionFilter):
        with self.mLock:
            for _sfc in self.mSubscriptionFiltersList:
                if _sfc.connection_id == connection_id and subscription_filter == _sfc.subscription_filter:
                    self.mSubscriptionFiltersList.remove( _sfc )

    def addEventListner(self, connection_id:int, callback:Callable[ [DistributorEvent], None]):
        with self.mLock:
            self.mEventCallbackListeners.append( EventCallbackCntx( connection_id, callback ))


    def removeEventListner(self, connection_id:int, callback:Callable[ [DistributorEvent], None]):
        with self.mLock:
            for _elc  in self.mEventCallbackListeners:
                if _elc.connection_id == connection_id and callback == _elc.callback:
                    self.mEventCallbackListeners.remove( _elc )

    def queueUpdate( self, connection_id:int, rcv_update:RcvUpdate ):
        with self.mLock:
            self.mQueueLength += 1
            if self.mEventQueueLength > self.mPeakSize:
                self.mPeakSize = self.mQueueLength
                self.mPeakTime = Aux.currentMilliseconds()

        self.mQueue.add( ClientUpdateEvent(connection_id, rcv_update))

    def queueUpdates( self, connection_id:int, update_list:list[RcvUpdate] ):
         with self.mLock:
             for _upd in update_list:
                self.mQueueLength += 1
                if self.mEventQueueLength > self.mPeakSize:
                    self.mPeakSize = self.mQueueLength
                    self.mPeakTime = Aux.currentMilliseconds()
                self.mQueue.add( ClientUpdateEvent(connection_id, _upd))

    def queueEventDedicated( self, connection_id:int,  event:DistributorEvent, callback:Callable[ [DistributorEvent], None]):
        with self.mLock:
            self.mQueueLength += 1
            if self.mEventQueueLength > self.mPeakSize:
                self.mPeakSize = self.mQueueLength
                self.mPeakTime = Aux.currentMilliseconds()
        self.mQueue.add( ClientDedicatedAppEvent(connection_id, event, callback))


    def queueEvent( self, connection_id:int,  event:DistributorEvent ):
        with self.mLock:
            self.mQueueLength += 1
            if self.mEventQueueLength > self.mPeakSize:
                self.mPeakSize = self.mQueueLength
                self.mPeakTime = Aux.currentMilliseconds()
        self.mQueue.add( ClientAppEvent(connection_id, event ))

    def	getQueueLength(self):
        return self.mQueueLength

    def getQueueSize(self) -> QueueSizeItem:
        with self.mLock:
            _item:QueueSizeItem = QueueSizeItem()
            _item.setPeakSize(self.mPeakSize)
            _item.setPeakTime(Aux.time_string(self.mPeakTime))
            _item.setSize(self.mQueueLength)
            return _item

    def getSubscriptionFilter( self, connection_id:int ) -> SubscriptionFilter:
        for _sfc in self.mSubscriptionFiltersList:
            if _sfc.connection_id == connection_id:
                return _sfc.subscription_filter
        return None

    def processEvent( self, event:ClientEvent):
        with self.mLock:
            if event.mEventType == ClientEvent.UPDATE:
                _filter = self.getSubscriptionFilter(event.mDistributorConnectionId)
                _updevt:ClientUpdateEvent = event
                if _filter:
                    if _updevt.mRcvUpdate:
                        _filter.match(_updevt.mRcvUpdate.mSubject, _updevt.mRcvUpdate.mUpdateData,
                                  _updevt.mRcvUpdate.mAppId, (self.mQueueLength - 1))
                        self.mQueueLength -= 1
                    elif _updevt.mRcvUpdateList:
                        for _upd in _updevt.mRcvUpdateList:
                            _filter.match(_upd.mSubject, _upd.mUpdateData, _upd.mAppId, (self.mQueueLength - 1))
                            self.mQueueLength -= 1
            elif event.mEventType == ClientEvent.APPEVENT:
                _appevt:ClientAppEvent = event
                for _evtlst in self.mEventCallbackListeners:
                    if _evtlst.connection_id == _appevt.mDistributorConnectionId:
                        _evtlst.callback( _appevt.mEvent )
                self.mQueueLength -= 1

            elif event.mEventType == ClientEvent.DEDICATED_APPEVENT:
                _appevt:ClientDedicatedAppEvent = event
                _appevt.mEventCallbackIf(_appevt.mEvent)
                self.mQueueLength -= 1

            else:
                raise DistributorException('unknown client event ({}'.format( event.mEventType ))




    def run_process_event(self):
        while True:
            _event:ClientEvent = self.mQueue.take()
            self.processEvent(_event )

            if not self.mQueue.isEmpty():
                _evtlst:list[ClientEvent] = self.mQueue.drain(30)
                if _evtlst:
                    for _cltevt in _evtlst:
                        self.processEvent(_cltevt)

