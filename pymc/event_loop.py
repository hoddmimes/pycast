import threading
import time
import asyncio
from abc import ABC, abstractmethod
from threading import Thread, current_thread
from concurrent.futures import Future
from typing import Callable, Any

from pymc.aux.distributor_exception import DistributorException


class ConnectionEvent(ABC):
    API_EVENT = "API_EVENT"
    NET_MESSAGE = "NET_MESSAGE"
    TIMER_EVENT = "TIMER_EVENT"

    def __init__(self, event_type: str):
        self._event_type = event_type

    @property
    def event_type(self) -> str:
        return self._event_type


    @classmethod
    def cast(cls, obj) -> Any:
        if isinstance(obj, cls):
            return obj
        raise DistributorException("can't cast object to {}".format( cls.__name__))


async def _dispatcher_(dispatcher: Callable[[ConnectionEvent], Any], event: ConnectionEvent):
    return dispatcher(event)


class EventLoop(Thread):
    def __init__(self, dispatcher: Callable[[ConnectionEvent], Any]):
        Thread.__init__(self)
        self.loop = None
        self.tid = None
        self._started_event: threading.Event = threading.Event()
        self.dispatcher: Callable[[ConnectionEvent], Any] = dispatcher

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.tid = current_thread()
        self._started_event.set()
        self.loop.run_forever()

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)

    def queue_event(self, event: ConnectionEvent):
        def _add_task(func) -> Future:
            if self.tid == current_thread():
              func()
            else:
                return asyncio.run_coroutine_threadsafe(func, self.loop)

        _add_task(_dispatcher_(self.dispatcher, event))

    def queue_event_wait(self, event: ConnectionEvent) -> object:
        def _add_task_wait(func) -> Future:
            f: Future = asyncio.run_coroutine_threadsafe(func, self.loop)
            return f

        if self.tid == current_thread():
            return _dispatcher_(self.dispatcher, event)
        else:
            future: Future = _add_task_wait(_dispatcher_(self.dispatcher, event))
            return future.result(None) # wait for the task to complete and return the result

    def wait_for_the_loop_to_start(self):
        self._started_event.wait()

    def cancel_task(self, task):
        self.loop.call_soon_threadsafe(task.cancel)


class EventLoopInterface(ABC):

    @abstractmethod
    def schedule_async_event(self, connection_id: int, async_event: 'ConnectionEvent', wait: bool = False) -> Any:
        pass

