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




def main():
   segment = Segment(1024)
   addr: int = Aux.ipAddrStrToInt('192.168.42.11')
   segment.setHeader(header_version=0x11,
                     messsage_type=Segment.MSG_TYPE_CONFIGURATION,
                     segment_flags=Segment.FLAG_M_SEGMENT_START+Segment.FLAG_M_SEGMENT_END,
                     local_address=addr,
                     sender_id=0x1234,
                     sender_start_time_sec=Aux.currentSeconds(),
                     app_id=0x9876)

   print(segment)
   print("time: {}".format(hex(segment.hdr_sender_start_time_sec)))
   print("segment hash: {}".format( hex(segment.__hash__())))
   map: dict[int, str] = {}
   map[segment] = 'segment-string'
   print('=============================')
   kk = 0
   for k in map.keys():
       print("map-key: {}".format(k))
       kk= k
   map.pop(kk)

   for k in map.keys():
       print("post-map-key: {}".format(k))



if __name__ == '__main__':
    main()
