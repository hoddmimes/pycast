import sys
import logging
from aux import Aux
from aux import LogManager
from distributor_interfaces import DistributorBase
from publisher import Publisher
from subscriber import Subscriber

from connection import DistributorConnection
from connection import ConnectionConfiguration


class LogFlags:
    LOG_ERROR_EVENTS = 1
    LOG_CONNECTION_EVENTS = 2
    LOG_RMTDB_EVENTS = 4
    LOG_RETRANSMISSION_EVENTS = 8
    LOG_SUBSCRIPTION_EVENTS = 16
    LOG_STATISTIC_EVENTS = 32
    LOG_SEGMENTS_EVENTS = 64
    LOG_DATA_PROTOCOL_RCV = 128;
    LOG_DATA_PROTOCOL_XTA = 256
    LOG_RETRANSMISSION_CACHE = 512
    LOG_DEFAULT_FLAGS = LOG_ERROR_EVENTS + LOG_CONNECTION_EVENTS + LOG_RETRANSMISSION_EVENTS

class DistributorConfiguration:

    def __init__(self, applName:str ):
        self.applName = applName
        self.logFlags = LogFlags.LOG_DEFAULT_FLAGS
        self.logToConsole = True
        self.logToFile = True
        self.logFile = 'Distributor.log'
        self.ethDevice = None


class Distributor(DistributorBase):

    def __init__(self, application_name: str, configuration: DistributorConfiguration = None):
        self.mUUID:Aux.PCUUID = Aux.PCUUID()
        self.mConfiguration = configuration or DistributorConfiguration(application_name)
        LogManager.setConfiguration( configuration.logToConsole, configuration.logToFile, configuration.logFile, logging.DEBUG)
        self.mLogger = LogManager.getLogger('Distributor')
        self.mId = Aux.getApplicationId()
        self.mStartTime = Aux.timestampStr()
        self.mLocalIpAddress = Aux.getIpAddress('')
        self.mLogger.info("==== Distributor [{}] Started at {} ID {} ====".format(configuration.applName, Aux.timestampStr(), self.mApplId))

    def createConnection(self, configuration: ConnectionConfiguration ) -> DistributorConnection:
        return DistributorConnection( self, configuration)

    def createPublisher(self, connection: DistributorConnection) -> Publisher:
        pass

    def createSubscriber( self, connection: DistributorConnection) -> Subscriber:
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