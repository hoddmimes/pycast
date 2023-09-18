from __future__ import annotations
from pymc.aux.aux import Aux
from pymc.aux.distributor_exception import DistributorException
from pymc.msg.segment import Segment


class RetransQueItm(object):
    def __init__(self, segment: Segment, sequence_no: int):
        self._queue_time_sec: int = Aux.current_seconds()
        self._segment: Segment = segment
        self._seqno: int = sequence_no
        self._in_progress: bool = False
        self._resent_count: int = 0
        self._cache_size: int = 0
        self._segment.hdr_msg_type = Segment.MSG_TYPE_RETRANSMISSION

    @classmethod
    def cast(cls, obj) -> RetransQueItm:
        if isinstance(obj, RetransQueItm):
            return obj
        else:
            raise DistributorException('object is not an instance of RetransQueItm')

    @property
    def segment(self) -> Segment:
        return self._segment
    @segment.setter
    def segment(self, value: Segment):
        self._segment = value

    @property
    def seqno(self):
        return self._seqno

    @property
    def in_progress(self):
        return self._in_progress

    @property
    def resent_count(self):
        return self._resent_count

    @property
    def queue_time_sec(self):
        return self._queue_time_sec

    @property
    def cache_size(self):
        return self._cache_size
