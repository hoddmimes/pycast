import sys
import logging
from pymc.aux.aux import Aux
from pymc.aux.log_manager import LogManager
from pymc.distributor_interfaces import DistributorBase
from pymc.publisher import Publisher
from pymc.subscriber import Subscriber

from pymc.connection_configuration import ConnectionConfiguration
from pymc.connection import Connection



class Distributor(DistributorBase):

    def __init__(self, application_name: str, configuration: DistributorConfiguration = None):
        self.mUUID:Aux.Aux_UUID = Aux.Aux_UUID()
        self.mConfiguration = configuration or DistributorConfiguration(application_name)
        LogManager.setConfiguration( configuration.logToConsole, configuration.logToFile, configuration.logFile, logging.DEBUG)
        self.mLogger = LogManager.getLogger('Distributor')
        self.mId = Aux.getApplicationId()
        self.mStartTime = Aux.datetime_string()
        self.mLocalIpAddress = Aux.getIpAddress('')
        self.mLogger.info("==== Distributor [{}] Started at {} ID {} ====".format(configuration.applName, Aux.datetime_string(), self.mApplId))

    def createConnection(self, configuration: ConnectionConfiguration ) -> Connection:
        return Connection( self, configuration)

    def createPublisher(self, connection: Connection) -> Publisher:
        pass

    def createSubscriber( self, connection: Connection) -> Subscriber:
       pass

    def getId(self) -> int:
        return self.mId

    def getStartTime(self) -> str:
        return self.mStartTime

    def getLocalInetAddrStr(self) -> str:
        return self.mLocalIpAddress

    def getLocalInetAddr(self) -> int:
        return Aux.ipAddrStrToInt(self.mLocalIpAddress)
    def getTXID(self) -> int:
        return self.mUUID.getNextId()

    def getConfiguration(self) -> DistributorConfiguration:
        return self.mConfiguration