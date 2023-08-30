from __future__ import annotations
from abc import ABC, abstractmethod
from pymc.distributor_configuration import DistributorConfiguration
from pymc.connection_configuration import ConnectionConfiguration
from pymc.ipmc import IPMC
from pymc.msg.segment import Segment
from pymc.msg.xta_update import XtaUpdate
from pymc.retransmission_controller import RetransmissionController
from pymc.traffic_statistics import TrafficStatisticTimerTask


class PublisherBase(ABC):
    pass


class SubscriberBase(ABC):
    pass


class ConnectionSenderBase(ABC):
    @abstractmethod
    def sender_id(self) -> int:
        pass


class ConnectionReceiverBase(ABC):
    pass


class ConnectionBase(ABC):
    STATE_INIT = 0
    STATE_RUNNING = 1
    STATE_CLOSED = 2
    STATE_ERROR = 3

    @abstractmethod
    def publishUpdate(self, xta_update: XtaUpdate):
        pass

    @abstractmethod
    def configuration(self) -> ConnectionConfiguration:
        pass

    @abstractmethod
    def distributor(self) -> DistributorBase:
        pass

    @abstractmethod
    def connection_id(self) -> int:
        pass

    @abstractmethod
    def send(self, segment: Segment) -> int:
        pass

    @abstractmethod
    def mc_address(self) -> int:
        pass

    @abstractmethod
    def mc_port(self) -> int:
        pass

    @abstractmethod
    def retransmission_controller(self) -> RetransmissionController:
        pass

    @abstractmethod
    def start_time(self) -> int:
        pass

    @abstractmethod
    def ipmc(self) -> IPMC:
        pass

    @abstractmethod
    def traffic_statistic_task(self) -> TrafficStatisticTimerTask:
        pass
class DistributorBase(ABC):

    @abstractmethod
    def distributor_id(self) -> int:
        pass

    @abstractmethod
    def app_name(self) -> str:
        pass

    @abstractmethod
    def app_id(self) -> int:
        pass

    @abstractmethod
    def start_time_string(self) -> str:
        pass

    @abstractmethod
    def local_address(self) -> int:
        pass

    @abstractmethod
    def local_address_string(self) -> str:
        pass

    @abstractmethod
    def get_txid(self) -> int:
        pass

    @abstractmethod
    def configuration(self) -> DistributorConfiguration:
        pass

    @abstractmethod
    def is_logging_enable(self, flag: int) -> bool:
        pass
