from __future__ import annotations
from abc import ABC
from pymc.msg.codec import Encoder,Decoder
from io import StringIO
from pymc.aux.aux import Aux

class Segment(ABC):

    SEGMENT_HEADER_SIZE = 20
    # +---------------------------------+----------- +
    # | Protocol Version 			    |	  Byte 2 |
    # +---------------------------------+----------- +
    # | Message Type                    |     Byte 1 |
    # +---------------------------------+----------- +
    # | Message Flags                   |     Byte 1 |
    # +---------------------------------+----------- +
    # | Local Host Address              |     Byte 4 |
    # +---------------------------------+----------- +
    # | Sender Id                       |     Byte 4 |
    # +---------------------------------+----------- +
    # | Sender Start Time (sec)         |     Byte 4 |
    # +---------------------------------+----------- +
    # | Application Id 		    		|	  Byte 4 |
    # +---------------------------------+------------+

    MSG_TYPE_UPDATE = 1
    MSG_TYPE_RETRANSMISSION = 2
    MSG_TYPE_HEARTBEAT = 3
    MSG_TYPE_CONFIGURATION = 4
    MSG_TYPE_RETRANSMISSION_RQST = 5
    MSG_TYPE_RETRANSMISSION_NAK = 6

    FLAG_M_SEGMENT_START = 1
    FLAG_M_SEGMENT_MORE = 2
    FLAG_M_SEGMENT_END = 4

    def __init__(self, *args):

        if isinstance(args[0], int):
            # The parameter is an integer which indicates that the segment will be
            # to encode a Distributor message
            self.mSize:int = args[0]
            self.mEncoder:Encoder = Encoder( self.mSize )
            self.mDecoder:Decoder = None
        elif isinstance(args[0], bytearray):
            # The parameter is a bytearray which indicates that the segment will be
            # to decode an incoming message to the Distributor
            self.mEncoder:Encoder = None
            self.mDecoder.Decoder = Decoder( args[0] )
            self.mSize = 0

        self.mHashCodeValue:int = 0
        self.mSeqno:int = 0

        self.mHdrVersion:int = 0#short
        self.mHdrMsgType:int = 0 #byte
        self.mHdrSegmentFlags:int = 0# byte
        self.mHdrLocalAddress:int = 0 # int
        self.mHdrSenderId:int = 0
        self.mHdrSenderStartTime:int = 0
        self.mHdrAppId:int = 0

    def setHeaderMessageType(self, msg_type):
        self.mHdrMsgType = msg_type
        if self.mDecoder:
            self.mDecoder.putByteAt(2, msg_type)
        else:
            self.mEncoder.putByteAt(2, msg_type)

    def getHeaderMessageType(self) -> int:
        if self.mDecoder:
            return self.mDecoder.getByteAt(2)
        else:
            return self.mEncoder.getByteAt(2)

    def getLength(self) -> int:
        if self.mDecoder:
            self.mDecoder.getLength()
        else:
            self.mEncoder.getLength()
    def getFreeSpaceLeft(self) ->int:
        return self.mEncoder.getRemaining()

    def setHeader( self, headerVersion:int, messageType:int, segmentFlags:int,
                   localAddress:int, senderId:int, senderStartTime:int, appId:int):
        self.mHdrVersion = headerVersion
        self.mHdrMsgType = messageType
        self.mHdrSegmentFlags = segmentFlags
        self.mHdrLocalAddress = localAddress
        self.mHdrSenderId = senderId
        self.mHdrSenderStartTime = senderStartTime
        self.mHdrAppId = appId

    def setSeqno( self, seqno:int ):
        self.mSeqno = seqno;
        if self.mEncoder:
            self.mEncoder.putIntAt( Segment.SEGMENT_HEADER_SIZE, seqno)

    def getSeqno(self) -> int:
        return self.mSeqno

    def encode( self ):
        self.mEncoder.reset()
        self.mEncoder.addShort(self.mHdrVersion)
        self.mEncoder.addByte(self.mHdrMsgType)
        self.mEncoder.addByte(self.mHdrSegmentFlags)
        self.mEncoder.addInt(self.mHdrLocalAddress)
        self.mEncoder.addInt(self.mHdrSenderId)
        self.mEncoder.addInt(self.mHdrSenderStartTime)
        self.mEncoder.addInt(self.mHdrAppId)


    def decode(self):
        self.mDecoder.reset()
        self.mHdrVersion = self.mDecoder.readShort()
        self.mHdrMsgType = self.mDecoder.readByte()
        self.mHdrSegmentFlags = self.mDecoder.readByte()
        self.mHdrLocalAddress = self.mDecoder.readInt()
        self.mHdrSenderId = self.mDecoder.readInt()
        self.mHdrSenderStartTime = self.mDecoder.readInt()
        self.mHdrAppId = self.mDecoder.readInt()


    def getDecoder(self) -> Decoder:
        return self.mDecoder

    def getEncoder(self) -> Encoder:
        return self.mEncoder


    def copy(self) -> Segment:

        if self.mDecoder:
            _buffer = bytearray[ len(self.mDecoder._buffer) ]
            _buffer[:] = self.mDecoder._buffer
            _segment = Segment(_buffer)
            _segment.mDecoder._pos = self.mDecoder._pos
            _segment.mDecoder._size = self.mDecoder._size
        else:
            _segment = Segment( len(self.mEncoder._buffer))
            _segment.mEncoder._buffer[:] = self.mEncoder._buffer
            _segment.mEncoder._pos = self.mEncoder._pos
            _segment.mEncoder._size = self.mEncoder._size

        _segment.mHdrSegmentFlags = self.mHdrSegmentFlags
        _segment.mHdrMsgType = self.mHdrMsgType
        _segment.mSeqno = self.mSeqno
        _segment.mHdrAppId = self.mHdrAppId
        _segment.mSize = self.mSize
        _segment.mHdrVersion = self.mHdrVersion
        _segment.mHdrSenderId = self.mHdrSenderId
        _segment.mHdrSenderStartTime = self.mHdrSenderStartTime
        return _segment


    # =========================================================================================

    def isUpdateMessage(self) -> bool:
        if self.mHdrMsgType == Segment.MSG_TYPE_UPDATE or  self.mHdrMsgType == Segment.MSG_TYPE_RETRANSMISSION:
            return True
        else:
            return False

    def hashCode(self) -> int:
        if self.mHashCodeValue == 0:
            _addr = (self.mHdrLocalAddressmHdrLocalHost  & 0xFF000000) >> 24
            _sndrid = (self.mHdrSenderId & 0xFF) << 16
            _time = (self.mHdrSenderStartTime & 0xFFFF)
            self.mHashCodeValue = _addr + _sndrid + _time
        return self.mHashCodeValue

    def equals( self, segment:Segment) -> bool:
        if segment == self:
            return True

        if (self.mHdrLocalAddress == segment.mHdrLocalAddress and
                self.mHdrSenderId == segment.mHdrSenderId and
                self.mHdrSenderStartTime == segment.mHdrSenderStartTime):
            return True
        else:
            return False

    def getFlagsString(self) -> str:
        if self.mHdrSegmentFlags == 0:
            return 'None'

        _str = ''

        if (self.mHdrSegmentFlags & Segment.FLAG_M_SEGMENT_START) != 0:
            _str += 'START+'

        if (self.mHdrSegmentFlags & Segment.FLAG_M_SEGMENT_MORE) != 0:
            _str += 'MORE+'

        if (self.mHdrSegmentFlags & Segment.FLAG_M_SEGMENT_END) != 0:
            _str += 'END+'

        return _str[:-1]


    @staticmethod
    def getMessageTypeString(msg_type) -> str:
        if msg_type == Segment.MSG_TYPE_UPDATE:
            return 'UPDATE'
        if msg_type == Segment.MSG_TYPE_RETRANSMISSION:
            return 'RETRANSMISSION'
        if msg_type == Segment.MSG_TYPE_HEARTBEAT:
            return 'HEARTBEAT'
        if msg_type == Segment.MSG_TYPE_CONFIGURATION:
            return 'CONFIGURATION'
        if msg_type == Segment.MSG_TYPE_RETRANSMISSION_RQST:
            return 'RETRANSMISSION_RQST'
        if msg_type == Segment.MSG_TYPE_RETRANSMISSION_NAK:
            return 'RETRANSMISSION_NAK'

        return "unknown-message: {}".format( msg_type )

    def __str__(self) -> str:
        sb:StringIO = StringIO()
        sb.write('[ Type: {}'.format(self.getMessageTypeString(self.mHdrMsgType)))
        sb.write(' SndrId: {0:x}'.format( self.mHdrSenderId))
        sb.write(' Len: {}'.format( self.getLength()));
        sb.write(' Flgs: {}'.format(  self.getFlagsString() ));
        sb.write(' LclHst: {}'.format( Aux.ipAddrIntToStr( self.mHdrLocalAddress)));
        sb.write(' StartTime: {}'.format( Aux.timestampToStr(  self.mHdrSenderStartTime)));
        sb.write(' Vrs: {0:x}'.format( self.mHdrVersion));
        sb.write(' AppId: {0:x}'.format( self.mHdrAppId));


        if (self.mHdrMsgType == Segment.MSG_TYPE_UPDATE or
                self.mHdrMsgType == Segment.MSG_TYPE_RETRANSMISSION):

            _value:int = 0
            if self.mDecoder:
                sb.write(' Seqno: {}'.format( self.mDecoder.getIntAt( self.SEGMENT_HEADER_SIZE)))
                sb.write(' Updcnt: {}'.format(self.mDecoder.getIntAt(self.SEGMENT_HEADER_SIZE)))
            else:
                sb.write(' Seqno: {}'.format(  self.mEncoder.getIntAt( self.SEGMENT_HEADER_SIZE)))
                sb.write(' Updcnt: {}'.format( self.mEncoder.getIntAt( self.SEGMENT_HEADER_SIZE)))

            sb.write('] ')
            return sb.getvalue()
