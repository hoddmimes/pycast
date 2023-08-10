from __future__ import annotations

import random
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor,Future
from threading import Thread

from time import perf_counter, perf_counter_ns
from pymc.connection import Connection
from pymc.connection_controller import ConnectionController
from pymc.aux.blocking_queue import BlockingQueue
from pymc.aux.aux import Aux

import time

class ConnectionTimerTask(ABC):

    def __init__(self, connectionId):
        self.mConnectionId = connectionId
        self.mCanceled = False

    def cancel(self):
        self.mCanceled = True

    @abstractmethod
    def execute( self, connection:Connection ):
        pass

class _TimerTaskWraper_(object):
    def __init__(self, delay_ms:int , connectionTimerTask:ConnectionTimerTask, repeat:bool=False):
        self.task:ConnectionTimerTask = connectionTimerTask
        self.delay_ms = delay_ms
        self.repeat:bool = repeat
        self.queue_time = perf_counter()


def _timer_executor_(timerTask:_TimerTaskWraper_ ):
    _overhead = int((perf_counter() - timerTask.queue_time) * 1000.0)
    Aux.sleepMs(timerTask.delay_ms - _overhead)

    tConnection:Connection = ConnectionController.getAndLockConnection( timerTask.task.mConnectionId )
    try:
        timerTask.task.execute( tConnection )
        if timerTask.repeat and not timerTask.task.mCanceled:
            ConnectionTimerExecutor.getInstance().add( delay_ms=timerTask.delay_ms, task=timerTask.task, repeat=timerTask.repeat)
    except Exception as e:
        print(e)
    finally:
        if tConnection:
            tConnection.unlock()
class ConnectionTimerExecutor(object):

    _instance = None
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


    @staticmethod
    def getInstance() -> ConnectionTimerExecutor:
        if not ConnectionTimerExecutor._instance:
            ConnectionTimerExecutor._instance = ConnectionTimerExecutor()
        return ConnectionTimerExecutor._instance

    def __init__(self):
        self._queue = BlockingQueue()
        self._executor = ThreadPoolExecutor()
        self._dispatcher = Thread( target=self._timer_task_dispatcher)
        self._dispatcher.start()


    def _timer_task_dispatcher( self ):
        while True:
            timerTask:_TimerTaskWraper_ = self._queue.take()
            future:Future = self._executor.submit( _timer_executor_, timerTask)



    def add( self, delay_ms:int, task:ConnectionTimerTask, repeat=False):
        timerTask:_TimerTaskWraper_ = _TimerTaskWraper_(delay_ms=delay_ms, connectionTimerTask=task, repeat=repeat)
        self._queue.add(timerTask)



#===================================================================
#  Test
#===================================================================
class _TestTask( ConnectionTimerTask ):

    def __init__(self, connection_id, interval):
        super().__init__(connection_id)
        self.startTime = perf_counter()
        self.interval = interval

    def execute( self, connection:Connection ):
        _exectime = (perf_counter() - self.startTime) * 1000.0
        print('interval: {} time: {}'.format(self.interval, _exectime))


## ======================================
##     Test
## ======================================
def test():
    executor = ConnectionTimerExecutor.getInstance()
    for i in range(10):
        _delay = random.randrange( start=10, stop=46)
        _task = _TestTask(0, _delay)
        executor.add( delay_ms=_delay, task=_task)
        time.sleep(3)


if __name__ == '__main__':
    test()
