import struct

########################################################################################################################
#   Encoder
########################################################################################################################

class Encoder:
    def __init__(self, size = 1024):
        self._buffer = bytearray( size )
        self._size = size;
        self._pos = 0;

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
        for i in range(8):
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
            bytarr = bytearray( value, 'utf-8')
            for i in range( len(bytarr)):
                self._buffer[ self._pos + i] = bytarr[i]
            self._pos += len(value)

    def addBytes(self, value: bytearray ):
        if value is None:
            self._capacity_(1)
            self.addBool(0)
            return

        _size = (3 + len(value))
        self._capacity_( _size )
        self.addBool(1)
        self.addShort(len(value))

        if len(value) > 0:
            for i in range( len(value)):
                self._buffer[ self._pos + i] = value[i]
            self._pos += len(value)

    def getRemaining(self) -> int:
        return len( self._buffer) - self._pos

    def length(self):
        return self._pos

    def getBytes(self):
        return self._buffer[:self._pos]

    def reset(self):
        self._pos = 0


########################################################################################################################
#   Decoder
########################################################################################################################

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

    def getLength(self):
        return len( self._buffer )


    def reset(self):
        self._pos = 0