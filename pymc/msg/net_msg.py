from abc import ABC
from pymc.msg.codec import Encoder,Decoder
from pymc.msg.segment import Segment


class NetMsg( ABC ):

    IGNORE = 0
    SYNCH = 1
    LOWER = 2
    HIGHER = 3

    VERSION:int = 0x0100


    def __init__(self, segment:Segment):
        self.mSegment = segment

    def getSegment(self):
        return self.mSegment

    def getEncoder(self) -> Encoder:
        return self.mSegment.getEncoder()

    def getDecoder(self) -> Decoder:
        self.mSegment.getDecoder()

    def setHeader( self, headerVersion:int, messageType:int, segmentFlags:int,
                   localAddress:int, senderId:int, senderStartTime:int, appId:int):
        self.mSegment.setHeader(headerVersion, messageType, segmentFlags, localAddress, senderId,senderStartTime,appId)

    def setHeaderSegmentFlags(self, segmentFlags:int):
        self.mSegment.mHdrSegmentFlags = segmentFlags

    def getHeaderLocalSourceAddress( self) -> int:
        return self.mSegment.mHdrLocalAddress

    def getHeaderSegmentFlags(self) -> int:
        return self.mSegment.mHdrSegmentFlags

    def getHeaderSenderStartTime(self) -> int:
        return self.mSegment.mHdrSenderStartTime

    def getHeaderAppId(self) -> int:
        return self.mSegment.mHdrAppId

    def setSeqno(self, seqno:int):
        self.mSegment.mSeqno = seqno

    def getSeqno(self) -> int:
        return self.mSegment.mSeqno

    def encode(self) -> Encoder:
        self.mSegment.encode()
        return self.mSegment.mEncoder

    def decode(self) -> Decoder:
        self.mSegment.decode()
        return self.mSegment.mDecoder

    def __str__(self) ->str:
        return self.mSegment.toString()
