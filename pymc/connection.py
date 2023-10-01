from __future__ import annotations

import logging
import threading
import time
from time import perf_counter
from typing import Callable, Any

from pymc.aux.aux import Aux
from pymc.aux.aux_uuid import Aux_UUID
from pymc.aux.blocking_queue import BlockingQueue
from pymc.aux.distributor_exception import DistributorException
from pymc.aux.log_manager import LogManager
from pymc.aux.trace import Trace
from pymc.client_controller import ClientDeliveryController
from pymc.connection_configuration import ConnectionConfiguration
from pymc.connection_receiver import ConnectionReceiver
from pymc.connection_sender import ConnectionSender
from pymc.connection_timers import ConnectionTimerExecutor
from pymc.distributor_events import AsyncEvent, DistributorEvent
from pymc.distributor_configuration import DistributorLogFlags
from pymc.ipmc import IPMC
from pymc.msg.net_msg_configuration import NetMsgConfiguration
from pymc.msg.net_msg_retransmission import NetMsgRetransmissionRqst
from pymc.msg.segment import Segment
from pymc.msg.xta_update import XtaUpdate
from pymc.remote_connection import RemoteConnection
from pymc.retransmission_controller import RetransmissionController
from pymc.retransmission_statistics import NodeEntryIn, NodeEntryOut
from pymc.subscription import SubscriptionFilter
from pymc.traffic_statistics import TrafficStatisticTimerTask, DistributorPublisherStatisticsIf, \
    DistributorSubscriberStatisticsIf


class Connection(object):
    STATE_INIT = 0
    STATE_RUNNING = 1
    STATE_CLOSED = 2
    STATE_ERROR = 3

    def __init__(self, configuration: ConnectionConfiguration):
        self._connection_id: int = Aux_UUID.getId()
        self._time_to_die: bool = False
        self._publishers: ['Publisher'] = []
        self._subscribers: ['Subscriber'] = []
        self._configuration: ConnectionConfiguration = configuration
        self._logger: logging.Logger = LogManager.get_instance().get_logger(module_name='DistributorConnection')
        self._last_known_error = None
        self._state: int = self.STATE_INIT
        self._mutex: threading.RLock = threading.RLock()
        self._async_event_queue: BlockingQueue = BlockingQueue()
        self._subscription_filter = SubscriptionFilter()
        ClientDeliveryController.get_instance().add_subscription_filter(self._connection_id, self._subscription_filter)
        self._retransmission_controller = RetransmissionController(self)
        self._ipmc: IPMC = IPMC(configuration.eth_device, configuration.ttl, configuration.ipBufferSize)
        self._ipmc.open(configuration.mca, configuration.mca_port)
        self._working_thread = threading.Thread(target=self.connection_worker, name="connection-working")
        self._working_thread.start()
        self._connection_sender = ConnectionSender(self)
        self._connection_receiver = ConnectionReceiver(self)
        self._start_time = Aux.current_seconds()
        self._traffic_statistic_task = TrafficStatisticTimerTask(self._connection_id)
        ConnectionTimerExecutor.getInstance().queue(interval=1000, task=self._traffic_statistic_task, repeat=True)
        self._state: int = self.STATE_RUNNING

    def __enter__(self):
        self._mutex.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._mutex.release()

    def remove_publisher(self, publisher: 'Publisher'):
        self._publishers.remove(publisher)

    def get_traffic_statistics(self) -> DistributorPublisherStatisticsIf | DistributorSubscriberStatisticsIf:
        return self._traffic_statistic_task

    def eval_outgoing_traffic_flow(self, bytes_sent: int) -> int:
        return self._connection_sender.eval_outgoing_traffic_flow(bytes_sent)

    def flush_holdback(self, flush_holback_seqno: int):
        self._connection_sender.flush_holback(flush_holback_seqno)

    @property
    def mc_port(self) -> int:
        return self._ipmc.mc_port

    @property
    def mc_address(self) -> int:
        return self._ipmc.mc_address

    @property
    def ipmc(self) -> IPMC:
        return self._ipmc

    @property
    def configuration(self) -> ConnectionConfiguration:
        return self._configuration

    @property
    def connection_id(self) -> int:
        return self._connection_id

    @property
    def last_known_error(self) -> str:
        return self._last_known_error

    @property
    def retransmission_controller(self) -> RetransmissionController:
        return self._retransmission_controller

    @last_known_error.setter
    def last_known_error(self, value: str):
        self._last_known_error = value

    @property
    def connection_sender(self) -> ConnectionSender:
        return self._connection_sender

    @property
    def connection_receiver(self) -> ConnectionReceiver:
        return self._connection_receiver

    @property
    def subscribers(self) -> list['Subscriber']:
        return self._subscribers

    @property
    def remote_connections(self) -> list['RemoteConnection']:
        return self.connection_receiver.get_remote_connections()

    @property
    def publishers(self) -> list['Publisher']:
        return self._publishers

    @property
    def logger(self):
        return self._logger

    @property
    def start_time(self) -> int:
        return self._start_time

    @property
    def is_time_to_die(self) -> bool:
        return self._time_to_die

    @property
    def traffic_statistic_task(self) -> TrafficStatisticTimerTask:
        return self._traffic_statistic_task

    @property
    def local_address(self) -> int:
        from pymc.distributor import Distributor
        return Distributor.get_instance().local_address

    @property
    def get_active_subscriptions_count(self) -> int:
        return self._subscription_filter.getActiveSubscriptionsCount()

    def create_subscriber(self,
                          event_callback: Callable[[DistributorEvent], None],
                          update_callback: Callable[[str, bytes, object, int, int], None]) -> 'Subscriber':

        from pymc.subscriber import Subscriber
        _subscriber = Subscriber(self.connection_id, event_callback, update_callback)

        self._subscribers.append(_subscriber)
        if event_callback:
            ClientDeliveryController.get_instance().add_event_listner(self._connection_id, event_callback)
            self._connection_receiver.trigger_remote_configuration_notifications(event_callback)

        return _subscriber

    def create_publisher(self, event_callback: Callable[['DistributorEvent'], None]) -> 'Publisher':
        from pymc.publisher import Publisher
        from pymc.distributor import Distributor

        if self._configuration.max_bandwidth_kbit > 0:
            _flood_regulated = True
        else:
            _flood_regulated = False

        publisher = Publisher(connection_id=self.connection_id,
                              app_id=Distributor.get_instance().app_id,
                              is_flood_regulated=_flood_regulated,
                              distributor_event_callback=event_callback)

        self._publishers.append(publisher)
        self.push_out_configuration()

        if event_callback:
            ClientDeliveryController.get_instance().add_event_listner(self._connection_id, event_callback)
            self._connection_receiver.trigger_remote_configuration_notifications(event_callback)

        return publisher

    def add_subscription(self, subscriber: 'Subscriber', subject: str, callback_parameter: object):
        if self.is_time_to_die:
            raise DistributorException("Connection {} has been closed.".format(self._ipmc))

        if self.is_logging_enabled(DistributorLogFlags.LOG_SUBSCRIPTION_EVENTS):
            self.log_info("ADD Subscription: {} connection: {}".format(subject, self._ipmc))

        return self._subscription_filter.add(subject, subscriber.update_callback, callback_parameter)

    def queueAsyncEvent(self, async_event: AsyncEvent):
        if not self._time_to_die:
            self._async_event_queue.add(async_event)

    def __str__(self):
        return "mca: {} mca-port: {}".format(self._configuration.mca, self._configuration.mca_port)

    def publishUpdate(self, xta_update: XtaUpdate) -> int:
        return self._connection_sender.publish_update(xta_update)

    def checkStatus(self):
        if self._state == Connection.STATE_RUNNING:
            return

        if self._state == Connection.STATE_CLOSED:
            raise DistributorException("Connection is not in a running state, has been closed.")

        if self._state == Connection.STATE_ERROR:
            if not self._last_known_error:
                raise DistributorException(
                    "Connection in error state, not in a trustworthy state, last error signale:\n   {}".
                    format(self._last_known_error))
            else:
                raise DistributorException("Connection in error state, not in a trustworthy state")

    def send(self, segment: Segment) -> int:
        _start_time = time.perf_counter_ns()
        self._ipmc.send(segment.encoder.buffer)
        return int((time.perf_counter_ns() - _start_time) / 1000)  # return usec

    def getConfiguration(self):
        return self._configuration

    def get_remote_connection(self, remote_connection_id: int) -> RemoteConnection:
        return self._connection_receiver.get_remote_connection_by_id(remote_connection_id)

    def async_event_to_client(self, event: DistributorEvent):
        ClientDeliveryController.get_instance().queue_event(connection_id=self.connection_id, event=event)

    def push_out_configuration(self):
        from pymc.distributor import Distributor
        _cfgmsg = NetMsgConfiguration(Segment(self._configuration.small_segment_size))

        _cfgmsg.setHeader(message_type=Segment.MSG_TYPE_CONFIGURATION,
                          segment_flags=(Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END),
                          local_address=self._ipmc.local_address,
                          sender_id=self._connection_sender.sender_id,
                          sender_start_time_sec=self._connection_sender.sender_start_time,
                          app_id=Distributor.get_instance().app_id)

        _cfgmsg.set(mc_addr=self.ipmc.mc_address,
                    mc_port=self.ipmc.mc_port,
                    sender_id=self.connection_sender.sender_id,
                    start_time_sec=self.connection_sender.sender_start_time,
                    heartbeat_interval=self.configuration.heartbeat_interval_ms,
                    config_interval=self.configuration.configuration_interval_ms,
                    host_addr=Distributor.get_instance().local_address,
                    app_id=Distributor.get_instance().app_id,
                    app_name=Distributor.get_instance().app_name)

        _cfgmsg.encode()
        self.connection_sender.send_segment(_cfgmsg.segment)

    def connection_worker(self):
        while self._state == Connection.STATE_RUNNING or self._state == Connection.STATE_INIT:
            _async_event: AsyncEvent = AsyncEvent.cast(self._async_event_queue.take())

            trcctx: Trace = Trace()
            with self._mutex:
                trcctx.add("[connwrk {} got lock".format(_async_event.__class__.__name__))
                if not self._state == Connection.STATE_RUNNING:
                    self._async_event_queue.clear()
                    return

                # Execute Async Event
                _async_event.execute(self, trcctx)
                trcctx.add("[connwrk {} execution completed".format(_async_event.__class__.__name__))

                if not self._async_event_queue.is_empty():
                    _event_list: list = self._async_event_queue.drain(60)
                    for _async_event in _event_list:
                        if self._state == Connection.STATE_RUNNING:
                            trcctx.add("[connwrk-drain {} starting execution".format(_async_event.__class__.__name__))
                            _async_event.execute(self, trcctx)
                            trcctx.add("[connwrk-drain {} execution completed".format(_async_event.__class__.__name__))
            trcctx.dump()

    def get_web_connection_attributes(self) -> list[str]:
        from pymc.distributor import Distributor

        _in_node_entry: NodeEntryIn = Distributor.get_instance().retransmission_statistics.get_in_entry(self.mc_address,
                                                                                                        self.mc_port,
                                                                                                        self.local_address)
        _out_node_entry: NodeEntryOut = Distributor.get_instance().retransmission_statistics.get_out_entry(
            self.mc_address, self.mc_port, self.local_address)

        _attr_arr = []
        _attr_arr.append(Aux.ip_addr_int_to_str(self.mc_address))
        _attr_arr.append(str(self.mc_port))
        _attr_arr.append(str(Aux.time_string(self.start_time)))
        _attr_arr.append(str(len(self.publishers)))
        _attr_arr.append(str(len(self.subscribers)))
        _attr_arr.append(str(len(self.remote_connections)))
        _attr_arr.append(str(self._traffic_statistic_task.getTotalXtaUpdates()))
        _attr_arr.append(str(self._traffic_statistic_task.getTotalRcvUpdates()))

        _attr_arr.append(str(_out_node_entry.retrans_sent_by_this_node))
        _attr_arr.append(str(_in_node_entry.retrans_to_this_node))
        return _attr_arr

    def get_web_subscription_count_attributes(self) -> list[str]:
        _attr: list[str] = [Aux.ip_addr_int_to_str(self.mc_address), str(self.mc_port)]
        _attr.append(str(self._subscription_filter.getActiveSubscriptionsCount()))
        return _attr

    def get_web_subscription_subjects(self, address_data: bool) -> list[list]:
        subjects: list[str] = self._subscription_filter.getActiveSubscriptionsStrings()
        subscriptions: list[list[str]] = []
        _mc_addr_str = Aux.ip_addr_int_to_str(self.mc_address)
        _mc_port_str = str(self.mc_port)

        for subj in subjects:
            if address_data:
                subscriptions.append([_mc_addr_str, _mc_port_str, subj])
            else:
                subscriptions.append([subj])

        return subscriptions

    def get_web_remote_connections_attributes(self) -> list[list]:
        _rmt_connections: list[RemoteConnection] = self.connection_receiver.get_remote_connections()

        _web_rmt_connections: list[list] = []
        for _rmt_conn in _rmt_connections:
            _attr_arr = []
            _attr_arr.append(Aux.ip_addr_int_to_str(self.mc_address))
            _attr_arr.append(str(self.mc_port))

            _attr_arr.append(Aux.time_string(_rmt_conn.remote_start_time))
            _attr_arr.append(_rmt_conn.remote_host_address_string)
            _attr_arr.append(str(_rmt_conn.highiest_seen_seqno))
            _web_rmt_connections.append(_attr_arr)

        return _web_rmt_connections

    def log_info(self, msg):
        self._logger.info(msg)

    def log_warning(self, msg):
        self._logger.warning(msg)

    def log_error(self, msg):
        self._logger.error(msg)

    def log_exception(self, exception):
        self._logger.exception(exception)

    def is_logging_enabled(self, log_flag: int) -> bool:
        from pymc.distributor import Distributor
        _distributor = Distributor.get_instance()
        return _distributor.is_logging_enable(log_flag)
