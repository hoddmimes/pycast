from io import StringIO

from pymc.aux.aux import Aux
from pymc.msg.codec import Decoder, Encoder


class TestMessage(object):

    def __init__(self, *args):
        if len(args) == 2:
            self._seqno: int = int(args[0])
            self._time_stamp: int = Aux.current_milliseconds()
            self._data: bytes = bytes([65]) * int(args[1])
        else:
            self.decode(bytes(args[0]))

    def encode(self) -> bytes:
        _encoder = Encoder(len(self._data) + 16)
        _encoder.addInt(self._seqno)
        _encoder.addLong(self._time_stamp)
        _encoder.addBytes(self._data)
        return _encoder.buffer

    def decode(self, buffer: bytes):
        _decoder: Decoder = Decoder(buffer)
        self._seqno = _decoder.getInt()
        self._time_stamp = _decoder.getLong()
        self._data = _decoder.getBytes()

    @property
    def seqno(self) -> int:
        return self._seqno;

    def __str__(self):
        sb = StringIO()
        sb.write("sequence-number: {}".format(self._seqno))
        sb.write(" time: {}".format(Aux.time_string(self._time_stamp)))
        sb.write(" data_length: {}".format(len(self._data)))
        return sb.getvalue()
