from __future__ import annotations
from pymc.aux.trace import Trace

class XtaUpdate(object):

    def __init__(self, subject: str, data: bytes, trace_context: Trace = None):
        self._subject: str = subject
        self._data: bytes = data
        self._trace_cntx = trace_context



    # XtaUpdate encoded layout
    # 1 byte subject present or not
    # 4 bytes subject length
    # 'n' bytes subject data
    # 1 byte update present or not
    # 4 bytes update data length
    # 'n' bytes update payload

    @property
    def size(self) -> int:
        return len(self._subject) + (1 + 4 + 1 + 4) + len(self._data)

    @property
    def data_length(self) -> int:
        return len(self._data)

    @property
    def subject(self) -> str:
        return self._subject

    @property
    def data(self) -> bytes:
        return self._data

    @property
    def trace_context(self) -> Trace:
        return self._trace_cntx

    @classmethod
    def cast(cls, obj: object) -> XtaUpdate:
        if isinstance(obj, XtaUpdate):
            return obj
        raise Exception('Can not cast object to {}'.format(cls.__name__))
