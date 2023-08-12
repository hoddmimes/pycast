from pymc.msg.decoder import Decoder
from pymc.msg.encoder import Encoder
from pymc.msg.messageif import MessageBase

class MessageAux:

    @staticmethod
    def addBoolList( encoder: Encoder, arr: list):
        if arr is None:
            encoder.addBool(False)
            return
        encoder.addBool(True)
        encoder.addShort( len(arr))
        for x in arr:
            encoder.addBool( x )

    @staticmethod
    def addByteList( encoder: Encoder, arr: list):
        if arr is None:
            encoder.addBool(False)
            return
        encoder.addBool(True)
        encoder.addShort( len(arr))
        for x in arr:
            encoder.addByte( x )

    @staticmethod
    def addShortList( encoder: Encoder, arr: list):
        if arr is None:
            encoder.addBool(False)
            return
        encoder.addBool(True)
        encoder.addShort( len(arr))
        for x in arr:
            encoder.addShort( x )

    @staticmethod
    def addIntList( encoder: Encoder, arr: list):
        if arr is None:
            encoder.addBool(False)
            return
        encoder.addBool(True)
        encoder.addShort( len(arr))
        for x in arr:
            encoder.addInt( x )

    @staticmethod
    def addLongList( encoder: Encoder, arr: list):
        if arr is None:
            encoder.addBool(False)
            return
        encoder.addBool(True)
        encoder.addShort( len(arr))
        for x in arr:
            encoder.addLong( x )

    @staticmethod
    def addFloatList( encoder: Encoder, arr: list):
        if arr is None:
            encoder.addBool(False)
            return
        encoder.addBool(True)
        encoder.addShort( len(arr))
        for x in arr:
            encoder.addFloat( x )

    @staticmethod
    def addDoubleList( encoder: Encoder, arr: list):
        if arr is None:
            encoder.addBool(False)
            return
        encoder.addBool(True)
        encoder.addShort( len(arr))
        for x in arr:
            encoder.addDouble( x )

    @staticmethod
    def addStringList( encoder: Encoder, arr: list):
        if arr is None:
            encoder.addBool(False)
            return
        encoder.addBool(True)
        encoder.addShort( len(arr))
        for x in arr:
            encoder.addString( x )

    @staticmethod
    def addBytesList( encoder: Encoder, arr: list):
        if arr is None:
            encoder.addBool(False)
            return
        encoder.addBool(True)
        encoder.addShort( len(arr))
        for x in arr:
            encoder.addBytes( x )

    @staticmethod
    def addMessageList( encoder: Encoder, arr: list):
        if arr is None:
            encoder.addBool(False)
            return
        encoder.addBool(True)
        encoder.addShort( len(arr))
        for x in arr:
            encoder.addMessage( x )


    @staticmethod
    def getBoolList( decoder: Decoder) -> list:
        if not decoder.getBool() :
            return None
        _lst = []
        _size = decoder.getShort()
        for i in range( _size ):
            x = decoder.getBool()
            _lst.append(x)
        return _lst

    @staticmethod
    def getByteList( decoder: Decoder) -> list:
        if not decoder.getBool() :
            return None
        _lst = []
        _size = decoder.getShort()
        for i in range( _size ):
            x = decoder.getByte()
            _lst.append(x)
        return _lst

    @staticmethod
    def getShortList( decoder: Decoder) -> list:
        if not decoder.getBool() :
            return None
        _lst = []
        _size = decoder.getShort()
        for i in range( _size ):
            x = decoder.getShort()
            _lst.append(x)
        return _lst

    @staticmethod
    def getIntList( decoder: Decoder) -> list:
        if not decoder.getBool() :
            return None
        _lst = []
        _size = decoder.getShort()
        for i in range( _size ):
            x = decoder.getInt()
            _lst.append(x)
        return _lst

    @staticmethod
    def getLongList( decoder: Decoder) -> list:
        if not decoder.getBool() :
            return None
        _lst = []
        _size = decoder.getShort()
        for i in range( _size ):
            x = decoder.getLong()
            _lst.append(x)
        return _lst

    @staticmethod
    def getFloatList( decoder: Decoder) -> list:
        if not decoder.getBool() :
            return None
        _lst = []
        _size = decoder.getShort()
        for i in range( _size ):
            x = decoder.getFloat()
            _lst.append(x)
        return _lst

    @staticmethod
    def getDoubleList( decoder: Decoder) -> list:
        if not decoder.getBool() :
            return None
        _lst = []
        _size = decoder.getShort()
        for i in range( _size ):
            x = decoder.getDouble()
            _lst.append(x)
        return _lst

    @staticmethod
    def getStringList( decoder: Decoder) -> list:
        if not decoder.getBool():
            return None
        _lst = []
        _size = decoder.getShort()
        for i in range( _size ):
            x = decoder.getString()
            _lst.append(x)
        return _lst

    @staticmethod
    def getBytesList( decoder: Decoder) -> list:
        if not decoder.getBool() :
            return None
        _lst = []
        _size = decoder.getShort()
        for i in range( _size ):
            x = decoder.getBytes()
            _lst.append(x)
        return _lst

    @staticmethod
    def getMessageList( decoder: Decoder) -> list:
        if not decoder.getBool() :
            return None
        _lst = []
        _size = decoder.getShort()
        for i in range( _size ):
            x = decoder.getMessage()
            _lst.append(x)
        return _lst

