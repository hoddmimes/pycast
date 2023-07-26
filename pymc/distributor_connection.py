import threading

from aux import Aux
from aux import PCLogger
from aux import BlockingQueue
from distributor import Distributor
from ipmc import IPMC

class ConnectionConfiguration:

    def __init__(self, mca:str='224.44.44.44', mca_port:int=4444, eth_device=''):
        self.ttl = 32
        self.mca = mca
        self.mca_port= mca_port
        self.eth_device = eth_device

        self.ipBufferSize = 128000
        self.segment_size = 8192
        self.smallsegment_size = 512

        self.configuration_interval_ms = 15000
        self.configuration_max_lost = 3

        self.heartbeat_interval_ms = 3000
        self.heartbeat_max_lost = 10

        self.max_bandwidth_bytes = 0
        self.retrans_server_holdback_ms = 20
        self.retrans_timeout_ms = 800
        self.retrans_max_retries = 10
        self.retrans_max_cache_bytes = 10000000
        self.retrans_cache_life_time_sec = 60
        self.retrans_cache_clean_interval_sec = 2

        self.flow_rate_calculate_interval_ms = 100

        self.send_holdback_delay_ms = 0
        self.send_holdback_threshold = 100

        self.fake_xta_error_rate = 0
        self.fake_rcv_error_rate = 0

        self.nagging_window_interval_ms = 4000
        self.nagging_check_interval_ms = 60000

        self.statistic_interval_sec = 0


class DistributorConnection:
    STATE_INIT = 0
    STATE_RUNNING = 1
    STATE_CLOSED = 2
    STATE_ERROR = 3

    def __init__(self,  distributor, configuration: ConnectionConfiguration):
        self.distributor = distributor
        self.configuration = configuration
        self.logger: PCLogger = self.distributor.getLogger( __name__)
        self.state = self.STATE_INIT
        self.mutex = threading.RLock()
        self.asyncEventQueue = BlockingQueue()
        self.ipmc = IPMC( configuration.eth_device, configuration.ttl, configuration.ipBufferSize)
        self.ipmc.open( configuration.mca, configuration.mca_port )



    def mcaReadComplete(self, data, addr):
        pass


    def mcaReadException(self, exception: Exception):
        self.logger.fatal("MCA {} read exception {}".format( self.toString(), str(exception)))

    def toString(self) -> str:
        return "mca: " + self.configuration.mca + " mca_port: " + str(self.configuration.mca_port)
class Publisher:

    def __init__(self, distributor: Distributor, connection: DistributorConnection):
        self.distributor = distributor
        self.connection = connection

class Subscriber:
    def __init__(self, distributor: Distributor, connection: DistributorConnection):
        self.distributor = distributor
        self.connection = connection