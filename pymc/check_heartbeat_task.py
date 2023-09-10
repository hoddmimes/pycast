from __future__ import annotations

from pymc.client_controller import ClientDeliveryController
from pymc.connection_timers import ConnectionTimerTask
from pymc.distributor_events import DistributorRemoveRemoteConnectionEvent
from pymc.distributor_configuration import DistributorLogFlags



class CheckHeartbeatTask(ConnectionTimerTask):
    def __init__(self, connection_id: int , remote_connection_id: int):
        super().__init__(connection_id)
        self._remote_connection_id = remote_connection_id

    def execute(self, connection: 'Connection'):
        _remote_connection: 'RemoteConnection' = connection.get_remote_connection_by_id(self._remote_connection_id)
        if _remote_connection is None:
            self.cancel()
            return
        try:
            if _remote_connection.is_dead:
                self.cancel()
                return
            if connection.is_time_to_die:
                self.cancel()
                return
            if not _remote_connection.is_heartbeat_active:
                if connection.is_logging_enabled(DistributorLogFlags.LOG_RMTDB_EVENTS):
                    connection.log_info("Remote connection disconnected (no heartbeats) \n {}".format(_remote_connection))
                _event = DistributorRemoveRemoteConnectionEvent(_remote_connection.remote_host_address,
                                                                _remote_connection.remote_sender_id,
                                                                _remote_connection.mc_address,
                                                                _remote_connection.mc_port,
                                                                _remote_connection.remote_application_name,
                                                                _remote_connection.remote_application_id)
                ClientDeliveryController.get_instance().queue_event(connection.connection_id, _event)
                self.cancel()
                from pymc.remote_connection_controller import RemoteConnectionController
                RemoteConnectionController.removeRemoteConnection(self)
            else:
                _remote_connection.is_heartbeat_active = False
        except Exception as e:
            connection.log_exception(e)