from __future__ import annotations
import random
import threading
import time
import os
from abc import ABC
import types
import logging
from io import StringIO
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, Future
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Any
from pymc.msg.segment import Segment
from pymc.aux.aux import Aux


class TestClass(object):
    def __init__(self, msg: str, value: int):
        self._message: str = msg
        self._value = value

    @property
    def message(self) ->str:
        return self._message

    @message.setter
    def message(self, value: str):
        self._message = value

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value:  int):
        self._value = value

    def __str__(self):
        return "message: {} value: {}".format( self._message, self._value)

    def __hash__(self):
        return Aux.hash32( self._message)

    def __eq__(self, other: TestClass):
        if self._message == other.message and self.value == other.value:
            return True
        else:
            return False


def timer_callback( arg1, arg2, arg3 ):
    print(arg3)


def main():
   t = threading.Timer( interval=3, function=timer_callback, args=(42,'frotz','foo'))
   t.start()
   time.sleep(200)

if __name__ == '__main__':
    main()
