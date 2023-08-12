import struct
import importlib
from pymc.msg.messageif import MessageBase as MessageBase




class Decoder:

    def __init__(self, buffer: bytearray):
        self._buffer = buffer
        self._pos = 0

    def getBool(self) -> bool:
        if self._buffer[ self._pos ] == 1:
            self._pos += 1
            return True
        else:
            self._pos += 1
            return False

    def getByte(self) -> int:
        value =  self._buffer[ self._pos ]
        self._pos += 1
        return value

    def getShort(self) -> int:
        value = int.from_bytes( self._buffer[ self._pos: self._pos+2],'big')
        self._pos += 2
        return value

    def getInt(self) -> int:
        value = int.from_bytes( self._buffer[ self._pos: self._pos+4],'big')
        self._pos += 4
        return value

    def getLong(self) -> int:
        value = int.from_bytes( self._buffer[ self._pos: self._pos+8],'big')
        self._pos += 8
        return value

    def getFloat(self) -> float:
       value = struct.unpack('f', self._buffer[ self._pos:self._pos+4])
       self._pos += 4
       return value[0]

    def getDouble(self) -> float:
        value = struct.unpack('d', self._buffer[ self._pos:self._pos+8])
        self._pos += 8
        return value[0]

    def getString(self) -> str:
        if not self.getBool():
            return None
        _size = self.getShort()
        if _size == 0:
            return ''

        _bytarr = self._buffer[ self._pos:self._pos + _size]
        self._pos += _size
        return _bytarr.decode()

    def getBytes(self) -> str:
        if not self.getBool():
            return None
        _size = self.getShort()
        if _size == 0:
            return bytearray(0)

        _bytarr = self._buffer[ self._pos:self._pos + _size]
        self._pos += _size
        return _bytarr

    def getMessage(self) -> MessageBase:
        if not self.getBool():
            return None

        _size = self.getInt() # get message instance size

        _bytarr = self._buffer[ self._pos:self._pos + _size]
        self._pos += _size

        _msgClassPath: str = self._getMsgClassPath(_bytarr)
        _msg: MessageBase = self._createMessageInstance( classPath=_msgClassPath)
        _msg.decode( _bytarr)
        return _msg

    def _createMessageInstance( self, classPath: str) -> MessageBase:
        _classModule = importlib.import_module(classPath)
        _className = classPath[classPath.rfind('.') + 1:]
        _clazz = getattr(_classModule, _className)
        _instance:MessageBase = _clazz()
        return _instance

    def _getMsgClassPath( self, buffer: bytearray) -> str:
        _pos:int = 0
        if buffer[_pos] == 1:
            _pos += 1
            _size = int.from_bytes( buffer[_pos:_pos+2],'big')
            _pos += 2
            _bytarr = buffer[ _pos:_pos + _size]
            _class_name = _bytarr.decode()
            return _class_name
