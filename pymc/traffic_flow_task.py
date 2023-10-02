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

import random
import sys
import threading
from time import perf_counter
import threading

from pymc.connection_timers import ConnectionTimerTask, ConnectionTimerExecutor
from pymc.aux.aux import Aux
from pymc.aux.trace import Trace

'''
# The TrafficFlow Task is monitoring and regulator the traffic flow i.e. update/sec
# and bits/sec. The flow task is recalculate the rates periodically 'recalc_interval_ms'
# the key method is calculateWaitTime which called each time an update is to be published
# This method will ensure that we do not exceed the 'max_bandwidth_kbit' (per intervall).
'''


class TrafficFlowTask(ConnectionTimerTask):

    def __init__(self, connection_id: int, recalc_interval_ms: int, max_bandwidth_kbit_sec: int):
        super().__init__(connection_id)

        self._mutex: threading.Lock = threading.Lock()
        self._max_bandwidth_kbit_sec: int = max_bandwidth_kbit_sec  # same bandwidth limitation, if 0 flow regulation is off
        self._recalc_interval_ms: int = recalc_interval_ms

        self._interval_factor: float = 1000.0 / recalc_interval_ms

        self._bits_rate_increment: int = 0  # number bits published in the interval
        self._updates_increment: int = 0  # number of updates published in the interval

        self._last_recalc_timestamp = perf_counter()
        self._last_relative_time_factor: float = 1.0
        self._max_bandwith_within_interval: int = int((max_bandwidth_kbit_sec * 1024) / self._interval_factor)

    def execute(self, connection: 'Connection', trace: Trace):
        with self._mutex:
            _real_time_ms: float = (perf_counter() - self._last_recalc_timestamp) * 1000.0
            self._last_relative_time_factor = _real_time_ms / float(self._recalc_interval_ms)
            self._bits_rate_increment = 0
            self._updates_increment = 0
            self._last_recalc_timestamp = perf_counter()




    def increment(self, segment_size: int):
        self._bits_rate_increment += float(segment_size * 8)
        self._updates_increment += 1

    # get current update rate / sec
    def get_update_rate(self) -> int:
        update_rate_per_sec: int = int(float(self._updates_increment * self._interval_factor) * self._last_relative_time_factor)
        return update_rate_per_sec

    '''
    # This method if called if flow regulation is enabled i.e. max_bandwidth_kbits != 0
    # The method is called each time after a segment has been published. It will calculate
    # if the flow rate has been exceeded and if so how long the send flow should be delayed
    # inorder not to exceed the max bandwidth
    '''

    @property
    def calculate_wait_time_ms(self) -> int:
        with self._mutex:
            # If bandwidth control is not enforced just return wait time eq zero
            if self._max_bandwidth_kbit_sec == 0:
                return 0

            if self._bits_rate_increment > (self._max_bandwith_within_interval * self._last_relative_time_factor):
                # Bandwidth is exceeded, calculate suspend time
                _ratio: float = float(self._bits_rate_increment) / (
                        float(self._max_bandwith_within_interval) * self._last_relative_time_factor)
                _wait_time: float = float(self._recalc_interval_ms) * _ratio
                ''''
                print("increment: {} max-in-interval: {} wait-ms: {} ratio:{} relative-time-factor{}".format( self._bits_rate_increment,
                    int(float(self._max_bandwith_within_interval) * self._last_relative_time_factor),
                	int(_wait_time), _ratio, self._last_relative_time_factor))
                '''
                return int(_wait_time)
            else:
                return 0


'''
# ========================================
#     Test
# ========================================
'''


def test_bandwidth():
    flow_task = TrafficFlowTask(connection_id=0, recalc_interval_ms=100, max_bandwidth_kbit_sec=256)
    ConnectionTimerExecutor.getInstance().queue(interval=flow_task._recalc_interval_ms, task=flow_task, repeat=True)

    _startTime = Aux.current_milliseconds()
    _tot_bytes = 0
    for i in range(100):
        _bytes = random.randrange(start=100, stop=8192)
        flow_task.increment(_bytes)
        _tot_bytes += _bytes
        wt = flow_task.calculate_wait_time_ms
        if wt > 0:
            print('loop: {} wait: {}'.format(i, wt))
            Aux.sleep_ms(wt)

    _rate = float((_tot_bytes * 8 * 1000) / (Aux.current_milliseconds() - _startTime)) / 1024.0
    print('kbit-rate: {} '.format(_rate))
    sys.exit()

def test_holdback():
    flow_task = TrafficFlowTask(connection_id=0, recalc_interval_ms=100, max_bandwidth_kbit_sec=0)
    ConnectionTimerExecutor.getInstance().queue(interval=flow_task._recalc_interval_ms, task=flow_task, repeat=True)

    _startTime = Aux.current_milliseconds()
    _tot_bytes = 0

    for x in range(10000):
        for i in range(4):
            flow_task.increment(64)
        Aux.sleep_ms(10)
        if (x % 40) == 0:
            print("updates {} update-rate {}".format( x, flow_task.get_update_rate()))



    sys.exit()

if __name__ == '__main__':
    # test_bandwidth()
    test_holdback()
