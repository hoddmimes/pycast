from pymc.event_api.events_to_clients import DistributorEvent
from pymc.event_loop import ConnectionEvent


class EventNotificationToClient(ConnectionEvent):

    def __init__(self, notification_event: DistributorEvent):
        super().__init__( ConnectionEvent.API_EVENT)
        self._event_to_client = notification_event


    @property
    def notification_event(self) -> DistributorEvent:
        return self._event_to_client


