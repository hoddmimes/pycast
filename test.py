import threading
import time
import asyncio
import functools
from abc import ABC
from threading import Thread, current_thread, Event
from concurrent.futures import Future
from typing import Any

from pymc.aux.aux import Aux
from pymc.aux.blocking_queue import BlockingQueue
from pymc.aux.linked_list import ListItr, LinkedList
from pymc.msg.net_msg_retransmission import NetMsgRetransmissionRqst
from pymc.msg.segment import Segment


class AddEvent(object):

    def __init__(self, value: int = 1):
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    @classmethod
    def cast(cls, obj: object) -> Any:
        if isinstance(obj, cls):
            return obj
        if obj.__class__.__name__ == cls.__name__:
            return obj
        raise Exception("can not cast object to {}".format(cls.__name__))


class TestClass(Thread):
    def __init__(self, condition: int):
        super().__init__()
        self._counter: int = 0
        self._mutex: threading.Lock = threading.Lock()
        self._queue = BlockingQueue()
        self._wait_event = threading.Event()
        self._condition = condition
        self._counter = 0

    def __enter__(self):
        self._mutex.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._mutex.release()

    def incremen(self, event: AddEvent):
        self._queue.add(event)

    def wait_for_all(self):
        if not self._queue.is_empty():
            self._wait_event.wait()

    @property
    def counter(self):
        return self._counter

    def run(self):
        while (True):
            _evt: AddEvent = AddEvent.cast(self._queue.take())
            self._counter += _evt.value
            self._counter += 1
            if self._counter == self._condition:
                print("end condition reached")
                self._wait_event.set()


def main():
    filename: str = "/home/bertilsson/source/pycast/pymc/aux/trace.py"
    componets = filename.split('/')
    print(componets[-1])

    interations: int = 250000
    tstcls = TestClass(interations)
    tstcls.start()
    _start = time.perf_counter_ns()
    for x in range(interations):
        with tstcls:
            tstcls.incremen(AddEvent(1))

    tstcls.wait_for_all()
    _exec_time = (time.perf_counter_ns() - _start) / 1000.0
    print("overhead {} usec".format(_exec_time / tstcls.counter))


if __name__ == '__main__':
    main()
