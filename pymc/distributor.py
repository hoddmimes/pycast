import sys
import logging
from pymc.aux.aux import Aux
from pymc.aux.aux_uuid import Aux_UUID
from pymc.aux.log_manager import LogManager
from pymc.distributor_interfaces import DistributorBase
from pymc.publisher import Publisher
from pymc.subscriber import Subscriber
from pymc.distributor_configuration import DistributorConfiguration

from pymc.connection_configuration import ConnectionConfiguration
from pymc.connection import Connection


class Distributor(DistributorBase):

    def __init__(self, application_name: str, configuration: DistributorConfiguration = None):
        self._aux_uuid: Aux_UUID = Aux_UUID()
        self._configuration: DistributorConfiguration = configuration or DistributorConfiguration(application_name)
        LogManager.setConfiguration(configuration.log_to_console, configuration.log_to_file, configuration.log_file,
                                    logging.DEBUG)
        self._logger: logging.Logger = LogManager.getLogger('Distributor')
        self._id: int = Aux.getApplicationId()
        self._start_time_string: str = Aux.datetime_string()
        self._local_address_string: str = Aux.getIpAddress('')
        self._local_address: int = Aux.ipAddrStrToInt(self._local_address_string)
        self._logger.info("==== Distributor [{}] Started at {} ID {} local address: {} ====".
                          format(configuration.app_name, self._start_time_string, self._id, self._local_address_string))

    def createConnection(self, configuration: ConnectionConfiguration) -> Connection:
        return Connection(self, configuration)

    def createPublisher(self, connection: Connection) -> Publisher:
        pass

    def createSubscriber(self, connection: Connection) -> Subscriber:
        pass

    @property
    def distributor_id(self) -> int:
        return self._id

    @property
    def app_name(self) -> str:
        return self._configuration.app_name

    @property
    def app_id(self) -> int:
        return Aux.hash32(self.app_name)

    @property
    def start_time_string(self) -> str:
        return self._start_time_string

    @property
    def local_address(self) -> int:
        return self._local_address

    def get_txid(self) -> int:
        return self._aux_uuid.getNextId()

    @property
    def configuration(self) -> DistributorConfiguration:
        return self._configuration

    def is_logging_enable(self, log_flag: int) -> bool:
        if (self._configuration.log_flags & log_flag) != 0:
            return True
        return False
