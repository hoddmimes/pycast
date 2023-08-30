from pymc.msg.segment import Segment
from pymc.msg.net_msg_update import NetMsgUpdate
from pymc.msg.rcv_update import RcvUpdate
from pymc.aux.distributor_exception import DistributorException


class RcvSegment(Segment):
    OFFSET_SEQUENCE_NO = Segment.SEGMENT_HEADER_SIZE
    OFFSET_UPDATE_COUNT = OFFSET_SEQUENCE_NO + 4

    def __init__(self, buffer):
        super().__init__(buffer)
        self._from_address: int = 0
        self._from_port: int = 0

    @property
    def isStartSegment(self) -> bool:
        if (self.hdr_segment_flags & Segment.FLAG_M_SEGMENT_START) != 0:
            return True
        else:
            return False

    @property
    def isEndSegment(self) -> bool:
        if (self.hdr_segment_flags & Segment.FLAG_M_SEGMENT_END) != 0:
            return True
        else:
            return False

    @property
    def from_address(self) -> int:
        return self._from_address

    @from_address.setter
    def from_address(self, value: int):
        self._from_address = value

    @property
    def from_port(self) -> int:
        return self._from_port

    @from_port.setter
    def from_port(self, value: int):
        self._from_port = value

    @property
    def sequence_no(self) -> int:
        if self.hdr_msg_type == Segment.MSG_TYPE_UPDATE or self.hdr_msg_type == Segment.MSG_TYPE_RETRANSMISSION:
            if self.encoder is None:
                return self.decoder.getIntAt(self.OFFSET_SEQUENCE_NO)
            else:
                return self.decoder.getIntAt(self.OFFSET_SEQUENCE_NO)

        raise DistributorException(
            "Can not extract sequence number from a none update/retransmission message, message ")

    def setFrom(self, from_addr: int, from_port: int):
        self._from_port = from_port
        self._from_address = from_addr


class RcvSegmentBatch(object):

    def __init__(self, first_segment_in_batch: RcvSegment = None):
        if first_segment_in_batch != None:
            self._list: list[RcvSegment] = [first_segment_in_batch]
        else:
            self._list: list[RcvSegment] = []

    def addSegment(self, rcv_segment: RcvSegment):
        self._list.append(rcv_segment)

    def getUpdates(self, connection_id: int) -> list[RcvUpdate]:
        _msg: NetMsgUpdate = NetMsgUpdate(self._list[0])
        _msg.decode()
        if len(self._list) == 1:  # If just one segment it is not a large message splited into multiple segments
            return _msg.getUpdates(connection_id)

        # Assemble large message
        _msg.readLargeDataHeader()
        _updates: list[RcvUpdate] = []

        _subject = _msg.large_subject_name
        _data: bytearray = bytearray(_msg.large_data_size)

        _offset = 0
        _offset = _msg.getLargeData(_data, _offset)
        for i in range(1, len(self._list)):
            _msg: NetMsgUpdate = NetMsgUpdate(self._list[i])
            _msg.decode()
            _offset = _msg.getLargeData(_data, _offset)

        _updates.append(RcvUpdate(connection_id, _subject, _data, _msg.hdr_app_id))
        return _updates
