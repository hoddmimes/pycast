from __future__ import annotations
from abc import ABC, abstractmethod
from pymc.event_loop import ConnectionEvent


class ConnectionTimerEvent(ConnectionEvent):

    def __init__(self, connection_id: int):
        super().__init__(ConnectionEvent.TIMER_EVENT)
        self._connection_id = connection_id
        self._canceled = False

    def cancel(self):
        self._canceled = True

    @abstractmethod
    def execute(self, connection: 'Connection'):
        raise Exception("ConnectionTimerEvent implementation must implement the 'execute' method")

    @property
    def connection_id(self) -> int:
        return self._connection_id

    @property
    def canceled(self) -> bool:
        return self._canceled
