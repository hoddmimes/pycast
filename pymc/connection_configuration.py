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


class ConnectionConfiguration():

    def __init__(self, mca:str='224.44.44.44', mca_port:int=4444, eth_device=''):
        self.ttl = 32
        self.mca = mca
        self.mca_port= mca_port
        self.eth_device = eth_device
        self.sender_id_port = 0
        self.sender_id_port_offset = 61234

        self.ipBufferSize = 128000
        self.segment_size = 8192
        self.small_segment_size = 512

        self.configuration_interval_ms = 15000
        self.configuration_max_lost = 3

        self.heartbeat_interval_ms = 3000
        self.heartbeat_max_lost = 10


        self.retrans_server_holdback_ms = 20
        self.retrans_timeout_ms = 800
        self.retrans_max_retries = 10
        self.retrans_max_cache_bytes = 10000000
        self.retrans_cache_life_time_sec = 60
        self.retrans_cache_clean_interval_sec = 2

        self.max_bandwidth_kbit = 0
        self.max_bandwidth_calc_interval_ms = 100

        self.send_holdback_delay_ms = 0             # if update rate is over threshold apply holdback
        self.send_holdback_threshold = 100          # max updates per calc_interval
        self.send_holdback_calc_interval_ms = 100   # calc update rate interval

        self.fake_xta_error_rate = 0 # promille,  number of errors in 1000 msgs
        self.fake_rcv_error_rate = 0 # promille,  number of errors in 1000 msgs

        self.nagging_window_interval_ms = 4000
        self.nagging_check_interval_ms = 60000
        self.nagging_max_retransmit = 200

        self.statistic_interval_sec = 0

        self.receiver_threads = 1