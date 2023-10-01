from io import StringIO
from threading import Thread
import re

from airium import Airium
from http.server import BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer

from pymc.aux.aux import Aux
from pymc.retransmission_statistics import NodeEntryOut, NodeEntryIn


def _add_style_() -> str:
    sb: StringIO = StringIO()
    sb.write("body{font-family: arial, serif;}\n")
    sb.write("table, th, td {border: 1px solid black; border-collapse: collapse;}\n")
    sb.write("th, td {padding-left:10px;padding-right:10px;}\n")
    a: Airium = Airium()
    with a.style():
        a.append(sb.getvalue())
    return str(a)


def _tab_tr_(*args, header: bool = False, center: bool = False, href: str = None):
    a: Airium = Airium()
    if center:
        style = 'style="text-align:center"'
    else:
        style = None

    if isinstance(args[0], list):
        _arr = args[0]
        with a.tr():
            for s in _arr:
                if header:
                    a.td(style, _t=str(s))
                else:
                    if href is None:
                        a.td(style, _t=str(s))
                    else:
                        with a.td(style):
                            a.a(href, _t=str(s))
    else:
        with a.tr():
            for i in range(len(args)):
                if header:
                    a.td(style, _t=str(args[i]))
                else:
                    if href is None:
                        a.td(style, _t=str(args[i]))
                    else:
                        with a.td(style):
                            a.a(href, _t=str(args[i]))
    return (str(a))


def _tab_distributor_attributes_(distributor: 'Distributor') -> str:
    from pymc.connection_controller import ConnectionController

    a: Airium = Airium()
    with a.div('style="margin-left:40px"'):
        with a.table():
            a.append(_tab_tr_("Application name", distributor.app_name))
            a.append(_tab_tr_("Start Time", distributor.start_time_string))
            a.append(_tab_tr_("Connections", str(ConnectionController.get_instance().connections)))
            a.append(_tab_tr_("Host Address", str(Aux.ip_addr_int_to_str(distributor.local_address))))
    return str(a)


def _tab_connections_attributes_(host_path: str) -> str:
    from pymc.connection_controller import ConnectionController
    a: Airium = Airium()
    with a.div('style="margin-left:40px"'):
        with a.table():
            a.append(_tab_tr_("MC Address", "MC Port", "Start Time", "Publisher", "Subscribers", "Remote Conn",
                              "Updates Out", "Updates In", "Retrans Out", "Retrans In", header=True, center=True))
            _conn_arr_arr = ConnectionController.get_instance().get_web_connection_attributes()
            for _conn_arr in _conn_arr_arr:
                a.append(_tab_tr_(_conn_arr, center=True,
                                  href=('href=' + host_path + 'CONNECTION/' + _conn_arr[0] + '/' + _conn_arr[1])))
    return str(a)


def _tab_remote_connections_attributes_() -> str:
    from pymc.connection_controller import ConnectionController
    a: Airium = Airium()
    with a.div('style="margin-left:40px"'):
        with a.table():
            a.append(
                _tab_tr_("MC Address", "MC Port", "Start Time", "Remote Addr", "Sequence #", header=True, center=True))
            _conn_arr_arr = ConnectionController.get_instance().get_web_remote_connection_attributes()
            for _conn_arr in _conn_arr_arr:
                a.append(_tab_tr_(_conn_arr, center=True))

    return str(a)


def _tab_retransmission_attributes_():
    from pymc.distributor import Distributor
    retrns_stat = Distributor.get_instance().retransmission_statistics

    a: Airium = Airium()
    with a.div('style="margin-left:40px"'):
        with a.table():
            a.append(_tab_tr_("Total Retransmission Updates Seen", str(retrns_stat.total_out_seen)))
            a.append(_tab_tr_("Total Retransmission Requests Seen", str(retrns_stat.total_in_seen)))

            a.append(_tab_tr_("Total Published Retransmission (by this app) ", str(retrns_stat.total_out_from_this_app)))
            a.append(_tab_tr_("Total Retransmission Requests (to this app)", str(retrns_stat.total_in_to_this_app)))

        _in_list: list[NodeEntryIn] = retrns_stat.get_sorted_in_entries

        if _in_list is not None and len(_in_list) > 0:
            with a.div('style="margin-left:60px"'):
                with a.h3():
                    a('Top Retransmission Requestors')
                with a.table():
                    a.append(_tab_tr_("Host Addr", "MC Address", "MC Port", "Requests", header=True, center=True))
                    for ne in _in_list:
                        a.append(_tab_tr_(ne.host_address_str, ne.mc_address_str, str(ne.mc_port),
                                          str(ne.retrans_to_this_node), center=True))

    return str(a)

def _tab_subscriptions_count_() -> list[str]:
    from pymc.connection_controller import ConnectionController
    a: Airium = Airium()
    with a.div('style="margin-left:40px"'):
        with a.table():
            a.append(_tab_tr_(ConnectionController.get_instance().web_get_subscription_count()))
    return(str(a))


def web_build_home(host_path: str) -> str:
    from pymc.distributor import Distributor
    a: Airium = Airium()
    a('<!DOCTYPE html>')
    with (a.html()):
        with a.head():
            a.append(_add_style_())
        with a.h1():
            a('Distributor')
        a.append(_tab_distributor_attributes_(Distributor.get_instance()))
        with a.div('style="margin-left:40px"'):
            with a.h1():
                a('Connections')
            a.append(_tab_connections_attributes_(host_path))
        with a.div('style="margin-left:40px"'):
            with a.h1():
                a('Remote Connections')
            a.append(_tab_remote_connections_attributes_())
        with a.div('style="margin-left:40px"'):
            with a.h1():
                a.a('href=' + host_path + "RETRANSMISSIONS", _t=str('Retransmissions'))
                #a('Retransmissions')
            a.append(_tab_retransmission_attributes_())
        with a.div('style="margin-left:40px"'):
            with a.h1():
                a.a('href=' + host_path + "SUBSCRIPTION", _t=str('Subscriptions'))
            a.append(_tab_subscriptions_count_())
    return str(a)


def _total_bytes_(tot_bytes: int) -> str:
    if tot_bytes < 1000:
        return str(tot_bytes).rjust(20, ' ') + " bytes"
    if tot_bytes < 1000000:
        f = tot_bytes / 1000.0
        return str(round(f, 1)).rjust(20, ' ') + " kb"
    f = tot_bytes / 1000000.0
    return str(round(f, 1)).rjust(20, ' ') + " mb"


def _web_connection_out_stat_(conn_stat: 'TrafficStatisticTimerTask'):
    a: Airium = Airium()
    from pymc.traffic_statistics import TrafficStatisticTimerTask
    stat: TrafficStatisticTimerTask = conn_stat

    with a.table():
        a.append(_tab_tr_(["Total messages", str(stat.xta_total_segments.get())]))
        a.append(_tab_tr_(["Total updates", str(stat.xta_total_user_updates.get())]))
        a.append(_tab_tr_(["Total bytes", _total_bytes_(stat.xta_total_bytes.get())]))
    a.br()
    with a.table():
        a.append(_tab_tr_(stat.xta_updates.to_web_table))
        a.append(_tab_tr_(stat.xta_msgs.to_web_table))
        a.append(_tab_tr_(stat.xta_bytes.to_web_table))
        a.append(_tab_tr_(stat.xta_bytes_1_min.to_web_table))
        a.append(_tab_tr_(stat.xta_msgs_1_min.to_web_table))
        a.append(_tab_tr_(stat.xta_updates_1_min.to_web_table))
        a.append(_tab_tr_(stat.xta_bytes_5_min.to_web_table))
        a.append(_tab_tr_(stat.xta_msgs_5_min.to_web_table))
        a.append(_tab_tr_(stat.xta_updates_5_min.to_web_table))
    return str(a)

def _web_connection_in_stat_(conn_stat: 'TrafficStatisticTimerTask'):
    a: Airium = Airium()
    from pymc.traffic_statistics import TrafficStatisticTimerTask
    stat: TrafficStatisticTimerTask = conn_stat

    with a.table():
        a.append(_tab_tr_(["Total messages", str(stat.rcv_total_segments.get())]))
        a.append(_tab_tr_(["Total updates", str(stat.rcv_total_user_updates.get())]))
        a.append(_tab_tr_(["Total bytes", _total_bytes_(stat.rcv_total_bytes.get())]))
    a.br()
    with a.table():
        a.append(_tab_tr_(stat.rcv_updates.to_web_table))
        a.append(_tab_tr_(stat.rcv_msgs.to_web_table))
        a.append(_tab_tr_(stat.rcv_bytes.to_web_table))
        a.append(_tab_tr_(stat.rcv_bytes_1_min.to_web_table))
        a.append(_tab_tr_(stat.rcv_msgs_1_min.to_web_table))
        a.append(_tab_tr_(stat.rcv_updates_1_min.to_web_table))
        a.append(_tab_tr_(stat.rcv_bytes_5_min.to_web_table))
        a.append(_tab_tr_(stat.rcv_msgs_5_min.to_web_table))
        a.append(_tab_tr_(stat.rcv_updates_5_min.to_web_table))

    return str(a)

def web_build_connection_subscription( mc_addr_str, mc_port_str):
    from pymc.connection_controller import ConnectionController

    _subscr_attr_list: list[str] = ConnectionController.get_instance().web_get_connection_subscriptions(mc_addr_str, mc_port_str)
    a: Airium = Airium()
    a('<!DOCTYPE html>')
    with (a.html()):
        with a.head():
            a.append(_add_style_())
        with a.h1():
            a('Connection Subscriptions')
        with a.div('style="margin-left:40px"'):
            with a.table():
                for _attr in _subscr_attr_list:
                    a.append(_tab_tr_(_attr))
        return str(a)

def web_build_retransmissions():
    from pymc.distributor import Distributor

    out_entries : list[NodeEntryOut] = Distributor.get_instance().retransmission_statistics.get_sorted_out_entries
    in_entries: list[NodeEntryIn] = Distributor.get_instance().retransmission_statistics.get_sorted_in_entries

    tot_in: int = Distributor.get_instance().retransmission_statistics.total_in_to_this_app
    tot_out: int = Distributor.get_instance().retransmission_statistics.total_out_from_this_app
    tot_in_seen: int = Distributor.get_instance().retransmission_statistics.total_in_seen
    tot_out_seen: int = Distributor.get_instance().retransmission_statistics.total_out_seen


    a: Airium = Airium()
    a('<!DOCTYPE html>')
    with (a.html()):
        with a.head():
            a.append(_add_style_())
        with a.h1():
            a('Retransmissions')
        with a.div('style="margin-left:40px"'):
            with a.table():
                a.append(_tab_tr_(['total retransmission requests to this application', tot_in], center=True))
                a.append(_tab_tr_(['total retransmission published by this application', tot_out], center=True))
                a.append(_tab_tr_(['total retransmission requests seen', tot_in_seen], center=True))
                a.append(_tab_tr_(['total retransmission published seen', tot_out_seen], center=True))
            a.br()
            with a.h3():
                a('In Requests')
            with a.table():
                a.append(_tab_tr_("Host", "MC Address", "MC Port", "Incoming Requests", header=True, center=True))
                for ne in in_entries:
                    a.append(
                        _tab_tr_(ne.web_in(), center=True))
            with a.h3():
                a('Out Requests')
            with a.table():
                a.append(_tab_tr_("Host", "MC Address", "MC Port", "Retrans Sent", header=True, center=True))
                for ne in out_entries:
                    a.append(
                        _tab_tr_(ne.web_out(), center=True))

        return str(a)

def web_build_all_subscriptions(host_path: str):
    from pymc.connection_controller import ConnectionController

    _conn_subscr_subj_attr = ConnectionController.get_instance().web_get_all_subscription()

    a: Airium = Airium()
    a('<!DOCTYPE html>')
    with (a.html()):
        with a.head():
            a.append(_add_style_())
        with a.h1():
            a('All ActiveSubscriptions')
        with a.div('style="margin-left:40px"'):
            with a.table():
                a.append(_tab_tr_("MC Address", "MC Port", "Subscription Path", header=True, center=True))
                for _conn_list in _conn_subscr_subj_attr:
                    for _subscr_list in _conn_list:
                        a.append(_tab_tr_(_subscr_list, center=True,href='href=' + host_path + 'CONNECT_SUBSCRIPTIONS/' + _subscr_list[0] + '/' + _subscr_list[1] ))
        return str(a)


def web_build_connection(mc_addr_str: str, mc_port_str: str):
    mc_addr = Aux.ip_addr_str_to_int(mc_addr_str)
    mc_port = int(mc_port_str)
    from pymc.connection_controller import ConnectionController
    from pymc.traffic_statistics import TrafficStatisticTimerTask
    conn_stat: TrafficStatisticTimerTask = ConnectionController.get_instance().get_web_connection_statistics_attributes(
        mc_addr, mc_port)

    _conn = ConnectionController.get_instance().find_connection(Aux.ip_addr_str_to_int(mc_addr_str), int(mc_port_str))

    a: Airium = Airium()
    a('<!DOCTYPE html>')
    with (a.html()):
        with a.head():
            a.append(_add_style_())
        with a.h1():
            a('Connection')
        with a.div('style="margin-left:40px"'):
            with a.table():
                a.append(_tab_tr_("Multicast Group Address", mc_addr_str))
                a.append(_tab_tr_("Multicast Group Port", mc_port_str))
                a.append(_tab_tr_("Start Time", Aux.time_string(_conn.start_time)))

        with a.div('style="margin-left:60px"'):
            with a.h3():
                a('Out Statistics')
            a.append(_web_connection_out_stat_(conn_stat))

            with a.h3():
                a('In Statistics')
            a.append(_web_connection_in_stat_(conn_stat))
    return str(a)


def distributor_web_handle(path: str, host_path: str) -> str:
    if path == '/' or path == '/HOME':
        return web_build_home(host_path)
    elif path == '/' or path == '/SUBSCRIPTION':
        return web_build_all_subscriptions(host_path)
    elif path == '/' or path == '/RETRANSMISSIONS':
        return web_build_retransmissions()
    elif re.search(r'^/CONNECTION/(\d+.\d+.\d+.\d+)/(\d+)$', path):
        x = re.search(r'^/CONNECTION/(\d+.\d+.\d+.\d+)/(\d+)$', path)
        return web_build_connection(x.group(1), x.group(2))
    elif re.search(r'^/CONNECT_SUBSCRIPTIONS/(\d+.\d+.\d+.\d+)/(\d+)$', path):
        x = re.search(r'^/CONNECT_SUBSCRIPTIONS/(\d+.\d+.\d+.\d+)/(\d+)$', path)
        return web_build_connection_subscription(x.group(1), x.group(2))
    else:
        return "Invalid request path"


class WebRequestHandle(BaseHTTPRequestHandler):

    def do_GET(self):
        host_path = 'http://' + self.headers.get('Host') + '/'
        response: str = distributor_web_handle(self.path.upper(), host_path)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(response, 'utf-8'))

    def do_POST(self):
        pass


class WebServer(Thread):

    def __init__(self, port: int):
        super().__init__()
        self._port = port
        self.start()

    def run(self):
        server = ThreadingHTTPServer(('', self._port), WebRequestHandle)
        server.serve_forever()
