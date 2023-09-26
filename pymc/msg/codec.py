import importlib
import struct
from abc import ABC

from pymc.msg.messageif import MessageBase


########################################################################################################################
#   Encoder
########################################################################################################################

class Codec(ABC, object):

    def __init__(self, *args):
        if isinstance(args[0], int):
            self._buffer = bytearray(args[0])
            self._size = args[0]
            self._pos = 0
        elif isinstance(args[0], bytearray) or isinstance(args[0], bytes):
            self._buffer = args[0]
            self._pos = 0
            self._size = len(args[0])

    def getBoolAt(self, offset: int) -> bool:
        if self._buffer[offset] == 1:
            return True
        else:
            return False

    def getByteAt(self, offset: int) -> int:
        return self._buffer[offset]

    def getShortAt(self, offset: int) -> int:
        _value = int.from_bytes(self._buffer[offset: offset + 2], 'big')
        return _value

    def getIntAt(self, offset: int) -> int:
        _value = int.from_bytes(self._buffer[offset: offset + 4], 'big')
        return _value

    def getLongAt(self, offset: int) -> int:
        _value = int.from_bytes(self._buffer[offset: offset + 8], 'big')
        return _value

    def getFloatAt(self, offset: int) -> float:
        _value = struct.unpack('f', self._buffer[offset:offset + 4])
        return _value[0]

    def getDoubleAt(self, offset: int) -> float:
        _value = struct.unpack('d', self._buffer[offset:offset + 8])
        return _value[0]

    def getStringAt(self, offset: int) -> str | None:
        if not self.getBoolAt(offset):
            return None
        _size = self.getShortAt(offset + 1)
        _bytarr = self._buffer[offset + 3:offset + 3 + _size]
        return _bytarr.decode()

    def getBytesAt(self, offset) -> bytearray | None:
        if self.getBoolAt(offset):
            return None

        _size = self.getIntAt(offset + 1)
        _bytarr = self._buffer[offset + 5: offset + 5 + _size]
        return _bytarr

    def putBoolAt(self, offset: int, value: bool):
        if value:
            self._buffer[offset] = 1
        else:
            self._buffer[offset] = 0

    def putByteAt(self, offset: int, value: int):
        self._buffer[offset] = value

    def putShortAt(self, offset: int, value: int):
        bytarr = value.to_bytes(2, byteorder='big')
        for i in range(2):
            self._buffer[offset + i] = bytarr[i]

    def putIntAt(self, offset: int, value: int):
        bytarr = value.to_bytes(4, byteorder='big')
        for i in range(4):
            self._buffer[offset + i] = bytarr[i]

    def putLongAt(self, offset: int, value: int):
        bytarr = value.to_bytes(8, byteorder='big')
        for i in range(8):
            self._buffer[offset + i] = bytarr[i]

    def putFloatAt(self, offset: int, value: float):
        bytarr = bytearray(struct.pack("f", value))
        for i in range(4):
            self._buffer[offset + i] = bytarr[i]

    def putDoubleAt(self, offset: int, value: float):
        bytarr = bytearray(struct.pack("d", value))
        for i in range(8):
            self._buffer[offset + i] = bytarr[i]

    def putStringAt(self, offset: int, value: str):

        if value is None:
            self._buffer[offset] = 0
            return

        _strlen = len(value)
        self.putBoolAt(offset, True)
        self.putShortAt(offset + 1, _strlen)
        bytarr = bytearray(value, 'utf-8')
        for i in range(len(bytarr)):
            self._buffer[offset + 3 + i] = bytarr[i]

    def putBytesAt(self, offset: int, data: bytearray, data_size: int):

        if data is None:
            self.putBoolAt(offset, False)
            return

        self.putBoolAt(offset, True)
        self.putIntAt(offset + 1, data_size)
        self._buffer[offset + 5:] = data[:data_size]

    @property
    def size(self):
        return self._size


class Encoder(Codec):
    def __init__(self, size=1024):
        super().__init__(size)

    def _capacity_(self, size: int):
        if (self._size - self._pos) >= size:
            return
        else:
            new_size = self._size + 512
            while new_size < (self._pos + size):
                new_size += 512
            new_buffer = bytearray(new_size)
            new_buffer[:] = self._buffer
            self._buffer = new_buffer
            self._size = new_size

    def addBool(self, value: bool):
        self._capacity_(1)
        if value:
            self._buffer[self._pos] = 1
        else:
            self._buffer[self._pos] = 0
        self._pos += 1

    def addByte(self, value: int):
        self._capacity_(1)
        self._buffer[self._pos] = value
        self._pos += 1

    def addShort(self, value: int):
        self._capacity_(2)
        bytarr = value.to_bytes(2, byteorder='big')
        for i in range(2):
            self._buffer[self._pos + i] = bytarr[i]
        self._pos += 2

    def addInt(self, value: int):
        self._capacity_(4)
        bytarr = value.to_bytes(4, byteorder='big')
        for i in range(4):
            self._buffer[self._pos + i] = bytarr[i]
        self._pos += 4

    def addLong(self, value: int):
        self._capacity_(8)
        bytarr = value.to_bytes(8, byteorder='big')
        for i in range(8):
            self._buffer[self._pos + i] = bytarr[i]
        self._pos += 8

    def addFloat(self, value: float):
        self._capacity_(4)
        bytarr = bytearray(struct.pack("f", value))
        for i in range(4):
            self._buffer[self._pos + i] = bytarr[i]
        self._pos += 4

    def addDouble(self, value: float):
        self._capacity_(8)
        bytarr = bytearray(struct.pack("d", value))
        for i in range(8):
            self._buffer[self._pos + i] = bytarr[i]
        self._pos += 8

    def addString(self, value: str):

        if value is None:
            self._capacity_(1)
            self.addBool(False)
            return

        _size = (3 + len(value))
        self._capacity_(_size)
        self.addBool(True)
        self.addShort(len(value))

        if len(value) > 0:
            _bytarr = bytearray(value, 'utf-8')
            self._buffer[self._pos: self._pos + len(_bytarr)] = _bytarr
            self._pos += len(_bytarr)

    def addBytes(self, value: bytes, size: int = None):
        if value is None:
            self._capacity_(1)
            self.addBool(False)
            return

        if size is None:
            _size = (5 + len(value))
        else:
            _size = (5 + size)

        self._capacity_(_size)
        self.addBool(True)
        self.addInt(_size - 5)

        if len(value) > 0:
            self._buffer[self._pos: self._pos + len(value)] = value
            self._pos += len(value)

    def addMessage(self, msg: MessageBase):
        if msg is None:
            self._capacity_(1)
            self.addBool(False)
            return

        _bytarr = msg.encode()
        _size = (5 + len(_bytarr))
        self._capacity_(_size)
        self.addBool(1)
        self.addInt(len(_bytarr))
        self._buffer[self._pos:self._pos + len(_bytarr)] = _bytarr
        self._pos += len(_bytarr)

    @property
    def remaining(self) -> int:
        return len(self._buffer) - self._pos

    @property
    def length(self) -> int:
        return self._pos

    @property
    def buffer(self) -> bytearray:
        return self._buffer[:self._pos]

    def reset(self):
        self._pos = 0

    def addRaw(self, buffer: bytes):
        self._buffer[self._pos: self._pos + len(buffer)] = buffer
        self._pos += len(buffer)


########################################################################################################################
#   Decoder
########################################################################################################################

class Decoder(Codec):

    def __init__(self, buffer: bytes):
        super().__init__(buffer)

    def getBool(self) -> bool:
        if self._buffer[self._pos] == 1:
            self._pos += 1
            return True
        else:
            self._pos += 1
            return False

    def getByte(self) -> int:
        value = self._buffer[self._pos]
        self._pos += 1
        return value

    def getShort(self) -> int:
        value = int.from_bytes(self._buffer[self._pos: self._pos + 2], 'big')
        self._pos += 2
        return value

    def getInt(self) -> int:
        value = int.from_bytes(self._buffer[self._pos: self._pos + 4], 'big')
        self._pos += 4
        return value

    def getLong(self) -> int:
        value = int.from_bytes(self._buffer[self._pos: self._pos + 8], 'big')
        self._pos += 8
        return value

    def getFloat(self) -> float:
        value = struct.unpack('f', self._buffer[self._pos:self._pos + 4])
        self._pos += 4
        return value[0]

    def getDouble(self) -> float:
        value = struct.unpack('d', self._buffer[self._pos:self._pos + 8])
        self._pos += 8
        return value[0]

    def getString(self) -> str | None:
        if not self.getBool():
            return None
        _size = self.getShort()
        if _size == 0:
            return ''

        _bytarr = self._buffer[self._pos:self._pos + _size]
        self._pos += _size
        return _bytarr.decode()

    def getBytes(self) -> bytearray | None:
        if not self.getBool():
            return None
        _size = self.getInt()
        if _size == 0:
            return bytearray(0)

        _bytarr = self._buffer[self._pos:self._pos + _size]
        self._pos += _size
        return _bytarr

    @property
    def length(self):
        return len(self._buffer)

    def reset(self):
        self._pos = 0

    def getRaw(self, size: int):
        _bytarr = self._buffer[self._pos:self._pos + size]
        self._pos += size
        return _bytarr

    def getMessage(self) -> MessageBase|None:
        if not self.getBool():
            return None

        _size = self.getInt()  # get message instance size

        _bytarr = self._buffer[self._pos:self._pos + _size]
        self._pos += _size

        _cls_tuple = self._getMsgClassModuleAndName(_bytarr)
        _msg: MessageBase = self._createMessageInstance(class_module=_cls_tuple[0], class_name=_cls_tuple[1])
        _msg.decode(_bytarr)
        return _msg

    def _createMessageInstance(self, class_module: str, class_name:str) -> MessageBase:
        _classModule = importlib.import_module(class_module)
        _clazz = getattr(_classModule, class_name)
        _instance: MessageBase = _clazz()
        return _instance

    def _getMsgClassModuleAndName(self, buffer: bytearray) -> tuple:
        _pos: int = 0
        if buffer[_pos] == 1:
            _pos += 1
            _size = int.from_bytes(buffer[_pos:_pos + 2], 'big')
            _pos += 2
            _bytarr = buffer[_pos:_pos + _size]
            _class_module = _bytarr.decode()
            _pos += _size
        if buffer[_pos] == 1:
            _pos += 1
            _size = int.from_bytes(buffer[_pos:_pos + 2], 'big')
            _pos += 2
            _bytarr = buffer[_pos:_pos + _size]
            _class_name = _bytarr.decode()

        return (_class_module, _class_name)

    @property
    def remaining(self):
        return len(self._buffer) - self._pos

    @property
    def buffer(self) -> bytearray:
        return self._buffer

    @property
    def pos(self):
        return self._pos
