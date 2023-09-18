from __future__ import annotations
from abc import ABC

from pymc.aux.distributor_exception import DistributorException
from pymc.msg.codec import Encoder, Decoder
from io import StringIO
from pymc.aux.aux import Aux


class Segment(ABC, object):
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

    HDR_OFFSET_VERSION = 0
    HDR_OFFSET_MSG_TYPE = HDR_OFFSET_VERSION + 2
    HDR_OFFSET_MSG_FLAGS = HDR_OFFSET_MSG_TYPE + 1
    HDR_OFFSET_LOCAL_HOST_ADDR = HDR_OFFSET_MSG_FLAGS + 1
    HDR_OFFSET_SENDER_ID = HDR_OFFSET_LOCAL_HOST_ADDR + 4
    HDR_OFFSET_START_TIME = HDR_OFFSET_SENDER_ID + 4
    HDR_OFFSET_APPL_ID = HDR_OFFSET_START_TIME + 4
    SEGMENT_HEADER_SIZE = HDR_OFFSET_APPL_ID + 4

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
            self._size: int = args[0]
            self._encoder: Encoder = Encoder(self._size)
            self._decoder: Decoder = None
        elif isinstance(args[0], bytes) or isinstance(args[0], bytearray):
            # The parameter is a bytearray which indicates that the segment will be
            # to decode an incoming message to the Distributor
            self._encoder: Encoder = None
            self._decoder: Decoder = Decoder(args[0])
            self._size = len(args[0])

        self._hash_code_value: int = 0
        self._sequence_number: int = 0

        self._hdr_version: int = 0  # short
        self._hdr_msg_type: int = 0  # byte
        self._hdr_segment_flags: int = 0  # byte
        self._hdr_local_address: int = 0  # int
        self._hdr_sender_id: int = 0
        self._hdr_sender_start_time_sec: int = 0
        self._hdr_app_id: int = 0


    @property
    def length(self) -> int:
        if self._decoder:
            return self._decoder.length
        else:
            return self._encoder.length

    @property
    def allocate_size(self):
        return self._size

    @property
    def get_free_space_left(self) -> int:
        return self._encoder.remaining

    def setHeader(self, header_version: int, messsage_type: int, segment_flags: int,
                  local_address: int, sender_id: int, sender_start_time_sec: int, app_id: int):
        self._hdr_version = header_version
        self._hdr_msg_type = messsage_type
        self._hdr_segment_flags = segment_flags
        self._hdr_local_address = local_address
        self._hdr_sender_id = sender_id
        self._hdr_sender_start_time_sec = sender_start_time_sec
        self._hdr_app_id = app_id


    def encode(self):
        self.encoder.reset()
        self.encoder.addShort(self._hdr_version)
        self.encoder.addByte(self._hdr_msg_type)
        self.encoder.addByte(self._hdr_segment_flags)
        self.encoder.addInt(self._hdr_local_address)
        self.encoder.addInt(self._hdr_sender_id)
        self.encoder.addInt(self._hdr_sender_start_time_sec)
        self.encoder.addInt(self._hdr_app_id)

    def decode(self):
        self.decoder.reset()
        self._hdr_version = self.decoder.getShort()
        self._hdr_msg_type = self.decoder.getByte()
        self._hdr_segment_flags = self.decoder.getByte()
        self._hdr_local_address = self.decoder.getInt()
        self._hdr_sender_id = self.decoder.getInt()
        self._hdr_sender_start_time_sec = self.decoder.getInt()
        self._hdr_app_id = self._decoder.getInt()

    def clone_to_decoder(self):
        if self._decoder:
            raise DistributorException("can not clone a decode-segment to a decode-segment")
        _segment = Segment( self.encoder.buffer )
        return _segment

    @staticmethod
    def debug( segment: Segment):
        if segment._encoder:
            bytarr = segment._encoder.buffer
            dec = Decoder( bytarr )
            version = dec.getShort()
            msg_type = dec.getByte()
            msg_flags = dec.getByte()
            lcl_addr = dec.getInt()
            sndr_id = dec.getInt()
            start_time= dec.getInt()
            app_id = dec.getInt()
            print("[segment-dbg encode] version: {} type: {} flags:{} addr: {} sndrid: {} start-time: {} app_id: {}"
                  .format(version, msg_type, msg_flags, Aux.ip_addr_int_to_str(lcl_addr),
                          hex(sndr_id), Aux.time_string(start_time),hex(app_id)))
        else:
            print("[segment-dbg encode] None")

        if segment._decoder:
            bytarr = segment._decoder.buffer
            dec = Decoder(bytarr)
            version = dec.getShort()
            msg_type = dec.getByte()
            msg_flags = dec.getByte()
            lcl_addr = dec.getInt()
            sndr_id = dec.getInt()
            start_time = dec.getInt()
            app_id = dec.getInt()
            print("[segment-dbg decode] version: {} type: {} flags:{} addr: {} sndrid: {} start-time: {} app_id: {}"
                  .format(version, msg_type, msg_flags, Aux.ip_addr_int_to_str(lcl_addr),
                          hex(sndr_id), Aux.time_string(start_time), hex(app_id)))
        else:
            print("[segment-dbg decode] None")

    @property
    def hdr_version(self) -> int:
        return self._hdr_version

    @property
    def hdr_msg_type(self) -> int:
        return self._hdr_msg_type

    @hdr_msg_type.setter
    def hdr_msg_type(self, value:  int):
        self._hdr_msg_type = value

    @property
    def hdr_segment_flags(self) -> int:
        return self._hdr_segment_flags

    @hdr_segment_flags.setter
    def hdr_segment_flags(self, value:  int):
        self._hdr_segment_flags = value

    @property
    def hdr_local_address(self) -> int:
        return self._hdr_local_address


    @property
    def hdr_sender_id(self) -> int:
        return self._hdr_sender_id

    @property
    def hdr_sender_start_time_sec(self) -> int:
        return self._hdr_sender_start_time_sec

    @property
    def hdr_app_id(self) -> int:
        return self._hdr_app_id

    @property
    def decoder(self) -> Decoder | None:
        return self._decoder

    @property
    def encoder(self) -> Encoder | None:
        return self._encoder

    # =========================================================================================

    @property
    def is_update_message(self) -> bool:
        if self._hdr_msg_type == Segment.MSG_TYPE_UPDATE or self._hdr_msg_type == Segment.MSG_TYPE_RETRANSMISSION:
            return True
        else:
            return False

    @property
    def is_end_segment(self) -> bool:
        if self._hdr_segment_flags & Segment.FLAG_M_SEGMENT_END != 0:
            return True
        else:
            return False

    @property
    def is_start_segment(self) -> bool:
        if self._hdr_segment_flags & Segment.FLAG_M_SEGMENT_START != 0:
            return True
        else:
            return False
    @classmethod
    def cast(cls, obj: object) -> Segment:
        if isinstance( obj, Segment):
            return obj
        raise Exception('Can not cast object to {}'.format( cls.__name__))

    def __hash__(self):

        if self._hash_code_value == 0:
            _addr = (self._hdr_local_address & 0xFF000000) >> 24
            _sndrid = (self._hdr_sender_id & 0xFF) << 8
            _time = (self._hdr_sender_start_time_sec & 0xFFFF) << 16
            self._hash_code_value = _addr + _sndrid + _time
        return self._hash_code_value

    def __eq__(self, segment: Segment):
        if segment == self:
            return True

        if (self._hdr_local_address == segment._hdr_local_address and
                self._hdr_sender_id == segment._hdr_sender_id and
                self._hdr_sender_start_time_sec == segment._hdr_sender_start_time_sec):
            return True
        else:
            return False

    def _getFlagsString(self) -> str:
        if self._hdr_segment_flags == 0:
            return 'None'

        _str = ''

        if (self._hdr_segment_flags & Segment.FLAG_M_SEGMENT_START) != 0:
            _str += 'START+'

        if (self._hdr_segment_flags & Segment.FLAG_M_SEGMENT_MORE) != 0:
            _str += 'MORE+'

        if (self._hdr_segment_flags & Segment.FLAG_M_SEGMENT_END) != 0:
            _str += 'END+'

        return _str[:-1]

    """
    this is not pretty :-) but since we have added a circuit breaker and of cause 
    use the property insight manner it will work and do the jobb :-)  
    """
    @property
    def seqno(self) -> int:
        if self._hdr_msg_type == Segment.MSG_TYPE_UPDATE or self._hdr_msg_type == Segment.MSG_TYPE_RETRANSMISSION:
            if self._decoder:
                return self._decoder.getIntAt(self.SEGMENT_HEADER_SIZE)
            else:
                return self._encoder.getIntAt(self.SEGMENT_HEADER_SIZE)
        raise DistributorException("used property 'seqno' for a none update message, can not beleive we did that :-)")

    def update_count(self) -> int:
        if self._hdr_msg_type == Segment.MSG_TYPE_UPDATE or self._hdr_msg_type == Segment.MSG_TYPE_RETRANSMISSION:
            if self._decoder:
                return self._decoder.getIntAt(self.SEGMENT_HEADER_SIZE + 4)
            else:
                return self._encoder.getIntAt(self.SEGMENT_HEADER_SIZE + 4)
        raise DistributorException("used property 'update_count' for a none update message, can not beleive we did that :-)")

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

        return "unknown-message: {}".format(msg_type)

    def __str__(self) -> str:
        sb: StringIO = StringIO()
        sb.write('[ Type: {}'.format(self.getMessageTypeString(self._hdr_msg_type)))
        sb.write(' SndrId: {0:x}'.format(self._hdr_sender_id))
        sb.write(' Len: {}'.format(self.length))
        sb.write(' Flgs: {}'.format(self._getFlagsString()))
        sb.write(' LclHst: {}'.format(Aux.ip_addr_int_to_str(self._hdr_local_address)))
        sb.write(' StartTime: {}'.format(Aux.time_string(self._hdr_sender_start_time_sec)))
        sb.write(' Vrs: {0:x}'.format(self._hdr_version))
        sb.write(' AppId: {0:x}'.format(self._hdr_app_id))

        if self._hdr_msg_type == Segment.MSG_TYPE_UPDATE or self._hdr_msg_type == Segment.MSG_TYPE_RETRANSMISSION:
            _value: int = 0
            if self._decoder:
                sb.write(' Seqno: {}'.format(self._decoder.getIntAt(self.SEGMENT_HEADER_SIZE)))
                sb.write(' Updcnt: {}'.format(self._decoder.getIntAt(self.SEGMENT_HEADER_SIZE+4)))
            else:
                sb.write(' Seqno: {}'.format(self._decoder.getIntAt(self.SEGMENT_HEADER_SIZE)))
                sb.write(' Updcnt: {}'.format(self._decoder.getIntAt(self.SEGMENT_HEADER_SIZE+4)))

        sb.write('] ')
        return sb.getvalue()


