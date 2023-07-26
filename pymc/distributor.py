from aux import PCLogger
from aux import Aux

from distributor_connection import DistributorConnection
from distributor_connection import Publisher
from distributor_connection import Subscriber
from distributor_connection import ConnectionConfiguration


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

class Distributor:

    def __init__(self, application_name: str, configuration: DistributorConfiguration = None):
        self.configuration = configuration or DistributorConfiguration( application_name )
        self.logger = self.getLogger(__name__)
        self.applId = Aux.getUUID()
        self.logger.info("==== Distributor [{}] Started at {} ID {} ====".format(configuration.applName,Aux.timestampStr(), self.applId))


    def getLogger(self, module:str) ->PCLogger:
        _logger = PCLogger( __name__, fileName= self.configuration.logFile, logFlags= self.configuration.logFlags )
        _logger.toConsole = self.configuration.logToConsole
        _logger.toFile = self.configuration.logToFile
        return _logger

    def createConnection(self, configuration: ConnectionConfiguration ) -> DistributorConnection:
        return DistributorConnection( self, configuration)

    def createPublisher(self, connection: DistributorConnection) -> Publisher:
        return Publisher( self, connection )

    def createSubscriber( self, connection: DistributorConnection) -> Subscriber:
        return Subscriber( self, connection )