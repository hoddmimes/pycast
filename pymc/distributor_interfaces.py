from __future__ import annotations
from abc import ABC, abstractmethod
from logging import Logger

from pymc.distributor_configuration import DistributorConfiguration
from pymc.connection_configuration import ConnectionConfiguration
from pymc.ipmc import IPMC
from pymc.msg.net_msg_retransmission import NetMsgRetransmissionRqst
from pymc.msg.segment import Segment
from pymc.msg.xta_update import XtaUpdate
from pymc.retransmission_controller import RetransmissionController


class PublisherBase(ABC):

    @abstractmethod
    def get_id(self) -> int:
        pass


class SubscriberBase(ABC):
    @abstractmethod
    def get_id(self) -> int:
        pass


class ConnectionSenderBase(ABC):
    @abstractmethod
    def retransmit(self) -> int:
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
    def logger(self) -> Logger:
        pass

    @abstractmethod
    def is_logging_enable(self, flag: int) -> bool:
        pass

    @abstractmethod
    def log_info(self, msg: str):
        pass

    @abstractmethod
    def log_warn(self, msg: str):
        pass

    @abstractmethod
    def log_error(self, msg: str):
        pass

    @abstractmethod
    def log_exception(self, msg: str):
        pass

    @abstractmethod
    def connection_sender(self) -> ConnectionSenderBase:
        pass

    @abstractmethod
    def connection_receiver(self) -> ConnectionReceiverBase:
        pass

    @abstractmethod
    def update_in_retransmission_statistics(self, mc_addr: int, mc_port: int, msg: NetMsgRetransmissionRqst, to_this_node: bool):
        pass
    @abstractmethod
    def async_event_to_client(self, event):
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



