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

from abc import ABC
from pymc.msg.codec import Encoder, Decoder
from pymc.msg.segment import Segment


class NetMsg(ABC, object):
    IGNORE = 0
    SYNCH = 1
    LOWER = 2
    HIGHER = 3

    VERSION: int = 0x0100

    def __init__(self, segment: Segment):
        self._segment: Segment = segment

    @property
    def segment(self) -> Segment:
        return self._segment

    @property
    def encoder(self) -> Encoder:
        return self._segment.encoder

    @property
    def decoder(self) -> Decoder:
        return self._segment.decoder

    def setHeader(self, message_type: int, segment_flags: int, local_address: int, sender_id: int,
                  sender_start_time_sec: int, app_id: int):
        self._segment.setHeader(NetMsg.VERSION, message_type, segment_flags, local_address, sender_id,
                                sender_start_time_sec, app_id)

    @property
    def hdr_segment_flags(self) -> int:
        return self._segment.hdr_segment_flags



    @hdr_segment_flags.setter
    def hdr_segment_flags(self, value: int):
        self._segment.encoder.putByteAt(Segment.HDR_OFFSET_MSG_FLAGS, value)
        self._segment.hdr_segment_flags = value

    @property
    def hdr_msg_type(self) -> int:
        return self._segment.hdr_msg_type

    @hdr_msg_type.setter
    def hdr_msg_type(self, value: int):
        self._segment.hdr_msg_type = value

    @property
    def hdr_local_address(self) -> int:
        return self._segment.hdr_local_address

    @property
    def hdr_sender_start_time_sec(self):
        return self._segment.hdr_sender_start_time_sec

    @property
    def hdr_app_id(self):
        return self._segment.hdr_app_id

    def encode(self) -> Encoder:
        self._segment.encode()
        return self._segment.encoder

    def decode(self) -> Decoder:
        self._segment.decode()
        return self._segment.decoder

    def __str__(self) -> str:
        return self._segment.__str__()
