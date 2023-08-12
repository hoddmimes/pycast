
from pymc.msg.messageif import MessageBase
from pymc.msg.messages import MessageAux
from pymc.msg.decoder import Decoder
from pymc.msg.encoder import Encoder
from io import StringIO
            
class DistNetMsg( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.DistNetMsg"
        
        self.requestId: int
        self.timestamp: int
        self.isRequestMessage: bool
        self.message: MessageBase
    def setRequestId( self, value: int ):
        self.requestId = value

    def getRequestId( self ) -> int:
        return self.requestId
    def setTimestamp( self, value: int ):
        self.timestamp = value

    def getTimestamp( self ) -> int:
        return self.timestamp
    def setIsRequestMessage( self, value: bool ):
        self.isRequestMessage = value

    def getIsRequestMessage( self ) -> bool:
        return self.isRequestMessage
    def setMessage( self, value: MessageBase ):
        self.message = value

    def getMessage( self ) -> MessageBase:
        return self.message

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: requestId Type: long List: false
        _encoder.addLong( self.requestId )
        # Encode Attribute: timestamp Type: long List: false
        _encoder.addLong( self.timestamp )
        # Encode Attribute: isRequestMessage Type: bool List: false
        _encoder.addBool( self.isRequestMessage )
        # Encode Attribute: message Type: MessageBase List: false
        _encoder.addMessage( self.message )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: requestId Type:long List: false
        self.requestId = _decoder.getLong()
        
        #Decode Attribute: timestamp Type:long List: false
        self.timestamp = _decoder.getLong()
        
        #Decode Attribute: isRequestMessage Type:bool List: false
        self.isRequestMessage = _decoder.getBool()
        
        #Decode Attribute: message Type:MessageBase List: false
        self.message = _decoder.getMessage()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "requestId : " + str( self.requestId) + "\n")
        _buffer.write(self._blanks( _indent ) + "timestamp : " + str( self.timestamp) + "\n")
        _buffer.write(self._blanks( _indent ) + "isRequestMessage : " + str( self.isRequestMessage) + "\n")
        if self.message is None:
           _buffer.write(self._blanks( _indent ) + "message : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "message : \n" + self.message.toString( _indent + 2) + "\n")
        return _buffer.getvalue()
    
class DistDomainConnectionEntry( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.DistDomainConnectionEntry"
        
        self.connectionId: int
        self.mcaAddress: str
        self.mcaPort: int
        self.subscriptions: int
        self.inRetransmissions: int
        self.outRetransmissions: int
    def setConnectionId( self, value: int ):
        self.connectionId = value

    def getConnectionId( self ) -> int:
        return self.connectionId
    def setMcaAddress( self, value: str ):
        self.mcaAddress = value

    def getMcaAddress( self ) -> str:
        return self.mcaAddress
    def setMcaPort( self, value: int ):
        self.mcaPort = value

    def getMcaPort( self ) -> int:
        return self.mcaPort
    def setSubscriptions( self, value: int ):
        self.subscriptions = value

    def getSubscriptions( self ) -> int:
        return self.subscriptions
    def setInRetransmissions( self, value: int ):
        self.inRetransmissions = value

    def getInRetransmissions( self ) -> int:
        return self.inRetransmissions
    def setOutRetransmissions( self, value: int ):
        self.outRetransmissions = value

    def getOutRetransmissions( self ) -> int:
        return self.outRetransmissions

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: connectionId Type: long List: false
        _encoder.addLong( self.connectionId )
        # Encode Attribute: mcaAddress Type: str List: false
        _encoder.addString( self.mcaAddress )
        # Encode Attribute: mcaPort Type: int List: false
        _encoder.addInt( self.mcaPort )
        # Encode Attribute: subscriptions Type: int List: false
        _encoder.addInt( self.subscriptions )
        # Encode Attribute: inRetransmissions Type: int List: false
        _encoder.addInt( self.inRetransmissions )
        # Encode Attribute: outRetransmissions Type: int List: false
        _encoder.addInt( self.outRetransmissions )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: connectionId Type:long List: false
        self.connectionId = _decoder.getLong()
        
        #Decode Attribute: mcaAddress Type:str List: false
        self.mcaAddress = _decoder.getString()
        
        #Decode Attribute: mcaPort Type:int List: false
        self.mcaPort = _decoder.getInt()
        
        #Decode Attribute: subscriptions Type:int List: false
        self.subscriptions = _decoder.getInt()
        
        #Decode Attribute: inRetransmissions Type:int List: false
        self.inRetransmissions = _decoder.getInt()
        
        #Decode Attribute: outRetransmissions Type:int List: false
        self.outRetransmissions = _decoder.getInt()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "connectionId : " + str( self.connectionId) + "\n")
        _buffer.write(self._blanks( _indent ) + "mcaAddress : " + str( self.mcaAddress) + "\n")
        _buffer.write(self._blanks( _indent ) + "mcaPort : " + str( self.mcaPort) + "\n")
        _buffer.write(self._blanks( _indent ) + "subscriptions : " + str( self.subscriptions) + "\n")
        _buffer.write(self._blanks( _indent ) + "inRetransmissions : " + str( self.inRetransmissions) + "\n")
        _buffer.write(self._blanks( _indent ) + "outRetransmissions : " + str( self.outRetransmissions) + "\n")
        return _buffer.getvalue()
    
class DistDomainDistributorEntry( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.DistDomainDistributorEntry"
        
        self.distributorId: int
        self.hostname: str
        self.hostaddress: str
        self.applicationName: str
        self.applicationId: int
        self.startTime: str
        self.inRetransmissions: int
        self.outRetransmissions: int
        self.connections: DistDomainConnectionEntry
    def setDistributorId( self, value: int ):
        self.distributorId = value

    def getDistributorId( self ) -> int:
        return self.distributorId
    def setHostname( self, value: str ):
        self.hostname = value

    def getHostname( self ) -> str:
        return self.hostname
    def setHostaddress( self, value: str ):
        self.hostaddress = value

    def getHostaddress( self ) -> str:
        return self.hostaddress
    def setApplicationName( self, value: str ):
        self.applicationName = value

    def getApplicationName( self ) -> str:
        return self.applicationName
    def setApplicationId( self, value: int ):
        self.applicationId = value

    def getApplicationId( self ) -> int:
        return self.applicationId
    def setStartTime( self, value: str ):
        self.startTime = value

    def getStartTime( self ) -> str:
        return self.startTime
    def setInRetransmissions( self, value: int ):
        self.inRetransmissions = value

    def getInRetransmissions( self ) -> int:
        return self.inRetransmissions
    def setOutRetransmissions( self, value: int ):
        self.outRetransmissions = value

    def getOutRetransmissions( self ) -> int:
        return self.outRetransmissions
    def setConnections( self, value: DistDomainConnectionEntry ):
        self.connections = value

    def getConnections( self ) -> DistDomainConnectionEntry:
        return self.connections

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: distributorId Type: long List: false
        _encoder.addLong( self.distributorId )
        # Encode Attribute: hostname Type: str List: false
        _encoder.addString( self.hostname )
        # Encode Attribute: hostaddress Type: str List: false
        _encoder.addString( self.hostaddress )
        # Encode Attribute: applicationName Type: str List: false
        _encoder.addString( self.applicationName )
        # Encode Attribute: applicationId Type: int List: false
        _encoder.addInt( self.applicationId )
        # Encode Attribute: startTime Type: str List: false
        _encoder.addString( self.startTime )
        # Encode Attribute: inRetransmissions Type: int List: false
        _encoder.addInt( self.inRetransmissions )
        # Encode Attribute: outRetransmissions Type: int List: false
        _encoder.addInt( self.outRetransmissions )
        # Encode Attribute: connections Type: DistDomainConnectionEntry List: false
        _encoder.addMessage( self.connections )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: distributorId Type:long List: false
        self.distributorId = _decoder.getLong()
        
        #Decode Attribute: hostname Type:str List: false
        self.hostname = _decoder.getString()
        
        #Decode Attribute: hostaddress Type:str List: false
        self.hostaddress = _decoder.getString()
        
        #Decode Attribute: applicationName Type:str List: false
        self.applicationName = _decoder.getString()
        
        #Decode Attribute: applicationId Type:int List: false
        self.applicationId = _decoder.getInt()
        
        #Decode Attribute: startTime Type:str List: false
        self.startTime = _decoder.getString()
        
        #Decode Attribute: inRetransmissions Type:int List: false
        self.inRetransmissions = _decoder.getInt()
        
        #Decode Attribute: outRetransmissions Type:int List: false
        self.outRetransmissions = _decoder.getInt()
        
        #Decode Attribute: connections Type:DistDomainConnectionEntry List: false
        self.connections = _decoder.getMessage()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "distributorId : " + str( self.distributorId) + "\n")
        _buffer.write(self._blanks( _indent ) + "hostname : " + str( self.hostname) + "\n")
        _buffer.write(self._blanks( _indent ) + "hostaddress : " + str( self.hostaddress) + "\n")
        _buffer.write(self._blanks( _indent ) + "applicationName : " + str( self.applicationName) + "\n")
        _buffer.write(self._blanks( _indent ) + "applicationId : " + str( self.applicationId) + "\n")
        _buffer.write(self._blanks( _indent ) + "startTime : " + str( self.startTime) + "\n")
        _buffer.write(self._blanks( _indent ) + "inRetransmissions : " + str( self.inRetransmissions) + "\n")
        _buffer.write(self._blanks( _indent ) + "outRetransmissions : " + str( self.outRetransmissions) + "\n")
        if self.connections is None:
           _buffer.write(self._blanks( _indent ) + "connections : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "connections : \n" + self.connections.toString( _indent + 2) + "\n")
        return _buffer.getvalue()
    
class DistExploreDomainRqst( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.DistExploreDomainRqst"
        

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        return _buffer.getvalue()
    
class DistExploreDomainRsp( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.DistExploreDomainRsp"
        
        self.distributor: DistDomainDistributorEntry
    def setDistributor( self, value: DistDomainDistributorEntry ):
        self.distributor = value

    def getDistributor( self ) -> DistDomainDistributorEntry:
        return self.distributor

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: distributor Type: DistDomainDistributorEntry List: false
        _encoder.addMessage( self.distributor )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: distributor Type:DistDomainDistributorEntry List: false
        self.distributor = _decoder.getMessage()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        if self.distributor is None:
           _buffer.write(self._blanks( _indent ) + "distributor : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "distributor : \n" + self.distributor.toString( _indent + 2) + "\n")
        return _buffer.getvalue()
    
class DistributorEntry( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.DistributorEntry"
        
        self.hostname: str
        self.hostaddress: str
        self.applicationName: str
        self.applicationId: int
        self.startTime: str
        self.connections: int
        self.distributorId: int
        self.memMax: int
        self.memUsed: int
        self.memFree: int
        self.inRetransmissions: int
        self.outRetransmissions: int
        self.subscriptions: int
    def setHostname( self, value: str ):
        self.hostname = value

    def getHostname( self ) -> str:
        return self.hostname
    def setHostaddress( self, value: str ):
        self.hostaddress = value

    def getHostaddress( self ) -> str:
        return self.hostaddress
    def setApplicationName( self, value: str ):
        self.applicationName = value

    def getApplicationName( self ) -> str:
        return self.applicationName
    def setApplicationId( self, value: int ):
        self.applicationId = value

    def getApplicationId( self ) -> int:
        return self.applicationId
    def setStartTime( self, value: str ):
        self.startTime = value

    def getStartTime( self ) -> str:
        return self.startTime
    def setConnections( self, value: int ):
        self.connections = value

    def getConnections( self ) -> int:
        return self.connections
    def setDistributorId( self, value: int ):
        self.distributorId = value

    def getDistributorId( self ) -> int:
        return self.distributorId
    def setMemMax( self, value: int ):
        self.memMax = value

    def getMemMax( self ) -> int:
        return self.memMax
    def setMemUsed( self, value: int ):
        self.memUsed = value

    def getMemUsed( self ) -> int:
        return self.memUsed
    def setMemFree( self, value: int ):
        self.memFree = value

    def getMemFree( self ) -> int:
        return self.memFree
    def setInRetransmissions( self, value: int ):
        self.inRetransmissions = value

    def getInRetransmissions( self ) -> int:
        return self.inRetransmissions
    def setOutRetransmissions( self, value: int ):
        self.outRetransmissions = value

    def getOutRetransmissions( self ) -> int:
        return self.outRetransmissions
    def setSubscriptions( self, value: int ):
        self.subscriptions = value

    def getSubscriptions( self ) -> int:
        return self.subscriptions

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: hostname Type: str List: false
        _encoder.addString( self.hostname )
        # Encode Attribute: hostaddress Type: str List: false
        _encoder.addString( self.hostaddress )
        # Encode Attribute: applicationName Type: str List: false
        _encoder.addString( self.applicationName )
        # Encode Attribute: applicationId Type: int List: false
        _encoder.addInt( self.applicationId )
        # Encode Attribute: startTime Type: str List: false
        _encoder.addString( self.startTime )
        # Encode Attribute: connections Type: int List: false
        _encoder.addInt( self.connections )
        # Encode Attribute: distributorId Type: long List: false
        _encoder.addLong( self.distributorId )
        # Encode Attribute: memMax Type: long List: false
        _encoder.addLong( self.memMax )
        # Encode Attribute: memUsed Type: long List: false
        _encoder.addLong( self.memUsed )
        # Encode Attribute: memFree Type: long List: false
        _encoder.addLong( self.memFree )
        # Encode Attribute: inRetransmissions Type: int List: false
        _encoder.addInt( self.inRetransmissions )
        # Encode Attribute: outRetransmissions Type: int List: false
        _encoder.addInt( self.outRetransmissions )
        # Encode Attribute: subscriptions Type: int List: false
        _encoder.addInt( self.subscriptions )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: hostname Type:str List: false
        self.hostname = _decoder.getString()
        
        #Decode Attribute: hostaddress Type:str List: false
        self.hostaddress = _decoder.getString()
        
        #Decode Attribute: applicationName Type:str List: false
        self.applicationName = _decoder.getString()
        
        #Decode Attribute: applicationId Type:int List: false
        self.applicationId = _decoder.getInt()
        
        #Decode Attribute: startTime Type:str List: false
        self.startTime = _decoder.getString()
        
        #Decode Attribute: connections Type:int List: false
        self.connections = _decoder.getInt()
        
        #Decode Attribute: distributorId Type:long List: false
        self.distributorId = _decoder.getLong()
        
        #Decode Attribute: memMax Type:long List: false
        self.memMax = _decoder.getLong()
        
        #Decode Attribute: memUsed Type:long List: false
        self.memUsed = _decoder.getLong()
        
        #Decode Attribute: memFree Type:long List: false
        self.memFree = _decoder.getLong()
        
        #Decode Attribute: inRetransmissions Type:int List: false
        self.inRetransmissions = _decoder.getInt()
        
        #Decode Attribute: outRetransmissions Type:int List: false
        self.outRetransmissions = _decoder.getInt()
        
        #Decode Attribute: subscriptions Type:int List: false
        self.subscriptions = _decoder.getInt()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "hostname : " + str( self.hostname) + "\n")
        _buffer.write(self._blanks( _indent ) + "hostaddress : " + str( self.hostaddress) + "\n")
        _buffer.write(self._blanks( _indent ) + "applicationName : " + str( self.applicationName) + "\n")
        _buffer.write(self._blanks( _indent ) + "applicationId : " + str( self.applicationId) + "\n")
        _buffer.write(self._blanks( _indent ) + "startTime : " + str( self.startTime) + "\n")
        _buffer.write(self._blanks( _indent ) + "connections : " + str( self.connections) + "\n")
        _buffer.write(self._blanks( _indent ) + "distributorId : " + str( self.distributorId) + "\n")
        _buffer.write(self._blanks( _indent ) + "memMax : " + str( self.memMax) + "\n")
        _buffer.write(self._blanks( _indent ) + "memUsed : " + str( self.memUsed) + "\n")
        _buffer.write(self._blanks( _indent ) + "memFree : " + str( self.memFree) + "\n")
        _buffer.write(self._blanks( _indent ) + "inRetransmissions : " + str( self.inRetransmissions) + "\n")
        _buffer.write(self._blanks( _indent ) + "outRetransmissions : " + str( self.outRetransmissions) + "\n")
        _buffer.write(self._blanks( _indent ) + "subscriptions : " + str( self.subscriptions) + "\n")
        return _buffer.getvalue()
    
class DistExploreDistributorRqst( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.DistExploreDistributorRqst"
        
        self.distributorId: int
    def setDistributorId( self, value: int ):
        self.distributorId = value

    def getDistributorId( self ) -> int:
        return self.distributorId

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: distributorId Type: long List: false
        _encoder.addLong( self.distributorId )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: distributorId Type:long List: false
        self.distributorId = _decoder.getLong()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "distributorId : " + str( self.distributorId) + "\n")
        return _buffer.getvalue()
    
class DistExploreDistributorRsp( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.DistExploreDistributorRsp"
        
        self.distributor: DistributorEntry
    def setDistributor( self, value: DistributorEntry ):
        self.distributor = value

    def getDistributor( self ) -> DistributorEntry:
        return self.distributor

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: distributor Type: DistributorEntry List: false
        _encoder.addMessage( self.distributor )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: distributor Type:DistributorEntry List: false
        self.distributor = _decoder.getMessage()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        if self.distributor is None:
           _buffer.write(self._blanks( _indent ) + "distributor : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "distributor : \n" + self.distributor.toString( _indent + 2) + "\n")
        return _buffer.getvalue()
    
class DataRateItem( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.DataRateItem"
        
        self.total: int
        self.currValue: int
        self.peakValue: int
        self.peakTime: str
    def setTotal( self, value: int ):
        self.total = value

    def getTotal( self ) -> int:
        return self.total
    def setCurrValue( self, value: int ):
        self.currValue = value

    def getCurrValue( self ) -> int:
        return self.currValue
    def setPeakValue( self, value: int ):
        self.peakValue = value

    def getPeakValue( self ) -> int:
        return self.peakValue
    def setPeakTime( self, value: str ):
        self.peakTime = value

    def getPeakTime( self ) -> str:
        return self.peakTime

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: total Type: long List: false
        _encoder.addLong( self.total )
        # Encode Attribute: currValue Type: int List: false
        _encoder.addInt( self.currValue )
        # Encode Attribute: peakValue Type: int List: false
        _encoder.addInt( self.peakValue )
        # Encode Attribute: peakTime Type: str List: false
        _encoder.addString( self.peakTime )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: total Type:long List: false
        self.total = _decoder.getLong()
        
        #Decode Attribute: currValue Type:int List: false
        self.currValue = _decoder.getInt()
        
        #Decode Attribute: peakValue Type:int List: false
        self.peakValue = _decoder.getInt()
        
        #Decode Attribute: peakTime Type:str List: false
        self.peakTime = _decoder.getString()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "total : " + str( self.total) + "\n")
        _buffer.write(self._blanks( _indent ) + "currValue : " + str( self.currValue) + "\n")
        _buffer.write(self._blanks( _indent ) + "peakValue : " + str( self.peakValue) + "\n")
        _buffer.write(self._blanks( _indent ) + "peakTime : " + str( self.peakTime) + "\n")
        return _buffer.getvalue()
    
class QueueSizeItem( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.QueueSizeItem"
        
        self.size: int
        self.peakSize: int
        self.peakTime: str
    def setSize( self, value: int ):
        self.size = value

    def getSize( self ) -> int:
        return self.size
    def setPeakSize( self, value: int ):
        self.peakSize = value

    def getPeakSize( self ) -> int:
        return self.peakSize
    def setPeakTime( self, value: str ):
        self.peakTime = value

    def getPeakTime( self ) -> str:
        return self.peakTime

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: size Type: long List: false
        _encoder.addLong( self.size )
        # Encode Attribute: peakSize Type: int List: false
        _encoder.addInt( self.peakSize )
        # Encode Attribute: peakTime Type: str List: false
        _encoder.addString( self.peakTime )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: size Type:long List: false
        self.size = _decoder.getLong()
        
        #Decode Attribute: peakSize Type:int List: false
        self.peakSize = _decoder.getInt()
        
        #Decode Attribute: peakTime Type:str List: false
        self.peakTime = _decoder.getString()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "size : " + str( self.size) + "\n")
        _buffer.write(self._blanks( _indent ) + "peakSize : " + str( self.peakSize) + "\n")
        _buffer.write(self._blanks( _indent ) + "peakTime : " + str( self.peakTime) + "\n")
        return _buffer.getvalue()
    
class ConnectionEntry( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.ConnectionEntry"
        
        self.mcaAddress: str
        self.mcaPort: int
        self.connectionId: int
        self.publishers: int
        self.subscribers: int
        self.subscriptions: int
        self.inRetransmissions: int
        self.outRetransmissions: int
        self.deliverUpdateQueue: QueueSizeItem
        self.xtaTotalBytes: int
        self.xtaTotalSegments: int
        self.xtaTotalUpdates: int
        self.xtaBytes: DataRateItem
        self.xtaSegments: DataRateItem
        self.xtaUpdates: DataRateItem
        self.xtaBytes1min: DataRateItem
        self.xtaSegments1min: DataRateItem
        self.xtaUpdates1min: DataRateItem
        self.xtaBytes5min: DataRateItem
        self.xtaSegments5min: DataRateItem
        self.xtaUpdates5min: DataRateItem
        self.rcvTotalBytes: int
        self.rcvTotalSegments: int
        self.rcvTotalUpdates: int
        self.rcvBytes: DataRateItem
        self.rcvSegments: DataRateItem
        self.rcvUpdates: DataRateItem
        self.rcvBytes1min: DataRateItem
        self.rcvSegments1min: DataRateItem
        self.rcvUpdates1min: DataRateItem
        self.rcvBytes5min: DataRateItem
        self.rcvSegments5min: DataRateItem
        self.rcvUpdates5min: DataRateItem
    def setMcaAddress( self, value: str ):
        self.mcaAddress = value

    def getMcaAddress( self ) -> str:
        return self.mcaAddress
    def setMcaPort( self, value: int ):
        self.mcaPort = value

    def getMcaPort( self ) -> int:
        return self.mcaPort
    def setConnectionId( self, value: int ):
        self.connectionId = value

    def getConnectionId( self ) -> int:
        return self.connectionId
    def setPublishers( self, value: int ):
        self.publishers = value

    def getPublishers( self ) -> int:
        return self.publishers
    def setSubscribers( self, value: int ):
        self.subscribers = value

    def getSubscribers( self ) -> int:
        return self.subscribers
    def setSubscriptions( self, value: int ):
        self.subscriptions = value

    def getSubscriptions( self ) -> int:
        return self.subscriptions
    def setInRetransmissions( self, value: int ):
        self.inRetransmissions = value

    def getInRetransmissions( self ) -> int:
        return self.inRetransmissions
    def setOutRetransmissions( self, value: int ):
        self.outRetransmissions = value

    def getOutRetransmissions( self ) -> int:
        return self.outRetransmissions
    def setDeliverUpdateQueue( self, value: QueueSizeItem ):
        self.deliverUpdateQueue = value

    def getDeliverUpdateQueue( self ) -> QueueSizeItem:
        return self.deliverUpdateQueue
    def setXtaTotalBytes( self, value: int ):
        self.xtaTotalBytes = value

    def getXtaTotalBytes( self ) -> int:
        return self.xtaTotalBytes
    def setXtaTotalSegments( self, value: int ):
        self.xtaTotalSegments = value

    def getXtaTotalSegments( self ) -> int:
        return self.xtaTotalSegments
    def setXtaTotalUpdates( self, value: int ):
        self.xtaTotalUpdates = value

    def getXtaTotalUpdates( self ) -> int:
        return self.xtaTotalUpdates
    def setXtaBytes( self, value: DataRateItem ):
        self.xtaBytes = value

    def getXtaBytes( self ) -> DataRateItem:
        return self.xtaBytes
    def setXtaSegments( self, value: DataRateItem ):
        self.xtaSegments = value

    def getXtaSegments( self ) -> DataRateItem:
        return self.xtaSegments
    def setXtaUpdates( self, value: DataRateItem ):
        self.xtaUpdates = value

    def getXtaUpdates( self ) -> DataRateItem:
        return self.xtaUpdates
    def setXtaBytes1min( self, value: DataRateItem ):
        self.xtaBytes1min = value

    def getXtaBytes1min( self ) -> DataRateItem:
        return self.xtaBytes1min
    def setXtaSegments1min( self, value: DataRateItem ):
        self.xtaSegments1min = value

    def getXtaSegments1min( self ) -> DataRateItem:
        return self.xtaSegments1min
    def setXtaUpdates1min( self, value: DataRateItem ):
        self.xtaUpdates1min = value

    def getXtaUpdates1min( self ) -> DataRateItem:
        return self.xtaUpdates1min
    def setXtaBytes5min( self, value: DataRateItem ):
        self.xtaBytes5min = value

    def getXtaBytes5min( self ) -> DataRateItem:
        return self.xtaBytes5min
    def setXtaSegments5min( self, value: DataRateItem ):
        self.xtaSegments5min = value

    def getXtaSegments5min( self ) -> DataRateItem:
        return self.xtaSegments5min
    def setXtaUpdates5min( self, value: DataRateItem ):
        self.xtaUpdates5min = value

    def getXtaUpdates5min( self ) -> DataRateItem:
        return self.xtaUpdates5min
    def setRcvTotalBytes( self, value: int ):
        self.rcvTotalBytes = value

    def getRcvTotalBytes( self ) -> int:
        return self.rcvTotalBytes
    def setRcvTotalSegments( self, value: int ):
        self.rcvTotalSegments = value

    def getRcvTotalSegments( self ) -> int:
        return self.rcvTotalSegments
    def setRcvTotalUpdates( self, value: int ):
        self.rcvTotalUpdates = value

    def getRcvTotalUpdates( self ) -> int:
        return self.rcvTotalUpdates
    def setRcvBytes( self, value: DataRateItem ):
        self.rcvBytes = value

    def getRcvBytes( self ) -> DataRateItem:
        return self.rcvBytes
    def setRcvSegments( self, value: DataRateItem ):
        self.rcvSegments = value

    def getRcvSegments( self ) -> DataRateItem:
        return self.rcvSegments
    def setRcvUpdates( self, value: DataRateItem ):
        self.rcvUpdates = value

    def getRcvUpdates( self ) -> DataRateItem:
        return self.rcvUpdates
    def setRcvBytes1min( self, value: DataRateItem ):
        self.rcvBytes1min = value

    def getRcvBytes1min( self ) -> DataRateItem:
        return self.rcvBytes1min
    def setRcvSegments1min( self, value: DataRateItem ):
        self.rcvSegments1min = value

    def getRcvSegments1min( self ) -> DataRateItem:
        return self.rcvSegments1min
    def setRcvUpdates1min( self, value: DataRateItem ):
        self.rcvUpdates1min = value

    def getRcvUpdates1min( self ) -> DataRateItem:
        return self.rcvUpdates1min
    def setRcvBytes5min( self, value: DataRateItem ):
        self.rcvBytes5min = value

    def getRcvBytes5min( self ) -> DataRateItem:
        return self.rcvBytes5min
    def setRcvSegments5min( self, value: DataRateItem ):
        self.rcvSegments5min = value

    def getRcvSegments5min( self ) -> DataRateItem:
        return self.rcvSegments5min
    def setRcvUpdates5min( self, value: DataRateItem ):
        self.rcvUpdates5min = value

    def getRcvUpdates5min( self ) -> DataRateItem:
        return self.rcvUpdates5min

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: mcaAddress Type: str List: false
        _encoder.addString( self.mcaAddress )
        # Encode Attribute: mcaPort Type: int List: false
        _encoder.addInt( self.mcaPort )
        # Encode Attribute: connectionId Type: long List: false
        _encoder.addLong( self.connectionId )
        # Encode Attribute: publishers Type: int List: false
        _encoder.addInt( self.publishers )
        # Encode Attribute: subscribers Type: int List: false
        _encoder.addInt( self.subscribers )
        # Encode Attribute: subscriptions Type: int List: false
        _encoder.addInt( self.subscriptions )
        # Encode Attribute: inRetransmissions Type: int List: false
        _encoder.addInt( self.inRetransmissions )
        # Encode Attribute: outRetransmissions Type: int List: false
        _encoder.addInt( self.outRetransmissions )
        # Encode Attribute: deliverUpdateQueue Type: QueueSizeItem List: false
        _encoder.addMessage( self.deliverUpdateQueue )
        # Encode Attribute: xtaTotalBytes Type: long List: false
        _encoder.addLong( self.xtaTotalBytes )
        # Encode Attribute: xtaTotalSegments Type: long List: false
        _encoder.addLong( self.xtaTotalSegments )
        # Encode Attribute: xtaTotalUpdates Type: long List: false
        _encoder.addLong( self.xtaTotalUpdates )
        # Encode Attribute: xtaBytes Type: DataRateItem List: false
        _encoder.addMessage( self.xtaBytes )
        # Encode Attribute: xtaSegments Type: DataRateItem List: false
        _encoder.addMessage( self.xtaSegments )
        # Encode Attribute: xtaUpdates Type: DataRateItem List: false
        _encoder.addMessage( self.xtaUpdates )
        # Encode Attribute: xtaBytes1min Type: DataRateItem List: false
        _encoder.addMessage( self.xtaBytes1min )
        # Encode Attribute: xtaSegments1min Type: DataRateItem List: false
        _encoder.addMessage( self.xtaSegments1min )
        # Encode Attribute: xtaUpdates1min Type: DataRateItem List: false
        _encoder.addMessage( self.xtaUpdates1min )
        # Encode Attribute: xtaBytes5min Type: DataRateItem List: false
        _encoder.addMessage( self.xtaBytes5min )
        # Encode Attribute: xtaSegments5min Type: DataRateItem List: false
        _encoder.addMessage( self.xtaSegments5min )
        # Encode Attribute: xtaUpdates5min Type: DataRateItem List: false
        _encoder.addMessage( self.xtaUpdates5min )
        # Encode Attribute: rcvTotalBytes Type: long List: false
        _encoder.addLong( self.rcvTotalBytes )
        # Encode Attribute: rcvTotalSegments Type: long List: false
        _encoder.addLong( self.rcvTotalSegments )
        # Encode Attribute: rcvTotalUpdates Type: long List: false
        _encoder.addLong( self.rcvTotalUpdates )
        # Encode Attribute: rcvBytes Type: DataRateItem List: false
        _encoder.addMessage( self.rcvBytes )
        # Encode Attribute: rcvSegments Type: DataRateItem List: false
        _encoder.addMessage( self.rcvSegments )
        # Encode Attribute: rcvUpdates Type: DataRateItem List: false
        _encoder.addMessage( self.rcvUpdates )
        # Encode Attribute: rcvBytes1min Type: DataRateItem List: false
        _encoder.addMessage( self.rcvBytes1min )
        # Encode Attribute: rcvSegments1min Type: DataRateItem List: false
        _encoder.addMessage( self.rcvSegments1min )
        # Encode Attribute: rcvUpdates1min Type: DataRateItem List: false
        _encoder.addMessage( self.rcvUpdates1min )
        # Encode Attribute: rcvBytes5min Type: DataRateItem List: false
        _encoder.addMessage( self.rcvBytes5min )
        # Encode Attribute: rcvSegments5min Type: DataRateItem List: false
        _encoder.addMessage( self.rcvSegments5min )
        # Encode Attribute: rcvUpdates5min Type: DataRateItem List: false
        _encoder.addMessage( self.rcvUpdates5min )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: mcaAddress Type:str List: false
        self.mcaAddress = _decoder.getString()
        
        #Decode Attribute: mcaPort Type:int List: false
        self.mcaPort = _decoder.getInt()
        
        #Decode Attribute: connectionId Type:long List: false
        self.connectionId = _decoder.getLong()
        
        #Decode Attribute: publishers Type:int List: false
        self.publishers = _decoder.getInt()
        
        #Decode Attribute: subscribers Type:int List: false
        self.subscribers = _decoder.getInt()
        
        #Decode Attribute: subscriptions Type:int List: false
        self.subscriptions = _decoder.getInt()
        
        #Decode Attribute: inRetransmissions Type:int List: false
        self.inRetransmissions = _decoder.getInt()
        
        #Decode Attribute: outRetransmissions Type:int List: false
        self.outRetransmissions = _decoder.getInt()
        
        #Decode Attribute: deliverUpdateQueue Type:QueueSizeItem List: false
        self.deliverUpdateQueue = _decoder.getMessage()
        
        #Decode Attribute: xtaTotalBytes Type:long List: false
        self.xtaTotalBytes = _decoder.getLong()
        
        #Decode Attribute: xtaTotalSegments Type:long List: false
        self.xtaTotalSegments = _decoder.getLong()
        
        #Decode Attribute: xtaTotalUpdates Type:long List: false
        self.xtaTotalUpdates = _decoder.getLong()
        
        #Decode Attribute: xtaBytes Type:DataRateItem List: false
        self.xtaBytes = _decoder.getMessage()
        
        #Decode Attribute: xtaSegments Type:DataRateItem List: false
        self.xtaSegments = _decoder.getMessage()
        
        #Decode Attribute: xtaUpdates Type:DataRateItem List: false
        self.xtaUpdates = _decoder.getMessage()
        
        #Decode Attribute: xtaBytes1min Type:DataRateItem List: false
        self.xtaBytes1min = _decoder.getMessage()
        
        #Decode Attribute: xtaSegments1min Type:DataRateItem List: false
        self.xtaSegments1min = _decoder.getMessage()
        
        #Decode Attribute: xtaUpdates1min Type:DataRateItem List: false
        self.xtaUpdates1min = _decoder.getMessage()
        
        #Decode Attribute: xtaBytes5min Type:DataRateItem List: false
        self.xtaBytes5min = _decoder.getMessage()
        
        #Decode Attribute: xtaSegments5min Type:DataRateItem List: false
        self.xtaSegments5min = _decoder.getMessage()
        
        #Decode Attribute: xtaUpdates5min Type:DataRateItem List: false
        self.xtaUpdates5min = _decoder.getMessage()
        
        #Decode Attribute: rcvTotalBytes Type:long List: false
        self.rcvTotalBytes = _decoder.getLong()
        
        #Decode Attribute: rcvTotalSegments Type:long List: false
        self.rcvTotalSegments = _decoder.getLong()
        
        #Decode Attribute: rcvTotalUpdates Type:long List: false
        self.rcvTotalUpdates = _decoder.getLong()
        
        #Decode Attribute: rcvBytes Type:DataRateItem List: false
        self.rcvBytes = _decoder.getMessage()
        
        #Decode Attribute: rcvSegments Type:DataRateItem List: false
        self.rcvSegments = _decoder.getMessage()
        
        #Decode Attribute: rcvUpdates Type:DataRateItem List: false
        self.rcvUpdates = _decoder.getMessage()
        
        #Decode Attribute: rcvBytes1min Type:DataRateItem List: false
        self.rcvBytes1min = _decoder.getMessage()
        
        #Decode Attribute: rcvSegments1min Type:DataRateItem List: false
        self.rcvSegments1min = _decoder.getMessage()
        
        #Decode Attribute: rcvUpdates1min Type:DataRateItem List: false
        self.rcvUpdates1min = _decoder.getMessage()
        
        #Decode Attribute: rcvBytes5min Type:DataRateItem List: false
        self.rcvBytes5min = _decoder.getMessage()
        
        #Decode Attribute: rcvSegments5min Type:DataRateItem List: false
        self.rcvSegments5min = _decoder.getMessage()
        
        #Decode Attribute: rcvUpdates5min Type:DataRateItem List: false
        self.rcvUpdates5min = _decoder.getMessage()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "mcaAddress : " + str( self.mcaAddress) + "\n")
        _buffer.write(self._blanks( _indent ) + "mcaPort : " + str( self.mcaPort) + "\n")
        _buffer.write(self._blanks( _indent ) + "connectionId : " + str( self.connectionId) + "\n")
        _buffer.write(self._blanks( _indent ) + "publishers : " + str( self.publishers) + "\n")
        _buffer.write(self._blanks( _indent ) + "subscribers : " + str( self.subscribers) + "\n")
        _buffer.write(self._blanks( _indent ) + "subscriptions : " + str( self.subscriptions) + "\n")
        _buffer.write(self._blanks( _indent ) + "inRetransmissions : " + str( self.inRetransmissions) + "\n")
        _buffer.write(self._blanks( _indent ) + "outRetransmissions : " + str( self.outRetransmissions) + "\n")
        if self.deliverUpdateQueue is None:
           _buffer.write(self._blanks( _indent ) + "deliverUpdateQueue : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "deliverUpdateQueue : \n" + self.deliverUpdateQueue.toString( _indent + 2) + "\n")
        _buffer.write(self._blanks( _indent ) + "xtaTotalBytes : " + str( self.xtaTotalBytes) + "\n")
        _buffer.write(self._blanks( _indent ) + "xtaTotalSegments : " + str( self.xtaTotalSegments) + "\n")
        _buffer.write(self._blanks( _indent ) + "xtaTotalUpdates : " + str( self.xtaTotalUpdates) + "\n")
        if self.xtaBytes is None:
           _buffer.write(self._blanks( _indent ) + "xtaBytes : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "xtaBytes : \n" + self.xtaBytes.toString( _indent + 2) + "\n")
        if self.xtaSegments is None:
           _buffer.write(self._blanks( _indent ) + "xtaSegments : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "xtaSegments : \n" + self.xtaSegments.toString( _indent + 2) + "\n")
        if self.xtaUpdates is None:
           _buffer.write(self._blanks( _indent ) + "xtaUpdates : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "xtaUpdates : \n" + self.xtaUpdates.toString( _indent + 2) + "\n")
        if self.xtaBytes1min is None:
           _buffer.write(self._blanks( _indent ) + "xtaBytes1min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "xtaBytes1min : \n" + self.xtaBytes1min.toString( _indent + 2) + "\n")
        if self.xtaSegments1min is None:
           _buffer.write(self._blanks( _indent ) + "xtaSegments1min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "xtaSegments1min : \n" + self.xtaSegments1min.toString( _indent + 2) + "\n")
        if self.xtaUpdates1min is None:
           _buffer.write(self._blanks( _indent ) + "xtaUpdates1min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "xtaUpdates1min : \n" + self.xtaUpdates1min.toString( _indent + 2) + "\n")
        if self.xtaBytes5min is None:
           _buffer.write(self._blanks( _indent ) + "xtaBytes5min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "xtaBytes5min : \n" + self.xtaBytes5min.toString( _indent + 2) + "\n")
        if self.xtaSegments5min is None:
           _buffer.write(self._blanks( _indent ) + "xtaSegments5min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "xtaSegments5min : \n" + self.xtaSegments5min.toString( _indent + 2) + "\n")
        if self.xtaUpdates5min is None:
           _buffer.write(self._blanks( _indent ) + "xtaUpdates5min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "xtaUpdates5min : \n" + self.xtaUpdates5min.toString( _indent + 2) + "\n")
        _buffer.write(self._blanks( _indent ) + "rcvTotalBytes : " + str( self.rcvTotalBytes) + "\n")
        _buffer.write(self._blanks( _indent ) + "rcvTotalSegments : " + str( self.rcvTotalSegments) + "\n")
        _buffer.write(self._blanks( _indent ) + "rcvTotalUpdates : " + str( self.rcvTotalUpdates) + "\n")
        if self.rcvBytes is None:
           _buffer.write(self._blanks( _indent ) + "rcvBytes : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "rcvBytes : \n" + self.rcvBytes.toString( _indent + 2) + "\n")
        if self.rcvSegments is None:
           _buffer.write(self._blanks( _indent ) + "rcvSegments : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "rcvSegments : \n" + self.rcvSegments.toString( _indent + 2) + "\n")
        if self.rcvUpdates is None:
           _buffer.write(self._blanks( _indent ) + "rcvUpdates : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "rcvUpdates : \n" + self.rcvUpdates.toString( _indent + 2) + "\n")
        if self.rcvBytes1min is None:
           _buffer.write(self._blanks( _indent ) + "rcvBytes1min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "rcvBytes1min : \n" + self.rcvBytes1min.toString( _indent + 2) + "\n")
        if self.rcvSegments1min is None:
           _buffer.write(self._blanks( _indent ) + "rcvSegments1min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "rcvSegments1min : \n" + self.rcvSegments1min.toString( _indent + 2) + "\n")
        if self.rcvUpdates1min is None:
           _buffer.write(self._blanks( _indent ) + "rcvUpdates1min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "rcvUpdates1min : \n" + self.rcvUpdates1min.toString( _indent + 2) + "\n")
        if self.rcvBytes5min is None:
           _buffer.write(self._blanks( _indent ) + "rcvBytes5min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "rcvBytes5min : \n" + self.rcvBytes5min.toString( _indent + 2) + "\n")
        if self.rcvSegments5min is None:
           _buffer.write(self._blanks( _indent ) + "rcvSegments5min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "rcvSegments5min : \n" + self.rcvSegments5min.toString( _indent + 2) + "\n")
        if self.rcvUpdates5min is None:
           _buffer.write(self._blanks( _indent ) + "rcvUpdates5min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "rcvUpdates5min : \n" + self.rcvUpdates5min.toString( _indent + 2) + "\n")
        return _buffer.getvalue()
    
class DistExploreConnectionRqst( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.DistExploreConnectionRqst"
        
        self.distributorId: int
        self.connectionId: int
    def setDistributorId( self, value: int ):
        self.distributorId = value

    def getDistributorId( self ) -> int:
        return self.distributorId
    def setConnectionId( self, value: int ):
        self.connectionId = value

    def getConnectionId( self ) -> int:
        return self.connectionId

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: distributorId Type: long List: false
        _encoder.addLong( self.distributorId )
        # Encode Attribute: connectionId Type: long List: false
        _encoder.addLong( self.connectionId )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: distributorId Type:long List: false
        self.distributorId = _decoder.getLong()
        
        #Decode Attribute: connectionId Type:long List: false
        self.connectionId = _decoder.getLong()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "distributorId : " + str( self.distributorId) + "\n")
        _buffer.write(self._blanks( _indent ) + "connectionId : " + str( self.connectionId) + "\n")
        return _buffer.getvalue()
    
class DistExploreConnectionRsp( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.DistExploreConnectionRsp"
        
        self.connection: ConnectionEntry
    def setConnection( self, value: ConnectionEntry ):
        self.connection = value

    def getConnection( self ) -> ConnectionEntry:
        return self.connection

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: connection Type: ConnectionEntry List: false
        _encoder.addMessage( self.connection )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: connection Type:ConnectionEntry List: false
        self.connection = _decoder.getMessage()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        if self.connection is None:
           _buffer.write(self._blanks( _indent ) + "connection : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "connection : \n" + self.connection.toString( _indent + 2) + "\n")
        return _buffer.getvalue()
    
class DistExploreSubscriptionsRqst( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.DistExploreSubscriptionsRqst"
        
        self.distributorId: int
        self.connectionId: int
    def setDistributorId( self, value: int ):
        self.distributorId = value

    def getDistributorId( self ) -> int:
        return self.distributorId
    def setConnectionId( self, value: int ):
        self.connectionId = value

    def getConnectionId( self ) -> int:
        return self.connectionId

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: distributorId Type: long List: false
        _encoder.addLong( self.distributorId )
        # Encode Attribute: connectionId Type: long List: false
        _encoder.addLong( self.connectionId )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: distributorId Type:long List: false
        self.distributorId = _decoder.getLong()
        
        #Decode Attribute: connectionId Type:long List: false
        self.connectionId = _decoder.getLong()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "distributorId : " + str( self.distributorId) + "\n")
        _buffer.write(self._blanks( _indent ) + "connectionId : " + str( self.connectionId) + "\n")
        return _buffer.getvalue()
    
class DistExploreSubscriptionsRsp( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.DistExploreSubscriptionsRsp"
        
        self.mcaAddress: str
        self.mcaPort: int
        self.subscriptions: str
    def setMcaAddress( self, value: str ):
        self.mcaAddress = value

    def getMcaAddress( self ) -> str:
        return self.mcaAddress
    def setMcaPort( self, value: int ):
        self.mcaPort = value

    def getMcaPort( self ) -> int:
        return self.mcaPort
    def setSubscriptions( self, value: str ):
        self.subscriptions = value

    def getSubscriptions( self ) -> str:
        return self.subscriptions

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: mcaAddress Type: str List: false
        _encoder.addString( self.mcaAddress )
        # Encode Attribute: mcaPort Type: int List: false
        _encoder.addInt( self.mcaPort )
        # Encode Attribute: subscriptions Type: str List: false
        _encoder.addString( self.subscriptions )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: mcaAddress Type:str List: false
        self.mcaAddress = _decoder.getString()
        
        #Decode Attribute: mcaPort Type:int List: false
        self.mcaPort = _decoder.getInt()
        
        #Decode Attribute: subscriptions Type:str List: false
        self.subscriptions = _decoder.getString()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "mcaAddress : " + str( self.mcaAddress) + "\n")
        _buffer.write(self._blanks( _indent ) + "mcaPort : " + str( self.mcaPort) + "\n")
        _buffer.write(self._blanks( _indent ) + "subscriptions : " + str( self.subscriptions) + "\n")
        return _buffer.getvalue()
    
class DistExploreRetransmissionsRqst( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.DistExploreRetransmissionsRqst"
        
        self.distributorId: int
        self.connectionId: int
    def setDistributorId( self, value: int ):
        self.distributorId = value

    def getDistributorId( self ) -> int:
        return self.distributorId
    def setConnectionId( self, value: int ):
        self.connectionId = value

    def getConnectionId( self ) -> int:
        return self.connectionId

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: distributorId Type: long List: false
        _encoder.addLong( self.distributorId )
        # Encode Attribute: connectionId Type: long List: false
        _encoder.addLong( self.connectionId )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: distributorId Type:long List: false
        self.distributorId = _decoder.getLong()
        
        #Decode Attribute: connectionId Type:long List: false
        self.connectionId = _decoder.getLong()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "distributorId : " + str( self.distributorId) + "\n")
        _buffer.write(self._blanks( _indent ) + "connectionId : " + str( self.connectionId) + "\n")
        return _buffer.getvalue()
    
class DistExploreRetransmissonsRsp( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.DistExploreRetransmissonsRsp"
        
        self.mcaAddress: str
        self.mcaPort: int
        self.totalInRqst: int
        self.totalOutRqst: int
        self.totalSeenRqst: int
        self.inHosts: str
        self.outHosts: str
    def setMcaAddress( self, value: str ):
        self.mcaAddress = value

    def getMcaAddress( self ) -> str:
        return self.mcaAddress
    def setMcaPort( self, value: int ):
        self.mcaPort = value

    def getMcaPort( self ) -> int:
        return self.mcaPort
    def setTotalInRqst( self, value: int ):
        self.totalInRqst = value

    def getTotalInRqst( self ) -> int:
        return self.totalInRqst
    def setTotalOutRqst( self, value: int ):
        self.totalOutRqst = value

    def getTotalOutRqst( self ) -> int:
        return self.totalOutRqst
    def setTotalSeenRqst( self, value: int ):
        self.totalSeenRqst = value

    def getTotalSeenRqst( self ) -> int:
        return self.totalSeenRqst
    def setInHosts( self, value: str ):
        self.inHosts = value

    def getInHosts( self ) -> str:
        return self.inHosts
    def setOutHosts( self, value: str ):
        self.outHosts = value

    def getOutHosts( self ) -> str:
        return self.outHosts

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: mcaAddress Type: str List: false
        _encoder.addString( self.mcaAddress )
        # Encode Attribute: mcaPort Type: int List: false
        _encoder.addInt( self.mcaPort )
        # Encode Attribute: totalInRqst Type: int List: false
        _encoder.addInt( self.totalInRqst )
        # Encode Attribute: totalOutRqst Type: int List: false
        _encoder.addInt( self.totalOutRqst )
        # Encode Attribute: totalSeenRqst Type: int List: false
        _encoder.addInt( self.totalSeenRqst )
        # Encode Attribute: inHosts Type: str List: false
        _encoder.addString( self.inHosts )
        # Encode Attribute: outHosts Type: str List: false
        _encoder.addString( self.outHosts )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: mcaAddress Type:str List: false
        self.mcaAddress = _decoder.getString()
        
        #Decode Attribute: mcaPort Type:int List: false
        self.mcaPort = _decoder.getInt()
        
        #Decode Attribute: totalInRqst Type:int List: false
        self.totalInRqst = _decoder.getInt()
        
        #Decode Attribute: totalOutRqst Type:int List: false
        self.totalOutRqst = _decoder.getInt()
        
        #Decode Attribute: totalSeenRqst Type:int List: false
        self.totalSeenRqst = _decoder.getInt()
        
        #Decode Attribute: inHosts Type:str List: false
        self.inHosts = _decoder.getString()
        
        #Decode Attribute: outHosts Type:str List: false
        self.outHosts = _decoder.getString()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "mcaAddress : " + str( self.mcaAddress) + "\n")
        _buffer.write(self._blanks( _indent ) + "mcaPort : " + str( self.mcaPort) + "\n")
        _buffer.write(self._blanks( _indent ) + "totalInRqst : " + str( self.totalInRqst) + "\n")
        _buffer.write(self._blanks( _indent ) + "totalOutRqst : " + str( self.totalOutRqst) + "\n")
        _buffer.write(self._blanks( _indent ) + "totalSeenRqst : " + str( self.totalSeenRqst) + "\n")
        _buffer.write(self._blanks( _indent ) + "inHosts : " + str( self.inHosts) + "\n")
        _buffer.write(self._blanks( _indent ) + "outHosts : " + str( self.outHosts) + "\n")
        return _buffer.getvalue()
    
class NameValuePair( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.NameValuePair"
        
        self.name: str
        self.value: str
        self.code: str
    def setName( self, value: str ):
        self.name = value

    def getName( self ) -> str:
        return self.name
    def setValue( self, value: str ):
        self.value = value

    def getValue( self ) -> str:
        return self.value
    def setCode( self, value: str ):
        self.code = value

    def getCode( self ) -> str:
        return self.code

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: name Type: str List: false
        _encoder.addString( self.name )
        # Encode Attribute: value Type: str List: false
        _encoder.addString( self.value )
        # Encode Attribute: code Type: str List: false
        _encoder.addString( self.code )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: name Type:str List: false
        self.name = _decoder.getString()
        
        #Decode Attribute: value Type:str List: false
        self.value = _decoder.getString()
        
        #Decode Attribute: code Type:str List: false
        self.code = _decoder.getString()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "name : " + str( self.name) + "\n")
        _buffer.write(self._blanks( _indent ) + "value : " + str( self.value) + "\n")
        _buffer.write(self._blanks( _indent ) + "code : " + str( self.code) + "\n")
        return _buffer.getvalue()
    