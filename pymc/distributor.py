from __future__ import annotations

import sys
import logging
from pymc.aux.aux import Aux
from pymc.aux.aux_uuid import Aux_UUID
from pymc.aux.distributor_exception import DistributorException
from pymc.aux.log_manager import LogManager
from pymc.distributor_configuration import DistributorConfiguration
from pymc.connection_configuration import ConnectionConfiguration
from pymc.connection_controller import ConnectionController


class Distributor(object):
    _instance = None

    def __init__(self, application_name: str, configuration: DistributorConfiguration = None):
        self._aux_uuid: Aux_UUID = Aux_UUID()
        self._configuration: DistributorConfiguration = configuration or DistributorConfiguration(application_name)
        LogManager.set_configuration(self.configuration.log_to_console,
                                     self.configuration.log_to_file,
                                     self.configuration.log_file,
                                     logging.DEBUG)

        self._logger: logging.Logger = LogManager.get_instance().get_logger('Distributor')
        self._id: int = Aux.get_application_id()
        self._start_time_string: str = Aux.datetime_string()
        self._local_address_string: str = Aux.getIpAddress('')
        self._local_address: int = Aux.ip_addr_str_to_int(self._local_address_string)
        self._logger.info("==== Distributor [{}] Started at {} ID {} local address: {} ====".
                          format(self.configuration.app_name, self._start_time_string, hex(self._id),
                                 self._local_address_string))
        if Distributor._instance is None:
            self._instance = self
        else:
            raise DistributorException("Distributor instance is already instantiated")

    @staticmethod
    def get_instance() -> Distributor:
        if Distributor._instance is None:
            raise DistributorException("Distributor is not yet instantiated, is that possible")
        return Distributor._instance

    def create_connection(self, configuration: ConnectionConfiguration) -> 'Connection':
        return ConnectionController.get_instance().create_connection(connection_configuration=configuration)

    def create_publisher(self, connection: 'Connection') -> 'Publisher':
        pass

    def create_subscriber(self, connection: 'Connection') -> 'Subscriber':
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
