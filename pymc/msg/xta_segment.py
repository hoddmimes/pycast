from __future__ import annotations
from pymc.msg.segment import Segment

class XtaSegment(Segment):

    def __init__(self, bufferSize:int):
        super().__init__( bufferSize )
        self._allocated_buffer_size = bufferSize

    @property
    def size(self) -> int:
        return self.length

    @property
    def buffer_allocation_size(self) -> int:
        return self._allocated_buffer_size

    @classmethod
    def cast(cls, obj: object) -> XtaSegment:
        if isinstance( obj, XtaSegment):
            return obj
        raise Exception('Can not cast object to {}'.format( cls.__name__))