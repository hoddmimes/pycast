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



class DistributorLogFlags:
    LOG_ERROR_EVENTS = 1
    LOG_CONNECTION_EVENTS = 2
    LOG_RMTDB_EVENTS = 4
    LOG_RETRANSMISSION_EVENTS = 8
    LOG_SUBSCRIPTION_EVENTS = 16
    LOG_STATISTIC_EVENTS = 32
    LOG_SEGMENTS_EVENTS = 64
    LOG_DATA_PROTOCOL_RCV = 128;
    LOG_DATA_PROTOCOL_XTA = 256
    LOG_RETRANSMISSION_CACHE = 512
    LOG_TRAFFIC_FLOW_EVENTS = 1024
    LOG_DEFAULT_FLAGS = LOG_ERROR_EVENTS + LOG_CONNECTION_EVENTS + LOG_RETRANSMISSION_EVENTS


class DistributorConfiguration(object):

    def __init__(self, application_name: str):
        self.trace_enabled = False
        self.print_limit_usec = 3000
        self.app_name = application_name
        self.log_flags = DistributorLogFlags.LOG_DEFAULT_FLAGS
        self.log_to_console = True
        self.log_to_file = True
        self.log_file = 'Distributor.log'
        self.eth_device = None
        self.web_interface = True
        self.web_port = 8888
