from __future__ import annotations
import threading

from pymc.distributor_configuration import DistributorLogFlags
from pymc.aux.aux import Aux
from pymc.connection_configuration import ConnectionConfiguration
from pymc.event_api.events_to_clients import DistributorNaggingErrorEvent, DistributorRetransmissionNAKErrorEvent, \
    DistributorTooManyRetransmissionRetriesErrorEvent
from pymc.event_timers.nagging_monitor_task import NaggingMonitorTask
from pymc.event_timers.retransmission_request_item import RetransmissionRequestItem
from pymc.msg.net_msg_retransmission import NetMsgRetransmissionRqst, NetMsgRetransmissionNAK
from pymc.msg.segment import Segment
from pymc.msg.xta_segment import XtaSegment





class RetransmissionController:
    def __init__(self, connection: 'Connection'):
        from pymc.connection import Connection
        self._connection:Connection = connection
        self._queue_mutex = threading.Lock()
        self._retransmission_request_queue = []
        if connection.configuration.nagging_window_interval_ms > 0:
            self._nagging_monitor = NaggingMonitorTask(connection.connection_id,connection.configuration)
            from pymc.connection_timers import ConnectionTimerExecutor
            ConnectionTimerExecutor.getInstance().queue(interval=connection.configuration.nagging_window_interval_ms,
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
                                               remote_connection_id=remote_connection._remote_connection_id,
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
