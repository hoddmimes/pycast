from pymc.msg.net_msg import NetMsg
from pymc.msg.segment import Segment
from pymc.aux.aux import Aux
from io import StringIO


class NetMsgHeartbeat(NetMsg):
    def __init__(self, segment: Segment):
        super().__init__(segment)
        self._mc_address: int = 0
        self._mc_port: int = 0
        self._sender_id: int = 0
        self._sequence_no: int = 0

    def encode(self):
        super().encode()
        _encoder = super().encoder
        _encoder.addInt(self._mc_address)
        _encoder.addInt(self._mc_port)
        _encoder.addInt(self._sender_id)
        _encoder.addInt(self._sequence_no)

    def decode(self):
        super().decode()
        _decoder = super().decoder
        self._mc_address = _decoder.getInt()
        self._mc_port = _decoder.getInt()
        self._sender_id = _decoder.getInt()
        self._sequence_no = _decoder.getInt()

    def set(self, mc_addr: int, mc_port: int, sender_id: int, sequence_no: int):
        self._mc_address = mc_addr
        self._mc_port = mc_port
        self._sender_id = sender_id
        self._sequence_no = sequence_no

    @property
    def mc_address(self) -> int:
        return self._mc_address

    @property
    def mc_port(self) -> int:
        return self._mc_port

    @property
    def sender_id(self) -> int:
        return self._sender_id

    @property
    def sequence_no(self) -> int:
        return self._sequence_no

    def __str__(self):
        sb = StringIO()
        sb.write(super().__str__())
        sb.write("\n    <")
        sb.write("mc_addr: " + Aux.ip_addr_int_to_str(self._mc_address))
        sb.write(" mc_port: " + str(self._mc_port))
        sb.write(" sender_dd: " + hex(self._sender_id))
        sb.write(" sequence#: " + str(self._sequence_no))
        sb.write(">")
        return sb.getvalue()
