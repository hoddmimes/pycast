from abc import ABC, abstractmethod
from distributor import DistributorConfiguration


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




class DistributorBase(ABC):

    @abstractmethod
    def getId(self) -> int:
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


