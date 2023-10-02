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

from __future__ import annotations
from abc import ABC, abstractmethod


class ConnectionTimerTask(ABC):

    def __init__(self, connection_id):
        self._connection_id = connection_id
        self._canceled = False

    def cancel(self):
        self._canceled = True

    @abstractmethod
    def execute(self, connection, trace_context):
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