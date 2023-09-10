import socket

from pymc.aux.aux import Aux
from pymc.msg.generated.net_messages import DistExploreRetransmissonsRsp


class NodeEntry:
    def __init__(self, mc_address, mc_port, host_address):
        self.mc_address_str: str = Aux.ip_addr_int_to_str(mc_address)
        self.mc_port: int = mc_port
        self.host_address_str: str = Aux.ip_addr_int_to_str(host_address)
        self.to_this_node_count: int = 0
        self.to_remote_node_count: int = 0
        self.total_retransmission_seen: int = 0
        self.total_retransmission_out: int = 0

    def toOutString(self):
        return ("Host: {} number of outgoing retransmissions {} (total retransmissions served {})".
                format(self.host_address_str, self.to_remote_node_count, self.total_retransmission_out))

    def toInString(self):
        return ("Host: {} seen retransmissions requests {} (total retransmission requests in) {}".
                format(self.host_address_str, self.to_remote_node_count, self.total_retransmission_out))


def get_key(mc_address: int, mc_port: int, host_address: int) -> int:
    _key = (Aux.swap_int(mc_address) << 40) + (Aux.swap_int(host_address) << 16) + (Aux.swap_int(mc_port) & 0xffff)
    return _key


def sortOutNodes(out_nodes: list[NodeEntry]) -> list[NodeEntry] | None:
    if not out_nodes:
        return None
    for j in range(len(out_nodes)):
        for i in range(1, len(out_nodes)):
            if out_nodes[i].total_retransmission_out > out_nodes[i - 1].total_retransmission_out:
                _tmp = out_nodes[i - 1]
                out_nodes[i - 1] = out_nodes[i]
                out_nodes[i] = _tmp
    return out_nodes


def sortInNodes(in_nodes: list[NodeEntry]) -> list[NodeEntry] | None:
    if not in_nodes:
        return None
    for j in range(len(in_nodes)):
        for i in range(1, len(in_nodes)):
            if in_nodes[i].to_this_node_count > in_nodes[i - 1].to_this_node_count:
                _tmp = in_nodes[i - 1]
                in_nodes[i - 1] = in_nodes[i]
                in_nodes[i] = _tmp
        return in_nodes


class RetransmissionStatistics:
    def __init__(self):
        self.out_statistics: dict[int, NodeEntry] = {}
        self.in_statistics: dict[int, NodeEntry] = {}
        self.total_in: int = 0
        self.total_out: int = 0
        self.total_seen: int = 0

    def getRetransmissonsInfo(self):
        _rsp = DistExploreRetransmissonsRsp()
        _rsp.set_total_in_rqst(self.total_in)
        _rsp.set_total_out_rqst(self.total_out)
        _rsp.set_total_seen_rqst(self.total_seen)
        _in_nodes = list(self.in_statistics.values())
        if _in_nodes:
            sortInNodes(_in_nodes)
            _in_node_array = []
            for _node in _in_nodes:
                _in_node_array.append(_node.toInString())
            _rsp.set_in_hosts(_in_node_array)
        else:
            _rsp.set_in_hosts([])
        _out_nodes = list(self.out_statistics.values())
        if _out_nodes:
            _out_nodes = sortOutNodes(_out_nodes)
            _out_node_array = []
            for _node in _out_nodes:
                _out_node_array.append(_node.toOutString())
            _rsp.set_out_hosts(_out_node_array)
        else:
            _rsp.set_out_hosts([])
        return _rsp

    def update_in_statistics(self, mc_address: int, mc_port: int, host_address: int, to_this_application: bool):
        _key = get_key(mc_address=mc_address, mc_port=mc_port, host_address=host_address)
        _entry = self.in_statistics.get(_key)
        if not _entry:
            _entry = NodeEntry(mc_address, mc_port, host_address)
            self.in_statistics[_key] = _entry
        self.total_seen += 1
        _entry.total_retransmission_seen += 1
        if to_this_application:
            self.total_in += 1
            _entry.to_this_node_count += 1
        else:
            self.total_out += 1
            _entry.to_remote_node_count += 1

    def update_out_statistics(self, mc_address: int, mc_port: int, host_address: int):
        _key = get_key(mc_address, mc_port, host_address)
        _entry = self.out_statistics.get(_key)
        if not _entry:
            _entry = NodeEntry(mc_address, mc_port, host_address)
            self.out_statistics[_key] = _entry
        _entry.total_retransmission_out += 1
        self.total_in += 1
