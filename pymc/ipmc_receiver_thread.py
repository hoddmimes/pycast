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

from logging import Logger
from pymc.aux.aux import AuxThread, Aux
from pymc.aux.distributor_exception import DistributorException
from pymc.distributor_events import DistributorCommunicationErrorEvent, AsyncEventSignalEvent, AsyncEventReceiveSegment
from pymc.connection_controller import ConnectionController
from pymc.ipmc import IPMC
from pymc.msg.rcv_segment import RcvSegment


class IpmcReceiverThread(AuxThread):
    def __init__(self, logger: Logger, ipmc: IPMC, connection_id: int, index: int, segment_size: int):
        super().__init__()
        self._ipmc = ipmc
        self._index = index
        self._logger  = logger
        self._segment_size = segment_size
        self._connection_id = connection_id

    def run(self):
        _data_addr = None
        self.name = "DIST_RECEIVER_{}:{}".format(self._index, Aux.ip_addr_int_to_str(self._ipmc.mc_address))
        while True:
            _byte_buffer = bytearray(self._segment_size)
            try:
                _data_addr = self._ipmc.read()
                _data = _data_addr[0]
                _mc_addr = _data_addr[1][0]
                _mc_port = _data_addr[1][1]
            except Exception as e:
                if self.is_stopped:
                    return

                e = DistributorException("IPMC read failure", e)
                self._logger.exception( e )
                _event = DistributorCommunicationErrorEvent("[RECEIVE]",
                                                            self._ipmc.mc_address,
                                                            self._ipmc.mc_port,
                                                            str(e))
                _async_event = AsyncEventSignalEvent(_event)
                ConnectionController.get_instance().queue_async_event(self._connection_id, _async_event)
                return


            # Normal read complete, check connection status and deliver data
            _rcv_segment = RcvSegment(_data)
            _rcv_segment.from_address = _mc_addr
            _rcv_segment.from_port = _mc_port
            _rcv_segment.decode()
            _async_event :AsyncEventReceiveSegment = AsyncEventReceiveSegment(_rcv_segment)
            ConnectionController.get_instance().queue_async_event(self._connection_id, _async_event)
