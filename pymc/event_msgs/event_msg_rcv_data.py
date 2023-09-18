from __future__ import annotations
from pymc.aux.aux import Aux
from pymc.aux.distributor_exception import DistributorException
from pymc.event_loop import ConnectionEvent
from pymc.msg.segment import Segment


class EventMsgInboundMessage(ConnectionEvent):

    def __init__(self, data: bytes, mc_address_string: str, mc_port: int):
        super().__init__(ConnectionEvent.NET_MESSAGE)
        self._data = data
        self._mc_address_string = mc_address_string
        self._mc_address = Aux.ip_addr_str_to_int(mc_address_string)
        self._mc_port = mc_port

    @property
    def mc_address(self) -> int:
        return self._mc_address

    @property
    def mc_address_string(self) -> str:
        return self._mc_address_string

    @property
    def mc_port(self) -> int:
        return self._mc_port

    @property
    def data(self) -> bytes:
        return self._data

    def __str__(self):
        msg_type: str = Segment.getMessageTypeString(self.data[Segment.HDR_OFFSET_MSG_TYPE])
        return ("adress: {} port: {} msg_type: {} length: {}".
                format(self.mc_address_string,
                       self.mc_port,
                       msg_type,
                       len(self.data)))
