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

from pymc.connection_timer_task import ConnectionTimerTask
from pymc.retransmission_cache import RetransQueItm
from pymc.aux.trace import Trace


class QueueRetransmissionListTask(ConnectionTimerTask):
    def __init__(self, connection_id: int, retrans_list: list[RetransQueItm]):
        super().__init__(connection_id)
        self._retrans_list = list(reversed(retrans_list))

    def execute(self, connection: 'Connection', trace: Trace):
        connection.connection_sender.retransmission_cache.send_retransmissions(self._retrans_list)
        self._retrans_list = None
