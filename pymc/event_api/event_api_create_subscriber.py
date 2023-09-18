from typing import Callable

from pymc.event_loop import ConnectionEvent


class EventApiCreateSubscriber(ConnectionEvent):

    def __init__(self,
                 event_callback: Callable[['DistributorEvent'], None],
                 update_callback: Callable[[str, bytes, object, int, int], None]):
        super().__init__(ConnectionEvent.API_EVENT)
        self._event_callback = event_callback
        self._update_callback = update_callback

    @property
    def event_callback(self) -> Callable[['DistributorEvent'], None] | None:
        return self._event_callback

    @property
    def update_callback(self) -> Callable[[str, bytes, object, int, int], None] | None:
        return self._update_callback


    def __str__(self):
        return ("event_callback: {} update_callback {}"
                .format( self._event_callback, self._update_callback))

