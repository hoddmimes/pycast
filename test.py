
import time
import asyncio
import functools
from abc import ABC
from threading import Thread, current_thread, Event
from concurrent.futures import Future
from typing import Any


class BaseClass(ABC):

    def __str__(self):
        return "class name: {}".format( self.__class__.__name__)

    @classmethod
    def cast(cls, obj: object) -> Any:
        if isinstance(obj, cls):
            return obj
        if obj.__class__.__name__ == cls.__name__:
            return obj
        raise Exception("can not cast object to {}".format( cls.__name__))

class TestClass(BaseClass):
    def __init__(self, chr: str):
        self.a = chr
class TestClassXXX(BaseClass):
    def __init__(self):
        pass

def foo() -> tuple[int,str]:
    return (42,'frotz')


def test( base: BaseClass):
    x = foo()
    print(x)

def main():
    a = TestClass('frotz')
    test(a)







if __name__ == '__main__':
    main()
