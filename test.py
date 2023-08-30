from __future__ import annotations
import random
import threading
import time
<<<<<<< HEAD
import os
from abc import ABC
import types
import logging
from io import StringIO
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, Future
from concurrent.futures import ThreadPoolExecutor, Future

class Event(object):

    def __init__(self, int_value:int, str_value:str ):
        self.mIntValue = int_value
        self.mStrValue = str_value

    def __str__(self):
        return "int: {} str: {}".format(self.mIntValue, self.mStrValue)

class TestBase(ABC):

    def __init__(self, event: Event):
        self.mEvent = event

    def __str__(self):
        return "[ {} ] {}".format( self.__class__.__name__, self.mEvent)


class TestClass(TestBase):

    def __init__(self, event: Event):
        super().__init__(event)


def main():
    evt = Event(42, 'kalle')
    tc = TestClass(evt)
    print( tc )
=======

from pymc.aux.aux import Aux

rnd = random.Random()

class Message(object):

    def __init__(self):
        self._length: int = 0
        self._value: str = None

    def set(self, value: str ):
        self._length = len( value )
        self._value = value

    def __str__(self):
        return "len: {} string: {}".format(self._length, self._value)

class TestClass(object):
    def __init__(self, msg: Message):
        self._message: Message = msg

    def send(self, message: Message) -> None:
        print(" Sending Message: {}".format( message))
        return None

    def test(self):
        self._message = self.send( self._message)

    def to_string(self):
        if self._message is None:
            print("message value is None")
        else:
            print(" Message: {}".format( self._message))




def getKey( mc_address: int,  mc_port: int, host_address: int) -> int:
    tValue = (Aux.swapInt(mc_address) << 40) + (Aux.swapInt(host_address) << 16) + (Aux.swapInt(mc_port) & 0xffff)
    return tValue




def main():
>>>>>>> 881b668 (intermidate commit, work in progress)


   local_address: int = Aux.ipAddrStrToInt(Aux.getIpAddress(''))
   mc_address: int = Aux.ipAddrStrToInt('224.10.10.12')
   mc_port: int = 5432

   key = getKey( mc_address, mc_port, local_address)
   print("key: {0:x}".format(key))
   print("host: {0:x}".format(local_address))
   print("mca: {0:x}".format(mc_address))
   print("port: {0:x}".format(mc_port))




if __name__ == '__main__':
    main()
