class DistributorLogFlags:
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
        self.logFlags = DistributorLogFlags.LOG_DEFAULT_FLAGS
        self.logToConsole = True
        self.logToFile = True
        self.logFile = 'Distributor.log'
        self.ethDevice = None
