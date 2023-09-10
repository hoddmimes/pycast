from __future__ import annotations
import logging
import threading

from pymc.distributor_configuration import DistributorLogFlags
from pymc.aux.aux import Aux
from pymc.client_controller import ClientDeliveryController
from pymc.connection_configuration import ConnectionConfiguration
from pymc.connection_timer_task import ConnectionTimerTask
from pymc.distributor_events import DistributorNaggingErrorEvent, DistributorRetransmissionNAKErrorEvent, \
    DistributorTooManyRetransmissionRetriesErrorEvent
from pymc.msg.net_msg_retransmission import NetMsgRetransmissionRqst, NetMsgRetransmissionNAK
from pymc.msg.segment import Segment
from pymc.msg.xta_segment import XtaSegment

'''
    This class will monitor itself as a subscriber i.e. it will monitor number of retransmissions 
    being generated by this application. If generating retransmission too frequently it will be considered 
    as a nagging subscriber and the connection should be closed. Whatever the connection should automatically 
    be closed or closed by the distributor application logic is something to be considered. 
    Currently the distributor application is just notified.
'''


class NaggingMonitorTask(ConnectionTimerTask):
    def __init__(self, connection_id: int, configuration: ConnectionConfiguration):
        super().__init__(connection_id)
        self._interval_count: int = 0
        self._last_interval_count: int = 0
        self._consecutive_ticks: int = 0
        self._cfg_window_interval: int = configuration.nagging_window_interval_ms()
        self._cfg_check_interval: int = configuration.nagging_check_interval_ms
        self._cfg_max_retransmissions: int = configuration.nagging_max_retransmit()

    def clear(self):
        self._interval_count = 0
        self._last_interval_count = 0
        self._consecutive_ticks = 0

    def increment_outgoing_retransmission_requests(self, count: int = 1):
        self._interval_count += count

    '''
    This method is called periodically to monitor how frequently we are 
    generating outgoing retransmission requests.
    '''

    def execute(self, connection: 'Connection'):
        try:
            # check if we have generated any new retransmission requests lately, if not reset
            if self._interval_count > self._last_interval_count:
                # increment number of intervals for which retransmissions has been generated
                self._consecutive_ticks += self._cfg_window_interval
                # If there has been retransmissions during all intervals or an excessive number of retransmission during one interval
                # then notify the upper application logic,
                if self._consecutive_ticks >= self._cfg_check_interval:
                    #
                    if self._cfg_max_retransmissions == 0 or (self._cfg_max_retransmissions <= self._interval_count):
                        _event = DistributorNaggingErrorEvent(connection.mIpmg.mInetAddress, connection.mIpmg.mPort)
                        ClientDeliveryController.get_instance().queue_event(connection.connection_id, _event)
                    self.clear()
            else:
                self.clear()
        except Exception as e:
            connection.log_exception(e)

class RetransmissionRequestItem(ConnectionTimerTask):
    def __init__(self, connection_id: int, remote_connection_id: int, low_seqno: int, high_seqno: int):
        super().__init__()
        self._connectio_id: int = connection_id
        self._remote_connection_id: int = remote_connection_id
        self._low_seqno: int = low_seqno
        self._high_seqno: int = high_seqno
        self._retrans_item_count = high_seqno - low_seqno + 1
        self._retries: int = 0
        self._served_list: list[int] = []

    def queue_retransmission_rqst_message(self, connection: 'Connection', remote_connection: 'RemoteConnection'):
        from pymc.distributor import Distributor
        _rqst_msg: NetMsgRetransmissionRqst = NetMsgRetransmissionRqst(
            XtaSegment(connection.configuration.small_segment_size))
        _rqst_msg.setHeader(message_type=Segment.MSG_TYPE_RETRANSMISSION_RQST,
                            segment_flags=Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END,
                            local_address=connection.local_address,
                            sender_id=connection.connection_sender.sender_id,
                            sender_start_time_sec=connection.connection_sender.sender_start_time,
                            app_id=Distributor.get_instance().app_id)
        _rqst_msg.set(requestor_addr=connection.local_address,
                      low_seqno=self._low_seqno,
                      high_seqno=self._high_seqno,
                      host_name=Aux.ip_addr_int_to_str(connection.local_address),
                      appl_name=Distributor.get_instance().app_name,
                      sender_id=remote_connection.remote_sender_id,
                      sender_start_time_ms=remote_connection.remote_start_time)

        connection.retransmission_statistics.update_out_statistics(mc_address=connection.mc_address,
                                                                   mc_port=connection.mc_port,
                                                                   host_address=remote_connection.remote_host_address)

        _rqst_msg.encode()
        connection.connection_sender.send_segment(_rqst_msg._segment)

    '''
    Invoked when a requested retransmission could not be served by a remote publisher
    '''

    def request_nak_smoked(self, remote_connection: 'RemoteConnection', nak_seqno: int):
        _event = DistributorRetransmissionNAKErrorEvent(mc_addr=remote_connection.mc_address,
                                                        mc_port=remote_connection.mc_port)

        if remote_connection.connection.is_logging_enable(DistributorLogFlags.LOG_RETRANSMISSION_EVENTS):
            remote_connection.mConnection.log(
                'RETRANSMISSION RCV NAK Reject seqno: {} rmt-addr: {} rmt-sender-id: {} low-seno: {} high-seqno: {}'
                .format(nak_seqno, Aux.ip_addr_int_to_str(remote_connection.remote_host_address),
                        hex(remote_connection.remote_sender_id), self._low_seqno,
                        remote_connection.highiest_seen_seqno))

        ClientDeliveryController.get_instance().queue_event(self._connection_id, _event)

    def adjust_seqno(self, seqno: int):
        if seqno > self._high_seqno or seqno < self._low_seqno:
            return
        if seqno in self._served_list:
            return
        self._served_list.append(seqno)
        if seqno == self._high_seqno:
            self._high_seqno -= 1
        if seqno == self._low_seqno:
            self._low_seqno += 1

    def execute(self, connection: 'Connection'):
        if connection.is_time_to_die:
            self.cancel()
            return

        _resend = _failed = False

        remote_connection = connection.connection_receiver.get_remote_connection_by_id(self._remote_connection_id)
        # Have all missed segments been recovered?
        if self._retrans_item_count == len(self._served_list):
            connection.retransmission_controller.remove_retransmission_request(self)
            self.cancel()
            return
        elif self._retries > connection.configuration.retrans_max_retries:
            _failed = True
        else:
            _resend = True

        if _resend:
            if connection.is_logging_enabled(DistributorLogFlags.LOG_RETRANSMISSION_EVENTS):
                connection.log_info(
                    'RETRANSMISSION XTA request Segments [{}:{}] Retry: {} rmt-host: {} rmt-sender-id: {} served {} out of {}'
                    .format(self._low_seqno, self._high_seqno, self._retries,
                            remote_connection.remote_host_address_string,
                            hex(remote_connection.remote_sender_id), len(self._served_list),
                            self._retrans_item_count))
                self.queue_retransmission_rqst_message(connection, remote_connection)
                self._retries += 1
            elif _failed:
                connection.retransmission_controller.remove_retransmission_request(self)
                self.cancel()
                _event = DistributorTooManyRetransmissionRetriesErrorEvent(mc_addr=connection.mc_address,
                                                                           mc_port=connection.mc_port)
                if connection.is_logging_enabled(DistributorLogFlags.LOG_RETRANSMISSION_EVENTS):
                    connection.log_info(
                        'RETRANSMISSION: to many retransmission retries, rmt-addr: {} Remote Sender Id: {} low-seqno: {} high-seqno: {}'
                        .format(remote_connection.remote_host_address_string,
                                hex(remote_connection.remote_sender_id), self._low_seqno, self._high_seqno))

                ClientDeliveryController.get_instance().queue_event(connection.connection_id, _event)


class RetransmissionController:
    def __init__(self, connection: 'Connection'):
        from pymc.connection import Connection
        self._connection:Connection = connection
        self._queue_mutex = threading.Lock()
        self._retransmission_request_queue = []
        if connection.configuration.nagging_window_interval > 0:
            self._nagging_monitor = NaggingMonitorTask(connection.configuration)
            from pymc.connection_timers import ConnectionTimerExecutor
            ConnectionTimerExecutor.getInstance().queue(interval=connection.configuration.nagging_window_interval,
                                                        task=self._nagging_monitor,
                                                        repeat=True)

    def remove_retransmission_request(self, retrans_rqst: RetransmissionRequestItem):
        with self._queue_mutex:
            self._retransmission_request_queue.remove(retrans_rqst)

    def close(self):
        self._nagging_monitor.cancel()
        with self._queue_mutex:
            for _item in self._retransmission_request_queue:
                _item.cancel()
            self._retransmission_request_queue.clear()

    def create_retransmission_request(self, remote_connection, low_seqno, high_seqno):
        _rqst_task = RetransmissionRequestItem(connection_id=self._connection.connection_id,
                                               remote_connection_id=remote_connection.mRemoteConnectionId,
                                               low_seqno=low_seqno,
                                               high_seqno=high_seqno)
        self._retransmission_request_queue.append(_rqst_task)

        from pymc.connection_timers import ConnectionTimerExecutor
        ConnectionTimerExecutor.getInstance().queue(interval=self._connection.configuration.retrans_timeout_ms,
                                                    task=_rqst_task,
                                                    init_delay=0,
                                                    repeat=True)

    def update_retransmissions(self, segment: Segment):
        if not self._retransmission_request_queue:
            return
        with self._queue_mutex:
            for _rqst in self._retransmission_request_queue:
                _rqst.adjust_seqno(segment.seqno)

    def process_retransmission_nak(self, segment: Segment):
        if not self._retransmission_request_queue:  # list is empty
            return

        _msg = NetMsgRetransmissionNAK(segment)
        _msg.decode()
        _nak_seqno_list = _msg.nak_sequence_numbers
        with self._queue_mutex:
            for seqno in _nak_seqno_list:
                for _rqst_task in self._retransmission_request_queue:
                    if seqno >= _rqst_task._low_seqno and seqno <= _rqst_task._high_seqno:
                        _remote_connection = self._connection.connection_receiver.get_remote_connection(segment)
                        _rqst_task.request_nak_smoked(_remote_connection, seqno)
                        self._retransmission_request_queue.remove(_remote_connection)
