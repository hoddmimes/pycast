from __future__ import annotations


class XtaUpdate(object):

    def __init__(self, subject: str, data: bytearray, length: int = None):
        self._subject = subject
        if length == None:
            self._data = data
            self._data_length = len(data)
        else:
            self._data = data[:length]
            self._data_length = length

    # XtaUpdate encoded layout
    # 1 byte subject present or not
    # 4 bytes subject length
    # 'n' bytes subject data
    # 1 byte update present or not
    # 4 bytes update data length
    # 'n' bytes update payload

    @property
    def size(self) -> int:
        return len(self._subject) + (1 + 4 + 1 + 4) + self._data_length

    @property
    def data_length(self) -> int:
        return self._data_length

    @property
    def subject(self) -> str:
        return self._subject

    @property
    def data(self) -> bytearray:
        return self._data

    @classmethod
    def cast(cls, obj: object) -> XtaUpdate:
        if isinstance(obj, XtaUpdate):
            return obj
        raise Exception('Can not cast object to {}'.format(cls.__name__))
