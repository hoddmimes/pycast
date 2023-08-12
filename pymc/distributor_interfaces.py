from __future__ import annotations
from abc import ABC, abstractmethod
from pymc.distributor_configuration import DistributorConfiguration
from pymc.connection_configuration import ConnectionConfiguration
from pymc.msg.segment import Segment

class AsyncEvent(ABC):

    def __init__(self, taskName):
        self._taskName = taskName
        super(AsyncEvent,self).__init__()

    @abstractmethod
    def execute(self):
        pass
    def getTaskName(self) -> str:
        return self._taskName

class PublisherBase(ABC):
    pass
class SubscriberBase(ABC):
    pass


class ConnectionSenderBase(ABC):
    @abstractmethod
    def getSenderId(self) -> int:
        pass


class ConnectionReceiverBase(ABC):
    pass

class ConnectionBase(ABC):
    STATE_INIT = 0
    STATE_RUNNING = 1
    STATE_CLOSED = 2
    STATE_ERROR = 3

    @abstractmethod
    def publishUpdate( xtaUpdate ):
        pass

    @abstractmethod
    def getConfiguration(self) -> ConnectionConfiguration:
        pass

    @abstractmethod
    def getDistributor(selfself) -> DistributorBase:
        pass

    @abstractmethod
    def getConnectionId(self) -> int:
        pass

    @abstractmethod
    def send(self, segment:Segment ) ->int:
        pass

    @abstractmethod
    def getMcAddress(self) ->int:
        pass
    @abstractmethod
    def getMcPort(self) ->int:
        pass

class DistributorBase(ABC):

    @abstractmethod
    def getId(self) -> int:
        pass
    @staticmethod
    def getApplName(self) -> str:
        pass

    @abstractmethod
    def getStartTime(self) -> str:
        pass
    @abstractmethod
    def getLocalInetAddr(self) -> int:
        pass
    @abstractmethod
    def getLocalInetAddrStr(self) -> str:
        pass

    @abstractmethod
    def getTXID(self) -> int:
        pass

    @abstractmethod
    def getConfiguration(self) -> DistributorConfiguration:
        pass


    @abstractmethod
    def isLoggingEnable(self) -> bool:
        pass