from __future__ import annotations
from pymc.msg.codec import Encoder, Decoder
from pymc.aux.atomic import AtomicLong
from pymc.aux.aux import Aux
from pymc.msg.net_msg import NetMsg
from pymc.msg.rcv_update import RcvUpdate
from pymc.msg.segment import Segment
from pymc.msg.xta_update import XtaUpdate
from io import StringIO

class NetMsgUpdate(NetMsg):

    cSeqnoStamp = AtomicLong(1)

    MIN_UPDATE_HEADER_SIZE = Segment.SEGMENT_HEADER_SIZE + 8 # segment-header-size + seqno:int + update-count:int


    def __init__(self, segment:Segment):
        super().__init__( segment )
        self.mUpdateCount:int = 0                     # Number of updates in segment
        self.mFlushSequenceNumber:int = 0
        self.mCreateTime:int = Aux.currentMilliseconds()        # Time when the NetMessage was created

        self.mLargeSubjectName:str = None
        self.mLargeMessageSize:int = 0

    def setHeader( self,
                   messageType:int,
                   segmentFlags:int,
                   localAddress:int,
                   senderId:int,
                   senderStartTime:int,
                   appId:int ) :

        super().setHeader( messageType, segmentFlags, localAddress, senderId, senderStartTime, appId)
        # now encode header
        tEncoder:Encoder = super().encode();
        tEncoder.addInt( self.mUpdateCount )
        tEncoder.addInt( 0 )                    # placeholder for the sequence number

    def getMinUpdateHeaderSize(self):
        return (Segment.SEGMENT_HEADER_SIZE + 8) # Segment-header-size + (sequence number + update count )


    def decode(self):
        tDecoder:Decoder = super().decode()
        super().setSeqno( tDecoder.getInt())
        self.mUpdateCount = tDecoder.getInt()

    def encode(self):
        # Poke in the update count header in the header
        tEncoder:Encoder = super().getEncoder();
        tEncoder.putIntAt( Segment.SEGMENT_HEADER_SIZE, self.getSeqno())
        tEncoder.putIntAt( Segment.SEGMENT_HEADER_SIZE+4, self.mUpdateCount)

    def setSequenceNumber(self, seqno:int ):
        self.mSegment.setSeqno( seqno )



    def getSequenceNumber(self) -> int:
        return self.mSegment.getSeqno()

    def addUpdate(self, xtaUpdate: XtaUpdate) -> bool:
        tEncoder:Encoder = super().getEncoder()
        if xtaUpdate.getSize() <= tEncoder.getRemaining():
            tEncoder.addString( xtaUpdate.mSubject )
            tEncoder.addBytes(xtaUpdate.mData, xtaUpdate.mDataLength)
            self.mUpdateCount += 1
            return True
        else:
            return False

    def getUpdates(self, connectionId:int) -> list:
        tRcvUpdates = []
        tDecoder = super().decode()

        tSeqno = tDecoder.getInt()
        self.mUpdateCount = tDecoder.getInt()

        for i in range( self.mUpdateCount ):
            tSubject:str = tDecoder.getString()
            tData:bytearray = tDecoder.getBytes()
            tRcvUpdates.append( RcvUpdate( connectionId=connectionId,
                                           subject=tSubject,
                                           updateData=tData,
                                           appId=super().mSegment.mHdrAppId))
        return tRcvUpdates

    def addLargeUpdateHeader(self, subject:str, dataSize:int ):
        tEncoder:Encoder = super().getEncoder()
        tEncoder.addString( subject )
        tEncoder.addBool( True )
        tEncoder.addInt( dataSize )
        self.mUpdateCount = 1

    def addLargeData(self, updateData:bytearray, updateDataOffset:int) -> int:
        tEncoder:Encoder = super().getEncoder()
        tDataLeft:int = len(updateData) - updateDataOffset
        tSize:int = min(tEncoder.getRemaining(), tDataLeft)

        # zap in raw data into the encoder byte buffer at the end of the encoder buffer
        tEncoder.addRaw( updateData[updateDataOffset : updateDataOffset + tSize ])
        return tSize # return size of the updateData transferred

    def readLargeDataHeader(self):
        tDecoder:Decoder = super.getDecoder();
        self.mLargeSubjectName = tDecoder.getString()
        tDecoder.readBoolean();
        self.mLargeMessageSize = tDecoder.getInt()

    def getLargeData(self, outBuffer:bytearray, offset:int ) -> int:
        tDecoder:Decoder = super().getDecoder()

        tBytesLeftToRead = len(outBuffer) - offset
        tBytesAvailable = tDecoder.getRemaning()
        tSize = min( tBytesAvailable, tBytesLeftToRead)
        outBuffer[:offset] = tDecoder.getRaw( tSize )
        return tSize # return size of bytes read from this segment

    def toString(self) -> str:
        sb = StringIO( super().toString())
        sb.write('\n    <updseqno: {} updcnt: {}>'.format( self.getSeqno(), self.mUpdateCount))
        return sb.getvalue()