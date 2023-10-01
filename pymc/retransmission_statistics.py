from abc import ABC

from pymc.aux.aux import Aux
from pymc.msg.generated.net_messages import DistExploreRetransmissonsRsp

'''
This module keeps statistics on incoming retransmission requests and re-sent updates i.e. out retransmissions.
There are two lists one for node entries requesting retransmissions (in_statistics) and one list for node entries that have published 
or re-sent updates marked retransmissions (out_statisticcs)

The IN statistics is updated when receiving NetMsgRetransmissionRqst messages. 
The OUT statistics is updated when receiving NetMsgUpdate (with message type equal to MSG_TYPE_RETRANSMISSION)
 
'''


class NodeEntry(ABC):
    def __init__(self, mc_address, mc_port, host_address):
        self._mc_address: int = mc_address
        self._mc_port: int = mc_port
        self._host_address: int = host_address

    @property
    def mc_address(self) -> int:
        return self._mc_address

    @property
    def mc_port(self) -> int:
        return self._mc_port

    @property
    def host_address(self) -> int:
        return self._host_address

    @property
    def mc_address_str(self) -> str:
        return Aux.ip_addr_int_to_str(self._mc_address)

    @property
    def host_address_str(self):
        return Aux.ip_addr_int_to_str(self._host_address)


class NodeEntryIn(NodeEntry):
    def __init__(self, mc_address: int, mc_port: int, host_address: int):
        super().__init__(mc_address, mc_port, host_address)
        self.retrans_to_this_node: int = 0  # in retransmission to this node and connection

    def web_in(self) -> list[str]:
        return [self.host_address_str, self.mc_address_str, str(self.mc_port), str(self.retrans_to_this_node)]

    def __str__(self):
        return ("host: {} mc-address; {} mc-port: {} retrans request in {}".
                format(self.host_address_str,
                       self.mc_address_str,
                       self.mc_port,
                       self.retrans_to_this_node))


class NodeEntryOut(NodeEntry):
    def __init__(self, mc_address: int, mc_port: int, host_address: int):
        super().__init__(mc_address, mc_port, host_address)
        self.retrans_sent_by_this_node: int = 0  # in retransmission to this node and connection

    def web_out(self) -> list[str]:
        return [self.host_address_str, self.mc_address_str, str(self.mc_port), str(self.retrans_sent_by_this_node)]

    def __str__(self):
        return ("host: {} mc-address; {} mc-port: {} Out retransmission sent {}".
                format(self.host_address_str,
                       self.mc_address_str,
                       self.mc_port,
                       self.retrans_sent_by_this_node))


def _get_key_(mc_address: int, mc_port: int, host_address: int) -> int:
    _key = (Aux.swap_int(mc_address) << 40) + (Aux.swap_int(host_address) << 16) + (Aux.swap_int(mc_port) & 0xffff)
    return _key


def _sort_out_nodes_(out_nodes: list[NodeEntryOut]) -> list[NodeEntryOut]:
    if not out_nodes:
        return []
    for j in range(len(out_nodes)):
        for i in range(1, len(out_nodes)):
            if out_nodes[i].retrans_sent_by_this_node > out_nodes[i - 1].retrans_sent_by_this_node:
                _tmp = out_nodes[i - 1]
                out_nodes[i - 1] = out_nodes[i]
                out_nodes[i] = _tmp
    return out_nodes


def _sort_in_nodes_(in_nodes: list[NodeEntryIn]) -> list[NodeEntryIn]:
    if not in_nodes:
        return []
    for j in range(len(in_nodes)):
        for i in range(1, len(in_nodes)):
            if in_nodes[i].retrans_to_this_node > in_nodes[i - 1].retrans_to_this_node:
                _tmp = in_nodes[i - 1]
                in_nodes[i - 1] = in_nodes[i]
                in_nodes[i] = _tmp
        return in_nodes


class RetransmissionStatistics(object):
    def __init__(self, local_host_address: int):
        self.out_statistics: dict[int, NodeEntryOut] = {}
        self.in_statistics: dict[int, NodeEntryIn] = {}
        self._total_in: int = 0  # Total retransmission requests address to this host
        self._total_out: int = 0  # Total retransmission sent by this distributor application
        self._total_in_seen: int = 0  # Total retransmission requests seen
        self._total_out_seen: int = 0  # Total retransmission updates seen
        self._local_host_address = local_host_address

    @property
    def total_in_to_this_app(self) -> int:
        return self._total_in

    @property
    def total_out_from_this_app(self) -> int:
        return self._total_out

    @property
    def total_in_seen(self) -> int:
        return self._total_in_seen

    @property
    def total_out_seen(self) -> int:
        return self._total_out_seen

    def get_in_entry(self, mc_address: int, mc_port: int, host_address: int) -> NodeEntryIn:
        _key = _get_key_(mc_address=mc_address, mc_port=mc_port, host_address=host_address)
        _entry = self.in_statistics.get(_key)
        if _entry is None:
            _entry = NodeEntryIn(mc_address, mc_port, host_address)
        return _entry

    def get_out_entry(self, mc_address: int, mc_port: int, host_address: int) -> NodeEntryOut:
        _key = _get_key_(mc_address=mc_address, mc_port=mc_port, host_address=host_address)
        _entry = self.out_statistics.get(_key)
        if _entry is None:
            _entry = NodeEntryOut(mc_address, mc_port, host_address)
        return _entry

    '''
    Invoked when an retransmission request is received
    '''

    def update_in_statistics(self, mc_address: int, mc_port: int, host_address: int, ):
        _key = _get_key_(mc_address=mc_address, mc_port=mc_port, host_address=host_address)
        _entry: NodeEntryIn = self.in_statistics.get(_key)
        if not _entry:
            _entry: NodeEntryIn = NodeEntryIn(mc_address, mc_port, host_address)
            self.in_statistics[_key] = _entry

        self._total_in_seen += 1
        _entry.retrans_to_this_node += 1
        if host_address == self._local_host_address:
            self._total_in += 1

    '''
    Invoked when this distributor have detected a gap and requests a retransmission
    from another distributor publishing the information
    '''

    def update_out_statistics(self, mc_address: int, mc_port: int, host_address: int):
        _key = _get_key_(mc_address, mc_port, host_address)
        _entry: NodeEntryOut = self.out_statistics.get(_key)
        if not _entry:
            _entry: NodeEntryOut = NodeEntryOut(mc_address, mc_port, host_address)
            self.out_statistics[_key] = _entry
        _entry.retrans_sent_by_this_node += 1
        self._total_out_seen += 1
        if host_address == self._local_host_address:
            self._total_out += 1

    @property
    def get_sorted_in_entries(self) -> list[NodeEntryIn]:
        _list = _sort_in_nodes_(self.in_statistics.values())
        return _list

    @property
    def get_sorted_out_entries(self) -> list[NodeEntryOut]:
        _list = _sort_out_nodes_(self.out_statistics.values())
        return _list
