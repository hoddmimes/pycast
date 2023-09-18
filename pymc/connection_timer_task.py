from __future__ import annotations
from abc import ABC, abstractmethod


class ConnectionTimerTask(ABC):

    def __init__(self, connection_id):
        self._connection_id = connection_id
        self._canceled = False

    def cancel(self):
        self._canceled = True

    @abstractmethod
    def execute(self, connection):
        pass

    @property
    def connection_id(self) -> int:
        return self._connection_id

    @property
    def canceled(self) -> bool:
        return self._canceled

    @classmethod
    def cast(cls, obj: object) -> ConnectionTimerTask:
        if isinstance(obj, ConnectionTimerTask):
            return obj
        else:
            raise Exception("object can no be cast to {}".format(cls.__name__))