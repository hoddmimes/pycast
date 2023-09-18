from logging import Logger
from pymc.aux.aux import AuxThread, Aux
from pymc.aux.distributor_exception import DistributorException
from pymc.event_api.event_api_notification import EventNotificationToClient
from pymc.event_api.events_to_clients import DistributorCommunicationErrorEvent, AsyncEventSignalEvent, AsyncEventReceiveSegment
from pymc.connection_controller import ConnectionController
from pymc.event_msgs.event_msg_rcv_data import EventMsgInboundMessage
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

                _notification_event: EventNotificationToClient = EventNotificationToClient( _event )
                ConnectionController.get_instance().schedule_async_event(self._connection_id, _notification_event)
                return


            # Normal read complete, deliver data
            _data_event: EventMsgInboundMessage = EventMsgInboundMessage(_data, _mc_addr, _mc_port)
            ConnectionController.get_instance().schedule_async_event(self._connection_id, _data_event)

