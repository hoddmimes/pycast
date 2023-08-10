import struct
from abc import ABC

########################################################################################################################
#   Encoder
########################################################################################################################

class Codec(object):

    def __init__(self, *args ):
        if isinstance(args[0], int):
            self._buffer = bytearray( args[0] )
            self._size = args[0]
            self._pos = 0
        elif isinstance(args[0], bytearray):
            self._buffer = args[0]
            self._pos = 0
            self._size = len(args[0])


    def getBoolAt(self, offset) -> bool:
        if self._buffer[ offset ] == 1:
            return True
        else:
            return False
    def getByteAt(self, offset ) -> int:
        return self._buffer[ offset ]

    def getShortAt(self, offset) -> int:
        _value = int.from_bytes( self._buffer[ offset : offset+2],'big')
        return _value
    def getIntAt(self, offset) -> int:
        _value = int.from_bytes( self._buffer[ offset : offset+4],'big')
        return _value

    def getLongAt(self, offset) -> int:
        _value = int.from_bytes( self._buffer[ offset : offset+8],'big')
        return _value

    def getFloatAt(self, offset) -> float:
        _value = struct.unpack('f', self._buffer[ offset:offset+4])
        return _value[0]

    def getDoubleAt(self, offset) -> float:
        _value = struct.unpack('d', self._buffer[ offset:offset+8])
        return _value[0]

    def getStringAt(self, offset):
        if not self.getBoolAt( offset):
            return None
        _size = self.getShortAt( offset + 1)
        _bytarr = self._buffer[ offset + 3:offset + 3 + _size]
        return _bytarr.decode()

    def getBytesAt(self, offset):
        if self.getBoolAt( offset):
            return None

        _size = self.getIntAt( offset + 1 )
        _bytarr = self._buffer[ offset + 5 : offset + 5 + _size]
        return _bytarr

    def putBoolAt(self, offset:int, value:bool):
        if value:
            self._buffer[offset] = 1
        else:
            self._buffer[offset] = 0

    def putByteAt(self, offset: int, value: int ):
        self._buffer[ offset ] = value


    def putShortAt(self, offset: int, value: int ):
        bytarr = value.to_bytes(2, byteorder='big')
        for i in range(2):
            self._buffer[ offset + i] = bytarr[i]


    def putIntAt(self, offset: int, value: int ):
        bytarr = value.to_bytes(4, byteorder='big')
        for i in range(4):
            self._buffer[ offset + i] = bytarr[i]


    def putLongAt(self, offset: int, value: int ):
        bytarr = value.to_bytes(8, byteorder='big')
        for i in range(8):
            self._buffer[ offset + i] = bytarr[i]

    def putFloatAt(self, offset: int, value: float ):
        bytarr = bytearray(struct.pack("f", value))
        for i in range(4):
            self._buffer[ offset + i] = bytarr[i]

    def putDoubleAt(self, offset: int, value: float ):
        bytarr = bytearray(struct.pack("d", value))
        for i in range(8):
            self._buffer[ offset + i] = bytarr[i]

    def putStringAt(self, offset: int, value: str ):

        if value is None:
           self._buffer[offset] = 0
           return

        _strlen = len(value)
        self.putBoolAt(offset,True)
        self.putShortAt(offset+1, _strlen)
        bytarr = bytearray( value, 'utf-8')
        for i in range( len(bytarr)):
            self._buffer[ offset + 3 + i] = bytarr[i]

    def putBytesAt(self, offset: int, data: bytearray, dataSize:int ):

        if data is None:
            self.putBoolAt(offset,False)
            return

        self.putBoolAt(offset,True)
        self.putIntAt( offset + 1, dataSize )
        self._buffer[ offset + 5:] = data[:dataSize]



class Encoder(Codec):
    def __init__(self, size = 1024):
        super.__init__( size )

    def _capacity_(self, size: int):
        #print("pos: " + str( self._pos) + " remaining: " + str( self._size - self._pos) + " requested: " + str( size ))
        if (self._size - self._pos) >= size:
            return
        else:
            newSize = self._size + 512
            while newSize < (self._pos + size):
                newSize += 512
            newBuffer = bytearray( newSize )
            newBuffer[:] = self._buffer
            self._buffer = newBuffer;
            self._size = newSize

    def addBool(self, value: bool):
        self._capacity_(1)
        if value:
            self._buffer[ self._pos ] = 1
        else:
            self._buffer[ self._pos ] = 0
        self._pos += 1

    def addByte(self, value: int ):
        self._capacity_( 1 )
        self._buffer[ self._pos ] = value
        self._pos += 1

    def addShort(self, value: int ):
        self._capacity_( 2 )
        bytarr = value.to_bytes(2, byteorder='big')
        for i in range(2):
            self._buffer[ self._pos + i] = bytarr[i]
        self._pos += 2

    def addInt(self, value: int ):
        self._capacity_( 4 )
        bytarr = value.to_bytes(4, byteorder='big')
        for i in range(4):
            self._buffer[ self._pos + i] = bytarr[i]
        self._pos += 4

    def addLong(self, value: int ):
        self._capacity_( 8 )
        bytarr = value.to_bytes(8, byteorder='big')
        for i in range(8):
            self._buffer[ self._pos + i] = bytarr[i]
        self._pos += 8

    def addFloat(self, value: float ):
        self._capacity_( 4 )
        bytarr = bytearray(struct.pack("f", value))
        for i in range(4):
            self._buffer[ self._pos + i] = bytarr[i]
        self._pos += 4

    def addDouble(self, value: float ):
        self._capacity_( 8 )
        bytarr = bytearray(struct.pack("d", value))
        for i in range(8):
            self._buffer[ self._pos + i] = bytarr[i]
        self._pos += 8

    def addString(self, value: str ):

        if value is None:
            self._capacity_(1)
            self.addBool(0)
            return

        _size = (3 + len(value))
        self._capacity_( _size )
        self.addBool(1)
        self.addShort(len(value))

        if len(value) > 0:
            _bytarr = bytearray( value, 'utf-8')
            self._buffer[ self._pos: ] = _bytarr;
            self._pos += len(_bytarr)

    def addBytes(self, value: bytearray ):
        if value is None:
            self._capacity_(1)
            self.addBool(0)
            return

        _size = (5 + len(value))
        self._capacity_( _size )
        self.addBool(1)
        self.addInt(len(value))

        if len(value) > 0:
            self._buffer[ self._pos: ] = value
            self._pos += len(value)

    def getRemaining(self) -> int:
        return len( self._buffer) - self._pos

    def length(self):
        return self._pos

    def getBytes(self):
        return self._buffer[:self._pos]

    def reset(self):
        self._pos = 0

    def addRaw(self, buffer:bytearray ):
        self._buffer[:self._pos:] = buffer
        self._pos += len(buffer)

########################################################################################################################
#   Decoder
########################################################################################################################

class Decoder(Codec):

    def __init__(self, buffer: bytearray):
        super.__init__( buffer )

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
        _size = self.getInt()
        if _size == 0:
            return bytearray(0)

        _bytarr = self._buffer[ self._pos:self._pos + _size]
        self._pos += _size
        return _bytarr

    def getLength(self):
        return len( self._buffer )


    def reset(self):
        self._pos = 0

    def getRaw(self, size:int ):
        _bytarr = self._buffer[ self._pos:self._pos + size]
        self._pos += size
        return  _bytarr

    def getRemaning(self) -> int:
        return len(self._buffer) - self._pos