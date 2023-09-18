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
    LOG_TRAFFIC_FLOW_EVENTS = 1024
    LOG_EVENT_LOOP_API = 2048
    LOG_EVENT_LOOP_MSGS = 4096
    LOG_EVENT_LOOP_TIMERS = 8192
    LOG_EVENT_LOOP_ALL = LOG_EVENT_LOOP_TIMERS + LOG_EVENT_LOOP_MSGS + LOG_EVENT_LOOP_API
    LOG_DEFAULT_FLAGS = LOG_ERROR_EVENTS + LOG_CONNECTION_EVENTS + LOG_RETRANSMISSION_EVENTS


class DistributorConfiguration(object):

    def __init__(self, application_name: str):
        self.app_name = application_name
        self.log_flags = DistributorLogFlags.LOG_DEFAULT_FLAGS
        self.log_to_console = True
        self.log_to_file = True
        self.log_file = 'Distributor.log'
        self.eth_device = None
