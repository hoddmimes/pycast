from __future__ import annotations

import random
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, Future
from threading import Thread

from time import perf_counter

from pymc.aux.distributor_exception import DistributorException
from pymc.connection_timer_task import ConnectionTimerTask
from pymc.connection_controller import ConnectionController
from pymc.aux.blocking_queue import BlockingQueue
from pymc.aux.aux import Aux

import time




class TimerTaskWraper(object):
    def __init__(self, delay_ms: int, connection_timer_task: ConnectionTimerTask, init_delay: int, repeat: bool):
        self._task: ConnectionTimerTask = connection_timer_task
        self._delay_ms: int = delay_ms
        self._repeat: bool = repeat
        self._init_delay = init_delay or delay_ms


    @classmethod
    def cast(cls, obj: object) -> TimerTaskWraper:
        if isinstance(obj, TimerTaskWraper):
            return obj
        else:
            raise Exception("can not cast object to {}".format(cls.__name__))

    @property
    def task(self) -> ConnectionTimerTask:
        return self._task

    @property
    def delay_ms(self) -> int:
        return self._delay_ms

    @property
    def repeat(self) -> bool:
        return self._repeat

    @property
    def init_delay(self) -> int:
        return self._init_delay


def _timer_executor_(timer_task: TimerTaskWraper):
    # Always execute one time
    _first_execution: bool = True
    while timer_task.repeat or _first_execution:
        if timer_task.task.canceled:
            return

        if _first_execution:
            Aux.sleep_ms(timer_task.init_delay)
            _first_execution = False
        else:
            Aux.sleep_ms(timer_task.delay_ms)

        if timer_task.task.connection_id == 0: # test connection id
            timer_task.task.execute(None)
        else:
            _connection = ConnectionController.get_instance().get_connection(connection_id=timer_task.task.connection_id)
            if _connection is None:
                raise DistributorException("Can not retreive connection with id {}, appears to be closed and removed".format(hex(timer_task.task.connection_id)))
            with _connection:
                try:
                    timer_task.task.execute(_connection)
                except Exception as e:
                    _connection.log_exception(e)



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
        self._executor = ThreadPoolExecutor(max_workers=200)
        self._dispatcher = Thread(target=self._timer_task_dispatcher)
        self._dispatcher.start()

    def _timer_task_dispatcher(self):
        while True:
            timer_task: TimerTaskWraper = TimerTaskWraper.cast(self._queue.take())
            self._executor.submit(_timer_executor_, timer_task)

    def queue(self, interval: int, task: ConnectionTimerTask, init_delay: int = None, repeat: bool = True):
        timer_task: TimerTaskWraper = TimerTaskWraper(delay_ms=interval, connection_timer_task=task, init_delay=init_delay, repeat=repeat)
        self._queue.add(timer_task)


# ===================================================================
#  Test
# ===================================================================
class _TestTask(ConnectionTimerTask):

    def __init__(self, connection_id, interval, thread_id):
        super().__init__(connection_id)
        self.startTime = perf_counter()
        self.interval = interval
        self.thread_id = thread_id
        self._count = 0
        self._overhead = 0

    def execute(self, connection):
        self._count += 1
        _exec_time = (perf_counter() - self.startTime) * 1000.0
        self._overhead += _exec_time - self.interval
        self.startTime = perf_counter()
        if (self._count % 200) == 0:
            print('thread: {} interval: {} time: {} overhead: {}'.format(self.thread_id, self.interval, _exec_time, (self._overhead/ self._count)))


"""
## ======================================
##     Test
## ======================================
"""


def test():
    executor = ConnectionTimerExecutor.getInstance()
    '''
        _task = _TestTask(0, 765)
        executor.queue(interval=765, task=_task, repeat=True)
        time.sleep(200)
    '''
   
    for i in range(10):
        _delay = random.randrange(start=100, stop=460)
        _task = _TestTask(0, _delay, (i+1))
        executor.queue(interval=_delay, task=_task, repeat=True)
    time.sleep(300)

if __name__ == '__main__':
    test()
