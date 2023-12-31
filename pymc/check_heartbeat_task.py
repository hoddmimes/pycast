'''
Copyright 2023 Hoddmimes Solutions AB

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from __future__ import annotations

from pymc.client_controller import ClientDeliveryController
from pymc.connection_timers import ConnectionTimerTask
from pymc.distributor_events import DistributorRemoveRemoteConnectionEvent
from pymc.distributor_configuration import DistributorLogFlags
from pymc.aux.trace import Trace


class CheckHeartbeatTask(ConnectionTimerTask):
    def __init__(self, connection_id: int, remote_connection_id: int):
        super().__init__(connection_id)
        self._remote_connection_id = remote_connection_id

    def execute(self, connection: 'Connection', trace: Trace):
        _remote_connection: 'RemoteConnection' = connection.connection_receiver.get_remote_connection_by_id(
            self._remote_connection_id)
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
                    connection.log_info(
                        "Remote connection disconnected (no heartbeats) \n {}".format(_remote_connection))
                _event = DistributorRemoveRemoteConnectionEvent(_remote_connection.remote_host_address,
                                                                _remote_connection.remote_sender_id,
                                                                _remote_connection.mc_address,
                                                                _remote_connection.mc_port,
                                                                _remote_connection.remote_application_name,
                                                                _remote_connection.remote_application_id)
                ClientDeliveryController.get_instance().queue_event(connection.connection_id, _event)
                self.cancel()
                from pymc.remote_connection_controller import RemoteConnectionController
                RemoteConnectionController.remove_remote_connection(_remote_connection)
            else:
                _remote_connection.is_heartbeat_active = False
        except Exception as e:
            connection.log_exception(e)
