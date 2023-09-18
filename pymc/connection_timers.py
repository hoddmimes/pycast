from __future__ import annotations

import random
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

from time import perf_counter
from pymc.event_timers.connection_timer_event import ConnectionTimerEvent
from pymc.connection_controller import ConnectionController
from pymc.aux.blocking_queue import BlockingQueue
from pymc.aux.aux import Aux


class TimerTaskWraper(object):
    def __init__(self, delay_ms: int, connection_timer_task: ConnectionTimerEvent, init_delay: int, repeat: bool, test_mode: bool = False):
        self._task: ConnectionTimerEvent = connection_timer_task
        self._delay_ms: int = delay_ms
        self._repeat: bool = repeat
        self._init_delay = init_delay or delay_ms
        self._test_mode = test_mode


    @classmethod
    def cast(cls, obj: object) -> TimerTaskWraper:
        if isinstance(obj, TimerTaskWraper):
            return obj
        else:
            raise Exception("can not cast object to {}".format(cls.__name__))

    @property
    def task(self) -> ConnectionTimerEvent:
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

        if not timer_task._test_mode:
            # Schedule the timer event in the connection event loop
            ConnectionController.get_instance().schedule_async_event(connection_id=timer_task.task.connection_id,
                                                                     async_event=timer_task.task)
        else:
            timer_task.task.execute(None)


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
        self._test_mode = False
        self._executor = ThreadPoolExecutor(max_workers=200)
        self._dispatcher = Thread(target=self._timer_task_dispatcher)
        self._dispatcher.start()

    def enable_test_mode(self):
        self._test_mode = True


    def _timer_task_dispatcher(self):
        while True:
            timer_task: TimerTaskWraper = TimerTaskWraper.cast(self._queue.take())
            self._executor.submit(_timer_executor_, timer_task)

    def queue(self, interval: int, task: ConnectionTimerEvent, init_delay: int = None,
              repeat: bool = True, test_mode: bool = False):

        timer_task: TimerTaskWraper = TimerTaskWraper(delay_ms=interval, connection_timer_task=task,
                                                      init_delay=init_delay, repeat=repeat, test_mode=test_mode)
        self._queue.add(timer_task)


# ===================================================================
#  Test
# ===================================================================
class _TestTask(ConnectionTimerEvent):

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
