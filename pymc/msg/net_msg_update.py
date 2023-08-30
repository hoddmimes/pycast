from __future__ import annotations
from pymc.aux.distributor_exception import DistributorException
from pymc.msg.codec import Encoder, Decoder
from pymc.aux.atomic import AtomicLong
from pymc.aux.aux import Aux
from pymc.msg.net_msg import NetMsg
from pymc.msg.rcv_update import RcvUpdate
from pymc.msg.segment import Segment
from pymc.msg.xta_update import XtaUpdate
from io import StringIO


class NetMsgUpdate(NetMsg):
    _seqno_stamp = AtomicLong(1)

    MIN_UPDATE_HEADER_SIZE = Segment.SEGMENT_HEADER_SIZE + 8  # segment-header-size + seqno:int + update-count:int

    def __init__(self, segment: Segment):
        super().__init__(segment)
        self._sequence_no: int = 0
        self._update_count: int = 0  # Number of updates in segment
        self._flush_sequence_number: int = 0
        self._create_time: int = Aux.currentMilliseconds()  # Time when the NetMessage was created

        self._large_subject_name: str = None
        self._large_message_size: int = 0

    def setHeader(self,
                  message_type: int,
                  segment_flags: int,
                  local_address: int,
                  sender_id: int,
                  sender_start_time_sec: int,
                  app_id: int):

        super().setHeader(message_type, segment_flags, local_address, sender_id, sender_start_time_sec, app_id)
        # now encode header
        _encoder: Encoder = super().encode()
        _encoder.addInt(self._sequence_no)  # placeholder for the sequence number
        _encoder.addInt(self._update_count)  # Placeholdet for the update count in this message

    @property
    def flush_seqno(self) -> int:
        return self._flush_sequence_number

    @flush_seqno.setter
    def flush_seqno(self, value: int):
        self._flush_sequence_number = value

    @property
    def large_subject_name(self) -> str:
        return self._large_subject_name

    @property
    def large_data_size(self) -> int:
        return self._large_message_size

    @property
    def min_update_header_size(self) -> int:
        return Segment.SEGMENT_HEADER_SIZE + 8  # Segment-header-size + (sequence number + update count )

    @property
    def sequence_no(self) -> int:
        return self._sequence_no

    @sequence_no.setter
    def sequence_no(self, value: int):
        if self._segment.decoder:
            raise DistributorException("must not update a read only message <sequence_no>")
        else:
            self._sequence_no = value
            self._segment.encoder.putIntAt(Segment.SEGMENT_HEADER_SIZE, value)

    @property
    def update_count(self) -> int:
        if self._segment.decoder:
            return self._segment.decoder.getIntAt(Segment.SEGMENT_HEADER_SIZE + 4)
        else:
            return self._segment.encoder.getIntAt(Segment.SEGMENT_HEADER_SIZE + 4)

    @update_count.setter
    def update_count(self, value: int):
        if self._segment.decoder:
            raise DistributorException("must not update a read only message <update_count>")
        else:
            self._update_count = value
            self._segment.encoder.putIntAt(Segment.SEGMENT_HEADER_SIZE + 4, value)

    @property
    def buffer(self):
        return super().encoder.buffer

    @property
    def create_time(self) -> int:
        return self._create_time

    def decode(self):
        _decoder: Decoder = super().decode()
        self._sequence_no = _decoder.getInt()
        self._update_count = _decoder.getInt()

    def encode(self):
        # Poke in the update count header in the header
        _encoder: Encoder = super().encode()
        _encoder.addInt(self._sequence_no)
        _encoder.addInt(self._update_count)

    def addUpdate(self, xta_update: XtaUpdate) -> bool:
        _encoder: Encoder = super().encoder
        if xta_update.size <= _encoder.remaining:
            _encoder.addString(xta_update.subject)
            _encoder.addBytes(xta_update.data, xta_update.data_length)
            self.update_count += 1
            return True
        else:
            return False

    def getUpdates(self, connection_id: int) -> list[RcvUpdate]:
        _rcv_updates = []
        _decoder = super().decode()

        self._sequence_no = _decoder.getInt()
        self._update_count = _decoder.getInt()

        for i in range(self._update_count):
            _subject: str = _decoder.getString()
            _data: bytearray = _decoder.getBytes()
            _rcv_updates.append(RcvUpdate(connection_id=connection_id,
                                          subject=_subject,
                                          update_data=_data,
                                          app_id=self._segment.hdr_app_id))
        return _rcv_updates

    def addLargeUpdateHeader(self, subject: str, data_size: int):
        _encoder: Encoder = super().encoder
        _encoder.addString(subject)
        _encoder.addBool(True)
        _encoder.addInt(data_size)
        self._update_count = 1

    def addLargeData(self, update_data: bytearray, update_data_offset: int) -> int:
        _encoder: Encoder = super().encoder
        _data_left: int = len(update_data) - update_data_offset
        _size: int = min(_encoder.remaining, _data_left)

        # zap in raw data into the encoder byte buffer at the end of the encoder buffer
        _encoder.addRaw(update_data[update_data_offset: update_data_offset + _size])
        return _size  # return size of the updateData transferred

    def readLargeDataHeader(self):
        _decoder: Decoder = super().decode()  # decode segment and return decoder
        self._sequence_no = _decoder.getInt()
        self._update_count = _decoder.getInt()

        self._large_subject_name = _decoder.getString()
        _decoder.getBool()  # yes, we should and will have a large message i.e. message present == True
        self._large_message_size = _decoder.getInt()  # Read large message size

    def getLargeData(self, out_buffer: bytearray, offset: int) -> int:
        _decoder: Decoder = super().decoder

        _bytes_left_to_read = len(out_buffer) - offset
        _bytes_available = _decoder.remaining
        _size = min(_bytes_available, _bytes_left_to_read)
        out_buffer[offset:offset + _size] = _decoder.getRaw(_size)
        return _size  # return size of bytes read from this segment

    def __str__(self) -> str:
        sb = StringIO(super().__str__())
        sb.write('\n    <updseqno: {} updcnt: {}>'.format(self._sequence_no, self._update_count))
        return sb.getvalue()
