from __future__ import annotations

import logging
import threading
from time import perf_counter

from pymc.aux.aux import Aux
from pymc.aux.aux_uuid import Aux_UUID
from pymc.aux.blocking_queue import BlockingQueue
from pymc.aux.distributor_exception import DistributorException
from pymc.aux.log_manager import LogManager
from pymc.connection_configuration import ConnectionConfiguration
from pymc.connection_receiver import ConnectionReceiver
from pymc.connection_sender import ConnectionSender
from pymc.connection_timers import ConnectionTimerExecutor
from pymc.distributor_events import AsyncEvent
from pymc.distributor_interfaces import ConnectionBase, PublisherBase, SubscriberBase
from pymc.distributor_interfaces import DistributorBase
from pymc.ipmc import IPMC
from pymc.msg.net_msg_configuration import NetMsgConfiguration
from pymc.msg.segment import Segment
from pymc.msg.xta_update import XtaUpdate
from pymc.retransmission_controller import RetransmissionController
from pymc.traffic_statistics import TrafficStatisticTimerTask


class Connection(ConnectionBase):


    def __init__(self, distributor: DistributorBase, configuration: ConnectionConfiguration):
        self._connection_id: int = Aux_UUID.getId()
        self._time_to_die: bool = False
        self._publishers: [PublisherBase] = []
        self._subscribers: [SubscriberBase] = []
        self._distributor: DistributorBase = distributor
        self._configuration: ConnectionConfiguration = configuration
        self._logger: logging.Logger = LogManager.getInstance().getLogger(module_name='DistributorConnection')
        self._last_known_error = None
        self._state: int = self.STATE_INIT
        self._mutex: threading.RLock = threading.RLock()
        self._async_event_queue: BlockingQueue = BlockingQueue()
        self._retransmission_controller = RetransmissionController(self)
        self._ipmc: IPMC = IPMC(configuration.eth_device, configuration.ttl, configuration.ipBufferSize)
        self._ipmc.open(configuration.mca, configuration.mca_port)
        self._ipmc.startReader(self.ipmcReadComplete, self.ipmcReadException)
        self._working_thread = threading.Thread(target=self.connectionWorker(), name="connection-working")
        self._connection_sender = ConnectionSender(self)
        self._connection_receiver = ConnectionReceiver(self)
        self._start_time = Aux.currentSeconds()
        self._traffic_statistic_task = TrafficStatisticTimerTask(self._connection_id)
        ConnectionTimerExecutor.getInstance().queue(interval=1000, task=self._traffic_statistic_task, repeat=True)


    def lock(self):
        self._mutex.acquire()

    def flushHoldback(self, flush_holback_seqno: int ):
        self._connection_sender.flushHoldback(flush_holback_seqno);
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
    def subscribers(self) -> list[SubscriberBase]:
        return self._subscribers

    @property
    def publishers(self) -> list[PublisherBase]:
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
    def distributor(self) -> DistributorBase:
        return self._distributor

    @property
    def traffic_statistic_task(self) -> TrafficStatisticTimerTask:
        return self._traffic_statistic_task

    def unlock(self):
        self._mutex.release()

    def queueAsyncEvent(self, async_event: AsyncEvent):
        if not self._time_to_die:
            self._async_event_queue.add(async_event)

    def ipmcReadException(self, exception: Exception):
        self._logger.fatal("IPMC {} read exception {}".format(self, str(exception)))

    def __str__(self):
        return "mca: {} mca-port: {}".format(self._configuration.mca, self._configuration.mca_port)

    def publishUpdate(self, xta_update: XtaUpdate):
        self._connection_sender.publishUpdate(xta_update)

    def checkStatus(self):
        if self._state == ConnectionBase.STATE_RUNNING:
            return

        if self._state == ConnectionBase.STATE_CLOSED:
            raise DistributorException("Connection is not in a running state, has been closed.")

        if self._state == ConnectionBase.STATE_ERROR:
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

    def isLoggingEnabled(self, log_flag: int) -> bool:
        return self._distributor.is_logging_enable(log_flag)

    def getConfiguration(self):
        return self._configuration

    def queueAsyncEvent(self):



    def pushOutConfiguration(self):
        _cfgmsg = NetMsgConfiguration(Segment(self._configuration.small_segment_size))

        _cfgmsg.setHeader(message_type=Segment.MSG_TYPE_CONFIGURATION,
                          segment_flags=(Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END),
                          local_address=self._ipmc.local_address,
                          sender_id=self._connection_sender.sender_id,
                          sender_start_time_sec=self._connection_sender.sender_start_time,
                          app_id=self._distributor.app_id())

        _cfgmsg.set(mc_addr=self.ipmc.mc_address,
                    mc_port=self.ipmc.mc_port,
                    sender_id=self.connection_sender.sender_id,
                    start_time_sec=self.connection_sender.sender_start_time,
                    heartbeat_interval=self.configuration.heartbeat_interval_ms,
                    config_interval=self.configuration.configuration_interval_ms,
                    host_addr=self.distributor.local_address(),
                    app_id=self.distributor.app_id(),
                    app_name=self.distributor.app_name())

        _cfgmsg.encode()
        self.connection_sender.send_segment(_cfgmsg.segment)

    def connectionWorker(self):
        while self._state == ConnectionBase.STATE_RUNNING or self._state == ConnectionBase.STATE_INIT:
            _async_event: AsyncEvent = AsyncEvent.cast(self._async_event_queue.take())

            with self._mutex:
                if not self._state == ConnectionBase.STATE_RUNNING:
                    self._async_event_queue.clear()
                    return

                # Execute Async Event
                _async_event.execute(self)
                
                if not self._async_event_queue.is_empty():
                    _event_list: list = self._async_event_queue.drain(60)
                    for _async_event in _event_list:
                        if self._state == ConnectionBase.STATE_RUNNING:
                            _async_event.execute(self)

    def logInfo(self, msg):
        self._logger.info(msg)

    def logWarning(self, msg):
        self._logger.warning(msg)

    def logError(self, msg):
        self._logger.error(msg)

    def logThrowable(self, exception):
        self._logger.exception(exception)

    def isLogFlagSet(self, flag: int) -> bool:
        if (self._distributor.configuration().log_flags & flag) != 0:
            return True
        return False
