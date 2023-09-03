from __future__ import annotations

import random
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, Future
from threading import Thread

from time import perf_counter
from pymc.connection_timer_task import ConnectionTimerTask
from pymc.connection_controller import ConnectionController
from pymc.aux.blocking_queue import BlockingQueue
from pymc.aux.aux import Aux

import time




class TimerTaskWraper(object):
    def __init__(self, delay_ms: int, connection_timer_task: ConnectionTimerTask, repeat: bool = False):
        self._task: ConnectionTimerTask = connection_timer_task
        self._delay_ms: int = delay_ms
        self._repeat: bool = repeat
        self._queue_time: float = perf_counter()

    @classmethod
    def cast(cls, obj: object) -> TimerTaskWraper:
        if isinstance(obj, TimerTaskWraper):
            return obj
        else:
            raise Exception("can not cast object to {}".format(cls.__name__))

    @property
    def overhead(self) -> int:
        return int((perf_counter() - self._queue_time) * 1000.0)

    @property
    def task(self) -> ConnectionTimerTask:
        return self._task

    @property
    def delay_ms(self) -> int:
        return self._delay_ms

    @property
    def repeat(self) -> bool:
        return self._repeat


def _timer_executor_(timer_task: TimerTaskWraper):
    Aux.sleepMs(timer_task.overhead)

    connection = ConnectionController.getInstance().getAndLockConnection(connection_id=timer_task.task.connection_id)
    try:
        timer_task.task.execute(connection)
        if timer_task.repeat and not timer_task.task.canceled:
            ConnectionTimerExecutor.getInstance().queue(interval=timer_task.delay_ms, task=timer_task.task,
                                                        repeat=timer_task.repeat)
    except Exception as e:
        print(e)
    finally:
        if connection:
            connection.unlock()


class ConnectionTimerExecutor(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    @staticmethod
    def getInstance() -> ConnectionTimerExecutor:
        if not ConnectionTimerExecutor._instance:
            ConnectionTimerExecutor._instance = ConnectionTimerExecutor()
        return ConnectionTimerExecutor._instance

    def __init__(self):
        self._queue = BlockingQueue()
        self._executor = ThreadPoolExecutor()
        self._dispatcher = Thread(target=self._timer_task_dispatcher)
        self._dispatcher.start()

    def _timer_task_dispatcher(self):
        while True:
            timer_task: TimerTaskWraper = TimerTaskWraper.cast(self._queue.take())
            self._executor.submit(_timer_executor_, timer_task)

    def queue(self, interval: int, task: ConnectionTimerTask, repeat: bool = True):
        timer_task: TimerTaskWraper = TimerTaskWraper(delay_ms=interval, connection_timer_task=task, repeat=repeat)
        self._queue.add(timer_task)


# ===================================================================
#  Test
# ===================================================================
class _TestTask(ConnectionTimerTask):

    def __init__(self, connection_id, interval):
        super().__init__(connection_id)
        self.startTime = perf_counter()
        self.interval = interval

    def execute(self, connection):
        _exectime = (perf_counter() - self.startTime) * 1000.0
        print('interval: {} time: {}'.format(self.interval, _exectime))


"""
## ======================================
##     Test
## ======================================
"""


def test():
    executor = ConnectionTimerExecutor.getInstance()
    for i in range(10):
        _delay = random.randrange(start=10, stop=46)
        _task = _TestTask(0, _delay)
        executor.queue(interval=_delay, task=_task)
        time.sleep(3)


if __name__ == '__main__':
    test()
