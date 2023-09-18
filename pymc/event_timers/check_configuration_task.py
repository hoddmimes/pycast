from pymc.client_controller import ClientDeliveryController
from pymc.distributor_configuration import DistributorLogFlags
from pymc.event_api.events_to_clients import DistributorRemoveRemoteConnectionEvent
from pymc.event_timers.connection_timer_event import ConnectionTimerEvent


class CheckConfigurationTask(ConnectionTimerEvent):
    def __init__(self, connection_id, remote_connection_id):
        super().__init__(connection_id)
        self._remote_connection_id = remote_connection_id

    def execute(self, connection: 'Connection'):
        _remote_connection: 'RemoteConnection' = connection.connection_receiver.get_remote_connection_by_id(self._remote_connection_id)
        if _remote_connection == None:
            self.cancel()
            return
        try:
            if _remote_connection.is_dead:
                self.cancel()
                return
            if connection.is_time_to_die:
                self.cancel()
                return
            if not _remote_connection.is_configuration_active:
                _remote_connection.is_dead = True
                connection.connection_receiver.remove_remote_connection(_remote_connection)
                if connection.is_logging_enabled(DistributorLogFlags.LOG_RMTDB_EVENTS):
                    connection.log_info("Remote connction disconnected (no configuration heartbeats) \n {}"
                                        .format(_remote_connection))

                tEvent = DistributorRemoveRemoteConnectionEvent(source_addr=_remote_connection.remote_host_address,
                                                                sender_id=_remote_connection.remote_sender_id,
                                                                mc_addr=_remote_connection.mc_address,
                                                                mc_port=_remote_connection.mc_port,
                                                                appl_name=_remote_connection.remote_application_name,
                                                                appl_id=_remote_connection.remote_application_id)
                ClientDeliveryController.get_instance().queue_event(connection.connection_id, tEvent)
                self.cancel()
            else:
                _remote_connection.is_configuration_active = False
        except Exception as e:
            connection.log_exception(e)
