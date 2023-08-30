from __future__ import annotations
from io import StringIO


class RcvUpdate(object):

    def __init__(self, connection_id:int, subject:str, update_data:bytearray, app_id:int):
        self._update_data: bytearray = update_data
        self._subject_name: str = subject
        self._app_id: int = app_id
        self._connection_id: int = connection_id

    @property
    def size(self) -> int:
        return len(self._subject_name) + 8 + len(self._update_data)

    @property
    def data(self) -> bytearray:
        return self._update_data

    @property
    def subject(self) -> str:
        return self._subject_name

    @property
    def app_ip(self):
        return self._app_id

    @property
    def connection_id(self):
        return self._connection_id
    def __str__(self):
        sb: StringIO = StringIO()
        sb.write(" subject: {}".format(self.subject))
        sb.write(" app_id: {0:x}".format(self.app_ip))
        sb.write(" conn_id: {}".format(self.connection_id))
        sb.write(" data_len: {}".format(len(self.data)))
        return sb.getvalue()

    @classmethod
    def cast(cls, obj: object) -> RcvUpdate:
        if isinstance( obj, RcvUpdate):
            return obj
        raise Exception('Can not cast object to {}'.format( cls.__name__))