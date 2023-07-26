

from msg.messageif import MessageBase
from msg.messages import MessageAux
from msg.decoder import Decoder
from msg.encoder import Encoder

            

class SubMessage( MessageBase ):

    def __init__(self):
        self.className = "msg.generated.SubMessage"
        
        self.subBool: bool
        self.subString: str
        self.subLong: int
    def setSubBool( self, value: bool ):
        self.subBool = value

    def getSubBool( self ) -> bool:
        return self.subBool
    def setSubString( self, value: str ):
        self.subString = value

    def getSubString( self ) -> str:
        return self.subString
    def setSubLong( self, value: int ):
        self.subLong = value

    def getSubLong( self ) -> int:
        return self.subLong

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: subBool Type: bool List: false
        _encoder.addBool( self.subBool )
        # Encode Attribute: subString Type: str List: false
        _encoder.addString( self.subString )
        # Encode Attribute: subLong Type: long List: false
        _encoder.addLong( self.subLong )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: subBool Type:bool List: false
        self.subBool = _decoder.getBool()
        
        #Decode Attribute: subString Type:str List: false
        self.subString = _decoder.getString()
        
        #Decode Attribute: subLong Type:long List: false
        self.subLong = _decoder.getLong()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                 "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: str = ""
        
        _buffer += self._blanks( _indent ) + "subBool : " + str( self.subBool) + "\n"
        _buffer += self._blanks( _indent ) + "subString : " + str( self.subString) + "\n"
        _buffer += self._blanks( _indent ) + "subLong : " + str( self.subLong) + "\n"
        return _buffer
    