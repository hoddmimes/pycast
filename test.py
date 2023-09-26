
import time
import asyncio
import functools
from abc import ABC
from threading import Thread, current_thread, Event
from concurrent.futures import Future
from typing import Any

from pymc.aux.aux import Aux
from pymc.aux.blocking_queue import BlockingQueue
from pymc.aux.linked_list import ListItr, LinkedList
from pymc.msg.net_msg_retransmission import NetMsgRetransmissionRqst
from pymc.msg.segment import Segment


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
    xsegment: Segment = Segment(512)
    xsegment.setHeader( header_version=0x0101,
                       messsage_type=5,
                       segment_flags=Segment.FLAG_M_SEGMENT_START+Segment.FLAG_M_SEGMENT_END,
                       local_address=123456789,
                       sender_id=4242,
                       sender_start_time_sec=Aux.current_seconds(),
                       app_id=0x6666)


    xmsg: NetMsgRetransmissionRqst = NetMsgRetransmissionRqst(xsegment)
    xmsg.set(requestor_addr=234567890,
            low_seqno=11,
            host_name="123456789",
            high_seqno=12,
            appl_name='test',
            remote_sender_id=8888,
            remote_sender_start_time_ms=2424242424)

    xmsg.encode()
    print(xmsg)
    data:bytes = xmsg.segment.buffer

    rsegment:Segment = Segment(data)
    rmsg: NetMsgRetransmissionRqst = NetMsgRetransmissionRqst(rsegment)
    rmsg.decode()

    print( rmsg )






if __name__ == '__main__':
    main()
