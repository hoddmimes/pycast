from __future__ import annotations

import logging
import threading
from time import perf_counter
from typing import Callable, Any

from pymc.aux.aux import Aux
from pymc.aux.aux_uuid import Aux_UUID
from pymc.event_api.event_api_create_publisher import EventApiCreatePublisher
from pymc.event_api.event_api_create_subscriber import EventApiCreateSubscriber
from pymc.event_api.event_api_publish import EventApiPublish
from pymc.event_api.event_api_subscribe import EventApiSubscribe
from pymc.event_loop import EventLoop, ConnectionEvent
from pymc.aux.blocking_queue import BlockingQueue
from pymc.aux.distributor_exception import DistributorException
from pymc.aux.log_manager import LogManager
from pymc.client_controller import ClientDeliveryController
from pymc.connection_configuration import ConnectionConfiguration
from pymc.connection_receiver import ConnectionReceiver
from pymc.connection_sender import ConnectionSender
from pymc.connection_timers import ConnectionTimerExecutor
from pymc.event_api.events_to_clients import AsyncEvent, DistributorEvent
from pymc.distributor_configuration import DistributorLogFlags
from pymc.event_msgs.event_msg_rcv_data import EventMsgInboundMessage
from pymc.event_timers.check_heartbeat_task import CheckHeartbeatTask
from pymc.event_timers.send_configuration_task import SendConfigurationTask
from pymc.event_timers.send_heartbeat_task import SendHeartbeatTask
from pymc.event_timers.send_holdback_task import SenderHoldbackTimerTask
from pymc.event_timers.traffic_flow_task import TrafficFlowTask
from pymc.ipmc import IPMC
from pymc.msg.net_msg_configuration import NetMsgConfiguration
from pymc.msg.net_msg_retransmission import NetMsgRetransmissionRqst
from pymc.msg.segment import Segment
from pymc.msg.xta_update import XtaUpdate
from pymc.remote_connection import RemoteConnection
from pymc.retransmission_controller import RetransmissionController
from pymc.retransmission_statistics import RetransmissionStatistics
from pymc.subscription import SubscriptionFilter
from pymc.event_timers.traffic_statistics_task import TrafficStatisticTimerTask, DistributorPublisherStatisticsIf, \
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

        self._retransmission_controller = RetransmissionController(self)
        self._retransmission_statistics = RetransmissionStatistics()
        self._ipmc: IPMC = IPMC(configuration.eth_device, configuration.ttl, configuration.ipBufferSize)
        self._ipmc.open(configuration.mca, configuration.mca_port)

        self._connection_sender = ConnectionSender(self)
        self._connection_receiver = ConnectionReceiver(self)
        self._start_time = Aux.current_seconds()
        self._traffic_statistic_task = TrafficStatisticTimerTask(self._connection_id)
        ConnectionTimerExecutor.getInstance().queue(interval=1000, task=self._traffic_statistic_task, repeat=True)

        self._subscription_filter = SubscriptionFilter()
        ClientDeliveryController.get_instance().add_subscription_filter(self._connection_id, self._subscription_filter)

        self._event_loop: EventLoop = EventLoop(self.event_dispatcher)
        self._event_loop.start()
        self._event_loop.wait_for_the_loop_to_start()
        self._state = Connection.STATE_RUNNING

    def lock(self):
        self._mutex.acquire()

    def unlock(self):
        self._mutex.release()

    def create_subscriber(self,
                          event_callback: Callable[[DistributorEvent], None],
                          update_callback: Callable[[str, bytes, object, int, int], None]) -> 'Subscriber':

        from pymc.subscriber import Subscriber
        _subscriber = Subscriber(self.connection_id, event_callback, update_callback)

        self._subscribers.append(_subscriber)
        if event_callback:
            ClientDeliveryController.get_instance().add_event_listner(self._connection_id, event_callback)
            self._connection_receiver.triggerRemoteConfigurationNotifications(event_callback)

        return _subscriber

    def remove_publisher(self, publisher: 'Publisher'):
        self._publishers.remove(publisher)

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
            self._connection_receiver.triggerRemoteConfigurationNotifications(event_callback)

        return publisher

    def get_traffic_statistics(self) -> DistributorPublisherStatisticsIf | DistributorSubscriberStatisticsIf:
        return self._traffic_statistic_task

    def eval_outgoing_traffic_flow(self, bytes_sent: int) -> int:
        return self._connection_sender.eval_outgoing_traffic_flow(bytes_sent)

    def flushHoldback(self, flush_holback_seqno: int):
        self._connection_sender.flush_holback(flush_holback_seqno)

    @property
    def is_flow_regulated(self):
        if self._configuration.max_bandwidth_kbit > 0:
            return True
        else:
            return False

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
        from distributor import Distributor
        return Distributor.get_instance().local_address

    @property
    def retransmission_statistics(self):
        return self._retransmission_statistics

    def get_subscriber(self, subscriber_id: int) -> 'Subscriber' | None:
        for _subscriber in self._subscribers:
            if _subscriber.get_id == subscriber_id:
                return _subscriber
        return None

    def add_subscription(self, subscriber_id: int, subject: str, callback_parameter: object):
        if self.is_time_to_die:
            raise DistributorException("Connection {} has been closed.".format(self._ipmc))

        _subscriber = self.get_subscriber(subscriber_id)
        if _subscriber is None:
            raise DistributorException("Subscriber {} is not found!!!".format(hex(subscriber_id)))

        if self.is_logging_enabled(DistributorLogFlags.LOG_SUBSCRIPTION_EVENTS):
            self.log_info("ADD Subscription: {} connection: {}".format(subject, self._ipmc))

        return self._subscription_filter.add(subject, _subscriber.update_callback, callback_parameter)

    def queueAsyncEvent(self, async_event: AsyncEvent):
        if not self._time_to_die:
            self._async_event_queue.add(async_event)

    def ipmcReadException(self, exception: Exception):
        self._logger.fatal("IPMC {} read exception {}".format(self, str(exception)))

    def __str__(self):
        return "mca: {} mca-port: {}".format(self._configuration.mca, self._configuration.mca_port)

    '''
    returns transmission delay time in usec
    '''

    def publish_update(self, event: EventApiPublish) -> int:
        self.check_status()
        _xta_update = XtaUpdate(event.subject, event.data)
        _xta_time = self._connection_sender.publish_update(_xta_update)

        if self.is_flow_regulated:
            _wait_time: int = self.eval_outgoing_traffic_flow(_xta_update.size)
            if _wait_time > 0:
                if self.is_logging_enabled(DistributorLogFlags.LOG_TRAFFIC_FLOW_EVENTS):
                    self.log_info(
                        "outgoing flow regulated, wait: {} ms)  xta_time: {}"
                        .format(_wait_time, _xta_time))
                Aux.sleep_ms(_wait_time)
        return _xta_time

    def check_status(self):
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
        _start_time = perf_counter()
        self._ipmc.send(segment.encoder.buffer)
        return int((perf_counter() - _start_time) * 1000000)  # return usec

    def getConfiguration(self):
        return self._configuration

    def get_remote_connection_by_id(self, remote_connection_id: int) -> RemoteConnection:
        return self._connection_receiver.get_remote_connection_by_id(remote_connection_id)

    def update_in_retransmission_statistics(self, mc_addr: int,
                                            mc_port: int,
                                            msg: NetMsgRetransmissionRqst,
                                            to_this_node: bool):
        self._retransmission_statistics.update_in_statistics(mc_addr, mc_port, msg.hdr_local_address, to_this_node)

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
        return Distributor.get_instance().is_logging_enable(log_flag)

    def schedule_async_event(self, event: ConnectionEvent) -> Any:
        self._event_loop.queue_event(event)
        return None

    '''
    =================================================================================
    Async schedule and dispatch routines. All asynchronous events are single threaded 
    per connection. There are three types of asynchronus events that needs to be synchronized 
    1) Timer events
    2) Unsolicited network messages
    3) distributor API calls
    '''

    def schedule_async_event_wait(self, event: ConnectionEvent) -> Any:
        return self._event_loop.queue_event_wait(event)

    def event_api(self, event: ConnectionEvent) -> Any:
        if self.is_logging_enabled(DistributorLogFlags.LOG_EVENT_LOOP_API):
            self.log_info("[EVENT-LOOP] <{}> {}".format(event.__class__.__name__, event))
        match event:
            case EventApiPublish():
                _event: EventApiPublish = EventApiPublish.cast(event)
                return self.publish_update(_event)
            case EventApiCreateSubscriber():
                _event: EventApiCreateSubscriber = EventApiCreateSubscriber.cast(event)
                return self.create_subscriber(event_callback=_event.event_callback,
                                              update_callback=_event.update_callback)
            case EventApiCreatePublisher():
                _event: EventApiCreatePublisher = EventApiCreatePublisher.cast(event)
                return self.create_publisher(event_callback=_event.event_callback)
            case EventApiSubscribe():
                _event: EventApiSubscribe = EventApiSubscribe.cast(event)
                return self.add_subscription(subscriber_id=_event.subscriber_id, subject=_event.subject,
                                             callback_parameter=_event.callback_parameter)

            case _:
                raise DistributorException("unknown API event {} ".format(event.__class__.__name__))

    def event_net_message(self, event: ConnectionEvent):
        if self.is_logging_enabled(DistributorLogFlags.LOG_EVENT_LOOP_MSGS):
            self.log_info("[EVENT-LOOP] <{}> {}".format(event.__class__.__name__, event))
        match event:
            case EventMsgInboundMessage():
                _event = EventMsgInboundMessage.cast(event)
                segment: Segment = Segment(_event.data)
                segment.decode()
                self.traffic_statistic_task.update_rcv_statistics(segment)
                self._connection_receiver.process_received_segment(segment)
            case _:
                raise DistributorException("unknown NET MSG event {} ".format(event.__class__.__name__))

    def event_timer(self, event: ConnectionEvent):
        if self.is_logging_enabled(DistributorLogFlags.LOG_EVENT_LOOP_TIMERS):
            self.log_info("[EVENT-LOOP] <{}> {}".format(event.__class__.__name__, event))
        match event:
            case CheckHeartbeatTask():
                _event: CheckHeartbeatTask = CheckHeartbeatTask.cast( event )
                _event.execute(self)
            case SendConfigurationTask():
                _event: SendConfigurationTask = SendConfigurationTask.cast(event)
                _event.execute(self)
            case SendHeartbeatTask():
                _event: SendHeartbeatTask = SendHeartbeatTask.cast(event)
                _event.execute(self)
            case SenderHoldbackTimerTask():
                _event: SenderHoldbackTimerTask = SenderHoldbackTimerTask.cast(event)
                _event.execute(self)
            case TrafficFlowTask():
                _event: TrafficFlowTask = TrafficFlowTask.cast(event)
                _event.execute(self)
            case TrafficStatisticTimerTask():
                _event: TrafficStatisticTimerTask = TrafficStatisticTimerTask.cast(event)
                _event.execute(self)
            case _:
                raise DistributorException("unknown Timer MSG event {} ".format(event.__class__.__name__))


    def event_dispatcher(self, event: ConnectionEvent):
        match event.event_type:
            case ConnectionEvent.API_EVENT:
                return self.event_api(event)
            case ConnectionEvent.TIMER_EVENT:
                self.event_timer(event)
            case ConnectionEvent.NET_MESSAGE:
                self.event_net_message(event)
            case _:
                raise DistributorException("Unknown connection event {}".format(event.event_type))
