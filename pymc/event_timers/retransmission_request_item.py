from pymc.aux.aux import Aux
from pymc.distributor_configuration import DistributorLogFlags
from pymc.event_api.events_to_clients import DistributorRetransmissionNAKErrorEvent, \
    DistributorTooManyRetransmissionRetriesErrorEvent
from pymc.event_timers.connection_timer_event import ConnectionTimerEvent
from pymc.msg.net_msg_retransmission import NetMsgRetransmissionRqst
from pymc.msg.segment import Segment
from pymc.msg.xta_segment import XtaSegment


class RetransmissionRequestItem(ConnectionTimerEvent):
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

        from pymc.client_controller import ClientDeliveryController
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

                from pymc.client_controller import ClientDeliveryController
                ClientDeliveryController.get_instance().queue_event(connection.connection_id, _event)
