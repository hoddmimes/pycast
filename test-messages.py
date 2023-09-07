import random
import time
import os
from abc import ABC
import types
import logging
from io import StringIO
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, Future
from concurrent.futures import ThreadPoolExecutor, Future
from pymc.aux.aux import Aux
from pymc.msg.codec import Encoder, Decoder
from pymc.msg.segment import Segment
from pymc.msg.rcv_segment import RcvSegment
from pymc.msg.rcv_update import RcvUpdate
from pymc.msg.rcv_segment import RcvSegment,RcvSegmentBatch
from pymc.msg.xta_update import XtaUpdate
from pymc.msg.xta_segment import XtaSegment
from pymc.msg.net_msg_update import NetMsgUpdate

class C(object):

    def tst(self):
        print("[C] name: {}".format( self.__class__.__name__))



class B(ABC):

    def __init__(self, c_class:C ):
        self.c_class = c_class
    def tst(self):
        self.c_class.tst()
        print("[B] name: {}".format(self.__class__.__name__))

class A(B):

    def __init__(self, c_class:C):
        super().__init__(c_class)
    def tst(self):
        super().tst()
        print("[A] name: {}".format(self.__class__.__name__))


def creXtaUpd( index: int ) -> XtaUpdate:
    tSize:int = random.randint(10,256)
    tChar:int  = random.randint(65,93)
    tData:bytearray = bytes([tChar] * tSize )
    xtaupd = XtaUpdate("subject-{}".format((index+1)), tData, tSize )
    return xtaupd

def testMany():
    segment:Segment = Segment( 8192 )
    netUpdate: NetMsgUpdate = NetMsgUpdate( segment )

    netUpdate.setHeader(messageType=Segment.MSG_TYPE_UPDATE,
                        segmentFlags=Segment.FLAG_M_SEGMENT_START+Segment.FLAG_M_SEGMENT_END,
                        localAddress=0x0A0A0A0A,
                        senderId=2222,
                        senderStartTime=Aux.current_seconds(),
                        appId=9999)

    for i in range(10):
        xtaUpd: XtaUpdate = creXtaUpd( i )
        netUpdate.addUpdate( xtaUpd )

    netUpdate.setSeqno(4711)


    netUpdate.encode()

    xtaSegment: Segment = netUpdate.getSegment()


    bytbuf = xtaSegment.mEncoder.getBuffer()
    netUpdate = NetMsgUpdate( Segment(bytbuf))
    netUpdate.decode()

    updates:list[RcvUpdate] = netUpdate.getUpdates(42)

    for upd in updates:
        print( upd )


def testCodec():
    bytarr: bytearray = bytes([66] *64 )
    enc: Encoder = Encoder( 512 )
    enc.addInt(1111)
    enc.addBool(True)
    enc.addString('hello world')
    enc.addBytes( bytarr )

    buffer = enc.getBuffer()

    dec: Decoder = Decoder( buffer )
    intValue: int = dec.getInt()
    boolValue: bool = dec.getBool()
    strValue: str = dec.getString()
    bytarr = dec.getBytes()

    print("int: {} bool:{} str: {} bytes: {}".format( intValue, boolValue, strValue, bytarr))

def testBytArr():
    ba = bytearray([32] * 64)
    sa = bytearray( 'foobar', 'utf-8')
    ba[ 2:2+len(sa) ] = sa
    print("Len: {} ba: {}".format( len(ba), ba ))

def testInherit():
    c:C = C()
    a:A = A(c)
    a.tst()


def testTime():
    ms = Aux.current_milliseconds()
    ss = Aux.current_seconds()
    print("ms: {} ss: {}".format( ms, ss))
    print("ms: {} ss: {}".format(Aux.time_string(ms) , Aux.time_string(ss)))

def testMany():
    segment:Segment = Segment( 8192 )
    netUpdate: NetMsgUpdate = NetMsgUpdate( segment )

    netUpdate.setHeader(message_type=Segment.MSG_TYPE_UPDATE,
                        segment_flags=Segment.FLAG_M_SEGMENT_START+Segment.FLAG_M_SEGMENT_END,
                        local_address=0x0A0A0A0A,
                        sender_id=2222,
                        sender_start_time_sec=Aux.current_seconds(),
                        app_id=9999)

    for i in range(10):
        xtaUpd: XtaUpdate = creXtaUpd( i )
        netUpdate.addUpdate( xtaUpd )

    netUpdate.sequence_no = 4711
    xtaSegment: Segment = netUpdate.segment


    _bytbuf = xtaSegment.encoder.buffer
    netUpdate = NetMsgUpdate( Segment(_bytbuf))
    netUpdate.decode()

    updates:list[RcvUpdate] = netUpdate.getUpdates(42)

    for upd in updates:
        print( upd )


def get_net_update() -> NetMsgUpdate:
    segment: Segment = Segment(8192)
    netUpdate: NetMsgUpdate = NetMsgUpdate(segment)

    netUpdate.setHeader(message_type=Segment.MSG_TYPE_UPDATE,
                        segment_flags=Segment.FLAG_M_SEGMENT_START,
                        local_address=0x0A0A0A0A,
                        sender_id=2222,
                        sender_start_time_sec=Aux.current_seconds(),
                        app_id=9999)

    return netUpdate

def testLarge():
    tXtaBuffers:list[bytearray] = []
    tLargeData = bytearray([120] * 12345)

    xtaUpdate: XtaUpdate =  XtaUpdate("subject-large", tLargeData )

    netUpdMsg = get_net_update()
    netUpdMsg.addLargeUpdateHeader('subject-large', len(tLargeData))

    _offset = 0
    _segment_count = 0
    _seq_no = 100

    while _offset < xtaUpdate.mDataLength:
        _offset += netUpdMsg.addLargeData(xtaUpdate.mData, _offset)
        netUpdMsg.update_count = 1
        if _segment_count == 0:
            netUpdMsg.hdr_segment_flags=Segment.FLAG_M_SEGMENT_START
            netUpdMsg.sequence_no = _seq_no
            _seq_no += 1
            _segment_count += 1
            tXtaBuffers.append(netUpdMsg.buffer)
        elif _offset == xtaUpdate.mDataLength:
            netUpdMsg.hdr_segment_flags = Segment.FLAG_M_SEGMENT_END
            netUpdMsg.sequence_no = _seq_no
            _seq_no += 1
            _segment_count += 1
            tXtaBuffers.append(netUpdMsg.buffer)
        else:
            netUpdMsg.hdr_segment_flags = Segment.FLAG_M_SEGMENT_MORE
            netUpdMsg.sequence_no = _seq_no
            _seq_no += 1
            _segment_count += 1
            tXtaBuffers.append(netUpdMsg.buffer)

        netUpdMsg = get_net_update()

    # ==========================================
    #      Decode large update
    # ==========================================
    tRcvBatch: RcvSegmentBatch = RcvSegmentBatch()
    for _buffer in tXtaBuffers:
        tRcvSegment = RcvSegment( _buffer )
        tRcvBatch.addSegment( tRcvSegment)

    tUpdates: list[RcvUpdate] = tRcvBatch.getUpdates( 42 )
    for upd in tUpdates:
        print(upd)
        for i in range(len(upd.data)):
            if upd.data[i] != 120:
                raise Exception("invalid char at {}".format(i))
        print("All done !")


def main():
    # testBytArr()
    # testCodec()
    # testInherit()
    #testTime()
    testMany()
    #testLarge()




if __name__ == '__main__':
    main()
