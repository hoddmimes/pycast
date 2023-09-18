from typing import Callable

from pymc.event_loop import ConnectionEvent


class EventApiCreatePublisher(ConnectionEvent):

    def __init__(self, event_callback: Callable[['DistributorEvent'], None]):
        super().__init__(ConnectionEvent.API_EVENT)
        self._event_callback = event_callback

    @property
    def event_callback(self) -> Callable[['DistributorEvent'], None] | None:
        return self._event_callback


    def __str__(self):
        return "event_callback: {}".format( self._event_callback)

