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
from pymc.msg.segment import Segment

class XtaSegment(Segment):

    def __init__(self, bufferSize:int):
        super().__init__( bufferSize )
        self._allocated_buffer_size = bufferSize

    @property
    def size(self) -> int:
        return self.length

    @property
    def buffer_allocation_size(self) -> int:
        return self._allocated_buffer_size

    @classmethod
    def cast(cls, obj: object) -> XtaSegment:
        if isinstance( obj, XtaSegment):
            return obj
        raise Exception('Can not cast object to {}'.format( cls.__name__))