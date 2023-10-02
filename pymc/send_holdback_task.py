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

from pymc.connection_timers import ConnectionTimerExecutor, ConnectionTimerTask
from pymc.aux.trace import Trace



class SenderHoldbackTimerTask(ConnectionTimerTask):

    def __init__(self, connection_id: int, flush_seqno: int):
        super().__init__(connection_id)
        self._timer_flush_seqno = flush_seqno

    def execute(self, connection: 'Connection', trace: Trace):
        connection.flush_holdback(self._timer_flush_seqno)
