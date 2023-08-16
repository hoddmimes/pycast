import time
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






if __name__ == '__main__':
    main()
