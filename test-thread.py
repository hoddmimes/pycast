import threading
import time
import os
import types
import logging
import ctypes
from io import StringIO
from datetime import datetime
from threading import Thread
from pymc.aux.distributor_exception import DistributorTheadExitException






class AuxThread(threading.Thread):

    def __int__(self):
        self._time_to_exit = False

    @property
    def thread_id(self):
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def stop(self):
        _id = self.thread_id
        _sts = res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(_id), ctypes.py_object(DistributorTheadExitException))
        print("id: {} status: {}".format( _id,  _sts ))



class TestThread(AuxThread):



    def run(self):
        while True:
            try:
                print("thread id {} is alive {} native-id: {}".format( self.ident, self.is_alive(), self.native_id))
                time.sleep(3)
            except Exception as e:
                print( "Thread exception: {} ".format(e))
                return
    def stopThread(self):
        print("stopping-thread")


def main():
    ts = TestThread()
    ts.start()
    time.sleep(5)
    ts.stop()
    time.sleep(300)





if __name__ == '__main__':
    main()