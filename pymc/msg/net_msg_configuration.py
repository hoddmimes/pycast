from pymc.msg.codec import Encoder, Decoder
from pymc.msg.net_msg import NetMsg
from io import StringIO
from pymc.aux.aux import Aux

class NetMsgConfiguration(NetMsg):
    def __init__(self, segment):
        super().__init__(segment)
        self._mc_address: int = 0
        self._mc_port: int = 0
        self._hb_interval_ms: int = 0
        self._cfg_interval_ms: int = 0
        self._app_name: str = ''
        self._app_id: int = 0
        self._sender_id: int = 0
        self._host_address: int = 0
        self._sender_start_time_sec: int = 0

    def set(self, mc_addr:int, mc_port:int, sender_id:int, start_time_sec:int, heartbeat_interval:int, config_interval:int, host_addr:int, app_id: int, app_name:str):
        self._mc_address = mc_addr
        self._mc_port = mc_port
        self._hb_interval_ms = heartbeat_interval
        self._sender_start_time_sec = start_time_sec
        self._sender_id = sender_id
        self._cfg_interval_ms = config_interval
        self._host_address = host_addr
        self._app_name = app_name
        self._app_id = app_id



    def encode(self):
        super().encode()
        _encoder = super().encoder
        _encoder.addInt(self._mc_address)
        _encoder.addInt(self._mc_port)
        _encoder.addInt(self._sender_id)
        _encoder.addInt(self._sender_start_time_sec)
        _encoder.addInt(self._hb_interval_ms)
        _encoder.addInt(self._cfg_interval_ms)
        _encoder.addInt(self._host_address)
        _encoder.addInt(self._app_id)
        _encoder.addString(self._app_name)

    def decode(self):
        super().decode()
        _decoder = super().decoder
        self._mc_address = _decoder.getInt()
        self._mc_port = _decoder.getInt()
        self._sender_id = _decoder.getInt()
        self._sender_start_time_sec = _decoder.getInt()
        self._hb_interval_ms = _decoder.getInt()
        self._cfg_interval_ms = _decoder.getInt()
        self._host_address = _decoder.getInt()
        self._app_id = _decoder.getInt()
        self._app_name = _decoder.getString()

    @property
    def mc_address(self) -> int:
        return self._mc_address

    @property
    def mc_port(self) -> int:
        return self._mc_port

    @property
    def sender_id (self) -> int:
        return self._mc_port

    @property
    def send_start_time(self) -> int:
        return self._sender_start_time_sec

    @property
    def hb_interval_ms(self) -> int:
        return self._hb_interval_ms

    @property
    def cfg_interval_ms(self) -> int:
        return self._cfg_interval_ms

    @property
    def host_address(self) -> int:
        return self._host_address

    @property
    def app_id(self) -> int:
        return self._app_id

    @property
    def app_name(self) -> str:
        return self._app_name

    def __str__(self):
        sb = StringIO()
        sb.write(super().__str__())
        sb.write("\n    <")
        sb.write("MC Addr: {}".format(Aux.ip_addr_int_to_str(self.mc_address)))
        sb.write(" MC port: {}".format(self.mc_port))
        sb.write(" HB intval: {}".format(self.hb_interval_ms))
        sb.write(" CFG intval: {}".format(self.cfg_interval_ms))
        sb.write(" StartTime: {}".format(Aux.time_string(self.send_start_time)))
        sb.write(" SndrId: {0:x}".format(self.sender_id))
        sb.write(" Host: {}".format(Aux.ip_addr_int_to_str(self.host_address)))
        sb.write(" Appl: {}".format(self.app_name))
        sb.write(">")
        return "".join(sb)
