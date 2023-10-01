import socket
from pymc.msg.segment import Segment
from pymc.msg.net_msg import NetMsg
from pymc.aux.aux import Aux
from io import StringIO


##=================================================================
##  NetMsgRetransmissionRqst
##=================================================================
class NetMsgRetransmissionRqst(NetMsg):
    def __init__(self, segment):
        super().__init__(segment)
        self._app_name: str = ''
        self._requestor_host_name: str = ''
        self._requestor_host_addr: int = 0
        self._low_seqno: int = 0
        self._high_seqno: int = 0
        self._sender_id: int = 0
        self._sender_start_time_ms: int = 0

    def set(self, requestor_addr: int, low_seqno: int, high_seqno: int, host_name: str, appl_name: str,
            remote_sender_id: int, remote_sender_start_time_ms: int):

        self._requestor_host_addr = requestor_addr
        self._low_seqno = low_seqno
        self._high_seqno = high_seqno
        self._requestor_host_name = host_name
        self._app_name = appl_name
        self._sender_id = remote_sender_id
        self._sender_start_time_ms = remote_sender_start_time_ms

    @property
    def requestor_host_addr(self) -> int:
        return self._requestor_host_addr

    @property
    def low_sequence_no(self) -> int:
        return self._low_seqno

    @property
    def high_sequence_no(self) -> int:
        return self._high_seqno

    @property
    def requestor_host_name(self) -> str:
        return self._requestor_host_name
    @property
    def app_name(self) -> str:
        return self._app_name
    @property
    def sender_id(self) -> int:
        return self._sender_id

    @property
    def sender_start_time(self) -> int:
        return self._sender_start_time_ms

    def encode(self):
        super().encode()
        _encoder = super().encoder
        _encoder.addInt(self._requestor_host_addr)
        _encoder.addInt(self._sender_id)
        _encoder.addLong(self._sender_start_time_ms)
        _encoder.addInt(self._low_seqno)
        _encoder.addInt(self._high_seqno)
        _encoder.addString(self._requestor_host_name)
        _encoder.addString(self._app_name)

    def decode(self):
        super().decode()
        _decoder = super().decoder
        self._requestor_host_addr = _decoder.getInt()
        self._sender_id = _decoder.getInt()
        self._sender_start_time_ms = _decoder.getLong()
        self._low_seqno = _decoder.getInt()
        self._high_seqno = _decoder.getInt()
        self._requestor_host_name = _decoder.getString()
        self._app_name = _decoder.getString()



    def __str__(self):
        sb = StringIO()
        sb.write(super().__str__())
        sb.write("\n    <")
        sb.write("Rqstr addr: " + Aux.ip_addr_int_to_str(self.requestor_host_addr))
        sb.write(" Rqstr appl name: " + self.app_name)
        sb.write(" SndrId: " + hex(self.sender_id))
        sb.write(" StartTime: " + Aux.time_string(self.sender_start_time))
        sb.write(" Seqno Lo: " + str(self.low_sequence_no))
        sb.write(" Seqno Hi: " + str(self.high_sequence_no))
        sb.write(">")
        return sb.getvalue()

##=================================================================
##  NetMsgRetransmissionNAK
##=================================================================
class NetMsgRetransmissionNAK(NetMsg):
    def __init__(self, segment):
        super().__init__(segment)
        self._mc_address: int = 0
        self._mc_port: int = 0
        self._sender_id: int = 0
        self._nak_sequence_no: list[int] = []

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
    def nak_sequence_numbers(self) -> list[int]:
        return self._nak_sequence_no

    def encode(self):
        super().encode()
        _encoder = super().encoder
        _encoder.addInt(self.mc_address)
        _encoder.addInt(self.mc_port)
        _encoder.addInt(self.sender_id)
        _encoder.addInt(len(self._nak_sequence_no))
        for i in range(len(self._nak_sequence_no)):
            _encoder.addInt(self._nak_sequence_no[i])

    def decode(self):
        super().decode()
        _decoder = self.decoder
        self._mc_address = _decoder.getInt()
        self._mc_port = _decoder.getInt()
        self._sender_id = _decoder.getInt()
        _elements = _decoder.getInt()
        self._nak_sequence_no.clear()
        for i in range(_elements):
            self._nak_sequence_no.append(_decoder.getInt())

    def set(self, mc_addr:int, mc_port:int, sender_id:int):
        self._mc_address = mc_addr
        self._mc_port = mc_port
        self._sender_id = sender_id


    def setNakSeqNo(self, nak_list:list[int]):
        self._nak_sequence_no.clear()
        self._nak_sequence_no.extend(nak_list)

    def __str__(self):
        sb = StringIO()
        sb.write(super().__str__())
        sb.write("\n    <")
        sb.write("MC addr: " + str(self.mc_address))
        sb.write(" MC port: " + str(self.mc_port))
        sb.write(" SndrId: " + hex(self.sender_id))
        sb.write(" NAK count: " + str(len(self.nak_sequence_numbers)))
        sb.write(" NAKSeqno:  ")
        for i in range(len(self.nak_sequence_numbers)):
            sb.write(str(self.nak_sequence_numbers[i]) + ", ")
        sb.truncate(len(sb.getvalue()) - 2) ## truncate the last two char i.e. ', '
        sb.append(">")
        return sb.getvalue()