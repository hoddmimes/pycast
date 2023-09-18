
from pymc.msg.messageif import MessageBase
from pymc.msg.messages import MessageAux
from pymc.msg.codec import Decoder
from pymc.msg.codec import Encoder
from io import StringIO
            
class DistNetMsg( MessageBase ):

    def __init__(self):
        
        self.classModule = "pymc.msg.generated.net_messages"
        self.className = "DistNetMsg"
        
        self._request: int
        self._timestamp: int
        self._is_request_message: bool
        self._message: MessageBase
    @property
    def request(self) -> int:
        return self._request

    @request.setter
    def request(self, value: int):
            self._request = value
        
    @property
    def timestamp(self) -> int:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: int):
            self._timestamp = value
        
    @property
    def is_request_message(self) -> bool:
        return self._is_request_message

    @is_request_message.setter
    def is_request_message(self, value: bool):
            self._is_request_message = value
        
    @property
    def message(self) -> MessageBase:
       return self.message

    @message.setter
    def message(self, value: MessageBase):
        self._message = value


        

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString(self.classModule)
        _encoder.addString(self.className)

        
        # Encode Attribute: request Type: long List: false
        _encoder.addLong( self._request )
        # Encode Attribute: timestamp Type: long List: false
        _encoder.addLong( self._timestamp )
        # Encode Attribute: is_request_message Type: bool List: false
        _encoder.addBool( self._is_request_message )
        # Encode Attribute: message Type: MessageBase List: false
        _encoder.addMessage( self._message )
        return _encoder.buffer


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.classModule = _decoder.getString()
        self.className = _decoder.getString()
        
        #Decode Attribute: request Type:long List: false
        self._request = _decoder.getLong()
        
        #Decode Attribute: timestamp Type:long List: false
        self._timestamp = _decoder.getLong()
        
        #Decode Attribute: is_request_message Type:bool List: false
        self._is_request_message = _decoder.getBool()
        
        #Decode Attribute: message Type:MessageBase List: false
        self._message = _decoder.getMessage()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "request : " + str( self.request) + "\n")
        _buffer.write(self._blanks( _indent ) + "timestamp : " + str( self.timestamp) + "\n")
        _buffer.write(self._blanks( _indent ) + "is_request_message : " + str( self.is_request_message) + "\n")
        if self.message is None:
           _buffer.write(self._blanks( _indent ) + "message : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "message : \n" + self.message.toString( _indent + 2) + "\n")
        return _buffer.getvalue()

    def __str__(self) ->str:
        return self.toString()
    
class DistDomainConnectionEntry( MessageBase ):

    def __init__(self):
        
        self.classModule = "pymc.msg.generated.net_messages"
        self.className = "DistDomainConnectionEntry"
        
        self._connection_id: int
        self._mc_address: str
        self._mc_port: int
        self._subscriptions: int
        self._in_retransmissions: int
        self._out_retransmissions: int
    @property
    def connection_id(self) -> int:
        return self._connection_id

    @connection_id.setter
    def connection_id(self, value: int):
            self._connection_id = value
        
    @property
    def mc_address(self) -> str:
        return self._mc_address

    @mc_address.setter
    def mc_address(self, value: str):
            self._mc_address = value
        
    @property
    def mc_port(self) -> int:
        return self._mc_port

    @mc_port.setter
    def mc_port(self, value: int):
            self._mc_port = value
        
    @property
    def subscriptions(self) -> int:
        return self._subscriptions

    @subscriptions.setter
    def subscriptions(self, value: int):
            self._subscriptions = value
        
    @property
    def in_retransmissions(self) -> int:
        return self._in_retransmissions

    @in_retransmissions.setter
    def in_retransmissions(self, value: int):
            self._in_retransmissions = value
        
    @property
    def out_retransmissions(self) -> int:
        return self._out_retransmissions

    @out_retransmissions.setter
    def out_retransmissions(self, value: int):
            self._out_retransmissions = value
        

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString(self.classModule)
        _encoder.addString(self.className)

        
        # Encode Attribute: connection_id Type: long List: false
        _encoder.addLong( self._connection_id )
        # Encode Attribute: mc_address Type: str List: false
        _encoder.addString( self._mc_address )
        # Encode Attribute: mc_port Type: int List: false
        _encoder.addInt( self._mc_port )
        # Encode Attribute: subscriptions Type: int List: false
        _encoder.addInt( self._subscriptions )
        # Encode Attribute: in_retransmissions Type: int List: false
        _encoder.addInt( self._in_retransmissions )
        # Encode Attribute: out_retransmissions Type: int List: false
        _encoder.addInt( self._out_retransmissions )
        return _encoder.buffer


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.classModule = _decoder.getString()
        self.className = _decoder.getString()
        
        #Decode Attribute: connection_id Type:long List: false
        self._connection_id = _decoder.getLong()
        
        #Decode Attribute: mc_address Type:str List: false
        self._mc_address = _decoder.getString()
        
        #Decode Attribute: mc_port Type:int List: false
        self._mc_port = _decoder.getInt()
        
        #Decode Attribute: subscriptions Type:int List: false
        self._subscriptions = _decoder.getInt()
        
        #Decode Attribute: in_retransmissions Type:int List: false
        self._in_retransmissions = _decoder.getInt()
        
        #Decode Attribute: out_retransmissions Type:int List: false
        self._out_retransmissions = _decoder.getInt()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "connection_id : " + str( self.connection_id) + "\n")
        _buffer.write(self._blanks( _indent ) + "mc_address : " + str( self.mc_address) + "\n")
        _buffer.write(self._blanks( _indent ) + "mc_port : " + str( self.mc_port) + "\n")
        _buffer.write(self._blanks( _indent ) + "subscriptions : " + str( self.subscriptions) + "\n")
        _buffer.write(self._blanks( _indent ) + "in_retransmissions : " + str( self.in_retransmissions) + "\n")
        _buffer.write(self._blanks( _indent ) + "out_retransmissions : " + str( self.out_retransmissions) + "\n")
        return _buffer.getvalue()

    def __str__(self) ->str:
        return self.toString()
    
class DistDomainDistributorEntry( MessageBase ):

    def __init__(self):
        
        self.classModule = "pymc.msg.generated.net_messages"
        self.className = "DistDomainDistributorEntry"
        
        self._distributor_id: int
        self._hostname: str
        self._hosta_ddress: str
        self._application_name: str
        self._application_id: int
        self._start_time: str
        self._in_retransmissions: int
        self._out_retransmissions: int
        self._connections: list
    @property
    def distributor_id(self) -> int:
        return self._distributor_id

    @distributor_id.setter
    def distributor_id(self, value: int):
            self._distributor_id = value
        
    @property
    def hostname(self) -> str:
        return self._hostname

    @hostname.setter
    def hostname(self, value: str):
            self._hostname = value
        
    @property
    def hosta_ddress(self) -> str:
        return self._hosta_ddress

    @hosta_ddress.setter
    def hosta_ddress(self, value: str):
            self._hosta_ddress = value
        
    @property
    def application_name(self) -> str:
        return self._application_name

    @application_name.setter
    def application_name(self, value: str):
            self._application_name = value
        
    @property
    def application_id(self) -> int:
        return self._application_id

    @application_id.setter
    def application_id(self, value: int):
            self._application_id = value
        
    @property
    def start_time(self) -> str:
        return self._start_time

    @start_time.setter
    def start_time(self, value: str):
            self._start_time = value
        
    @property
    def in_retransmissions(self) -> int:
        return self._in_retransmissions

    @in_retransmissions.setter
    def in_retransmissions(self, value: int):
            self._in_retransmissions = value
        
    @property
    def out_retransmissions(self) -> int:
        return self._out_retransmissions

    @out_retransmissions.setter
    def out_retransmissions(self, value: int):
            self._out_retransmissions = value
        

    @property
    def connections(self) -> list:
        return self._connections

    @connections.setter
    def connections(self, value: list):
        self._connections = value


        

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString(self.classModule)
        _encoder.addString(self.className)

        
        # Encode Attribute: distributor_id Type: long List: false
        _encoder.addLong( self._distributor_id )
        # Encode Attribute: hostname Type: str List: false
        _encoder.addString( self._hostname )
        # Encode Attribute: hosta_ddress Type: str List: false
        _encoder.addString( self._hosta_ddress )
        # Encode Attribute: application_name Type: str List: false
        _encoder.addString( self._application_name )
        # Encode Attribute: application_id Type: int List: false
        _encoder.addInt( self._application_id )
        # Encode Attribute: start_time Type: str List: false
        _encoder.addString( self._start_time )
        # Encode Attribute: in_retransmissions Type: int List: false
        _encoder.addInt( self._in_retransmissions )
        # Encode Attribute: out_retransmissions Type: int List: false
        _encoder.addInt( self._out_retransmissions )
        # Encode Attribute: connections Type: DistDomainConnectionEntry List: true
        MessageAux.addMessageList( _encoder, self._connections)
        return _encoder.buffer


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.classModule = _decoder.getString()
        self.className = _decoder.getString()
        
        #Decode Attribute: distributor_id Type:long List: false
        self._distributor_id = _decoder.getLong()
        
        #Decode Attribute: hostname Type:str List: false
        self._hostname = _decoder.getString()
        
        #Decode Attribute: hosta_ddress Type:str List: false
        self._hosta_ddress = _decoder.getString()
        
        #Decode Attribute: application_name Type:str List: false
        self._application_name = _decoder.getString()
        
        #Decode Attribute: application_id Type:int List: false
        self._application_id = _decoder.getInt()
        
        #Decode Attribute: start_time Type:str List: false
        self._start_time = _decoder.getString()
        
        #Decode Attribute: in_retransmissions Type:int List: false
        self._in_retransmissions = _decoder.getInt()
        
        #Decode Attribute: out_retransmissions Type:int List: false
        self._out_retransmissions = _decoder.getInt()
        
        #Decode Attribute: connections Type:DistDomainConnectionEntry List: true
        self._connections = MessageAux.getMessageList( _decoder )

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "distributor_id : " + str( self.distributor_id) + "\n")
        _buffer.write(self._blanks( _indent ) + "hostname : " + str( self.hostname) + "\n")
        _buffer.write(self._blanks( _indent ) + "hosta_ddress : " + str( self.hosta_ddress) + "\n")
        _buffer.write(self._blanks( _indent ) + "application_name : " + str( self.application_name) + "\n")
        _buffer.write(self._blanks( _indent ) + "application_id : " + str( self.application_id) + "\n")
        _buffer.write(self._blanks( _indent ) + "start_time : " + str( self.start_time) + "\n")
        _buffer.write(self._blanks( _indent ) + "in_retransmissions : " + str( self.in_retransmissions) + "\n")
        _buffer.write(self._blanks( _indent ) + "out_retransmissions : " + str( self.out_retransmissions) + "\n")
        if self.connections is None:
           _buffer.write(self._blanks( _indent ) + "connections : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "connections : \n")
           _idx = 0
           for _m in self.connections:
                _idx += 1;
                _buffer.write( self._blanks( _indent + 2 ) + "[" + str(_idx) +"] \n" )
                _buffer.write( _m.toString( _indent + 4) + "\n") 
        return _buffer.getvalue()

    def __str__(self) ->str:
        return self.toString()
    
class DistExploreDomainRqst( MessageBase ):

    def __init__(self):
        
        self.classModule = "pymc.msg.generated.net_messages"
        self.className = "DistExploreDomainRqst"
        

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString(self.classModule)
        _encoder.addString(self.className)

        
        return _encoder.buffer


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.classModule = _decoder.getString()
        self.className = _decoder.getString()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        return _buffer.getvalue()

    def __str__(self) ->str:
        return self.toString()
    
class DistExploreDomainRsp( MessageBase ):

    def __init__(self):
        
        self.classModule = "pymc.msg.generated.net_messages"
        self.className = "DistExploreDomainRsp"
        
        self._distributor: DistDomainDistributorEntry
    @property
    def distributor(self) -> DistDomainDistributorEntry:
       return self.distributor

    @distributor.setter
    def distributor(self, value: DistDomainDistributorEntry):
        self._distributor = value


        

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString(self.classModule)
        _encoder.addString(self.className)

        
        # Encode Attribute: distributor Type: DistDomainDistributorEntry List: false
        _encoder.addMessage( self._distributor )
        return _encoder.buffer


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.classModule = _decoder.getString()
        self.className = _decoder.getString()
        
        #Decode Attribute: distributor Type:DistDomainDistributorEntry List: false
        self._distributor = _decoder.getMessage()
        

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

    def __str__(self) ->str:
        return self.toString()
    
class DistributorEntry( MessageBase ):

    def __init__(self):
        
        self.classModule = "pymc.msg.generated.net_messages"
        self.className = "DistributorEntry"
        
        self._host_name: str
        self._hosta_address: str
        self._application_name: str
        self._application_id: int
        self._start_time: str
        self._connections: int
        self._distributor_id: int
        self._mem_max: int
        self._mem_used: int
        self._mem_free: int
        self._in_retransmissions: int
        self._out_retransmissions: int
        self._subscriptions: int
    @property
    def host_name(self) -> str:
        return self._host_name

    @host_name.setter
    def host_name(self, value: str):
            self._host_name = value
        
    @property
    def hosta_address(self) -> str:
        return self._hosta_address

    @hosta_address.setter
    def hosta_address(self, value: str):
            self._hosta_address = value
        
    @property
    def application_name(self) -> str:
        return self._application_name

    @application_name.setter
    def application_name(self, value: str):
            self._application_name = value
        
    @property
    def application_id(self) -> int:
        return self._application_id

    @application_id.setter
    def application_id(self, value: int):
            self._application_id = value
        
    @property
    def start_time(self) -> str:
        return self._start_time

    @start_time.setter
    def start_time(self, value: str):
            self._start_time = value
        
    @property
    def connections(self) -> int:
        return self._connections

    @connections.setter
    def connections(self, value: int):
            self._connections = value
        
    @property
    def distributor_id(self) -> int:
        return self._distributor_id

    @distributor_id.setter
    def distributor_id(self, value: int):
            self._distributor_id = value
        
    @property
    def mem_max(self) -> int:
        return self._mem_max

    @mem_max.setter
    def mem_max(self, value: int):
            self._mem_max = value
        
    @property
    def mem_used(self) -> int:
        return self._mem_used

    @mem_used.setter
    def mem_used(self, value: int):
            self._mem_used = value
        
    @property
    def mem_free(self) -> int:
        return self._mem_free

    @mem_free.setter
    def mem_free(self, value: int):
            self._mem_free = value
        
    @property
    def in_retransmissions(self) -> int:
        return self._in_retransmissions

    @in_retransmissions.setter
    def in_retransmissions(self, value: int):
            self._in_retransmissions = value
        
    @property
    def out_retransmissions(self) -> int:
        return self._out_retransmissions

    @out_retransmissions.setter
    def out_retransmissions(self, value: int):
            self._out_retransmissions = value
        
    @property
    def subscriptions(self) -> int:
        return self._subscriptions

    @subscriptions.setter
    def subscriptions(self, value: int):
            self._subscriptions = value
        

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString(self.classModule)
        _encoder.addString(self.className)

        
        # Encode Attribute: host_name Type: str List: false
        _encoder.addString( self._host_name )
        # Encode Attribute: hosta_address Type: str List: false
        _encoder.addString( self._hosta_address )
        # Encode Attribute: application_name Type: str List: false
        _encoder.addString( self._application_name )
        # Encode Attribute: application_id Type: int List: false
        _encoder.addInt( self._application_id )
        # Encode Attribute: start_time Type: str List: false
        _encoder.addString( self._start_time )
        # Encode Attribute: connections Type: int List: false
        _encoder.addInt( self._connections )
        # Encode Attribute: distributor_id Type: long List: false
        _encoder.addLong( self._distributor_id )
        # Encode Attribute: mem_max Type: long List: false
        _encoder.addLong( self._mem_max )
        # Encode Attribute: mem_used Type: long List: false
        _encoder.addLong( self._mem_used )
        # Encode Attribute: mem_free Type: long List: false
        _encoder.addLong( self._mem_free )
        # Encode Attribute: in_retransmissions Type: int List: false
        _encoder.addInt( self._in_retransmissions )
        # Encode Attribute: out_retransmissions Type: int List: false
        _encoder.addInt( self._out_retransmissions )
        # Encode Attribute: subscriptions Type: int List: false
        _encoder.addInt( self._subscriptions )
        return _encoder.buffer


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.classModule = _decoder.getString()
        self.className = _decoder.getString()
        
        #Decode Attribute: host_name Type:str List: false
        self._host_name = _decoder.getString()
        
        #Decode Attribute: hosta_address Type:str List: false
        self._hosta_address = _decoder.getString()
        
        #Decode Attribute: application_name Type:str List: false
        self._application_name = _decoder.getString()
        
        #Decode Attribute: application_id Type:int List: false
        self._application_id = _decoder.getInt()
        
        #Decode Attribute: start_time Type:str List: false
        self._start_time = _decoder.getString()
        
        #Decode Attribute: connections Type:int List: false
        self._connections = _decoder.getInt()
        
        #Decode Attribute: distributor_id Type:long List: false
        self._distributor_id = _decoder.getLong()
        
        #Decode Attribute: mem_max Type:long List: false
        self._mem_max = _decoder.getLong()
        
        #Decode Attribute: mem_used Type:long List: false
        self._mem_used = _decoder.getLong()
        
        #Decode Attribute: mem_free Type:long List: false
        self._mem_free = _decoder.getLong()
        
        #Decode Attribute: in_retransmissions Type:int List: false
        self._in_retransmissions = _decoder.getInt()
        
        #Decode Attribute: out_retransmissions Type:int List: false
        self._out_retransmissions = _decoder.getInt()
        
        #Decode Attribute: subscriptions Type:int List: false
        self._subscriptions = _decoder.getInt()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "host_name : " + str( self.host_name) + "\n")
        _buffer.write(self._blanks( _indent ) + "hosta_address : " + str( self.hosta_address) + "\n")
        _buffer.write(self._blanks( _indent ) + "application_name : " + str( self.application_name) + "\n")
        _buffer.write(self._blanks( _indent ) + "application_id : " + str( self.application_id) + "\n")
        _buffer.write(self._blanks( _indent ) + "start_time : " + str( self.start_time) + "\n")
        _buffer.write(self._blanks( _indent ) + "connections : " + str( self.connections) + "\n")
        _buffer.write(self._blanks( _indent ) + "distributor_id : " + str( self.distributor_id) + "\n")
        _buffer.write(self._blanks( _indent ) + "mem_max : " + str( self.mem_max) + "\n")
        _buffer.write(self._blanks( _indent ) + "mem_used : " + str( self.mem_used) + "\n")
        _buffer.write(self._blanks( _indent ) + "mem_free : " + str( self.mem_free) + "\n")
        _buffer.write(self._blanks( _indent ) + "in_retransmissions : " + str( self.in_retransmissions) + "\n")
        _buffer.write(self._blanks( _indent ) + "out_retransmissions : " + str( self.out_retransmissions) + "\n")
        _buffer.write(self._blanks( _indent ) + "subscriptions : " + str( self.subscriptions) + "\n")
        return _buffer.getvalue()

    def __str__(self) ->str:
        return self.toString()
    
class DistExploreDistributorRqst( MessageBase ):

    def __init__(self):
        
        self.classModule = "pymc.msg.generated.net_messages"
        self.className = "DistExploreDistributorRqst"
        
        self._distributor_id: int
    @property
    def distributor_id(self) -> int:
        return self._distributor_id

    @distributor_id.setter
    def distributor_id(self, value: int):
            self._distributor_id = value
        

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString(self.classModule)
        _encoder.addString(self.className)

        
        # Encode Attribute: distributor_id Type: long List: false
        _encoder.addLong( self._distributor_id )
        return _encoder.buffer


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.classModule = _decoder.getString()
        self.className = _decoder.getString()
        
        #Decode Attribute: distributor_id Type:long List: false
        self._distributor_id = _decoder.getLong()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "distributor_id : " + str( self.distributor_id) + "\n")
        return _buffer.getvalue()

    def __str__(self) ->str:
        return self.toString()
    
class DistExploreDistributorRsp( MessageBase ):

    def __init__(self):
        
        self.classModule = "pymc.msg.generated.net_messages"
        self.className = "DistExploreDistributorRsp"
        
        self._distributor: DistributorEntry
    @property
    def distributor(self) -> DistributorEntry:
       return self.distributor

    @distributor.setter
    def distributor(self, value: DistributorEntry):
        self._distributor = value


        

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString(self.classModule)
        _encoder.addString(self.className)

        
        # Encode Attribute: distributor Type: DistributorEntry List: false
        _encoder.addMessage( self._distributor )
        return _encoder.buffer


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.classModule = _decoder.getString()
        self.className = _decoder.getString()
        
        #Decode Attribute: distributor Type:DistributorEntry List: false
        self._distributor = _decoder.getMessage()
        

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

    def __str__(self) ->str:
        return self.toString()
    
class DataRateItem( MessageBase ):

    def __init__(self):
        
        self.classModule = "pymc.msg.generated.net_messages"
        self.className = "DataRateItem"
        
        self._total: int
        self._curr_value: int
        self._peak_value: int
        self._peak_time: str
    @property
    def total(self) -> int:
        return self._total

    @total.setter
    def total(self, value: int):
            self._total = value
        
    @property
    def curr_value(self) -> int:
        return self._curr_value

    @curr_value.setter
    def curr_value(self, value: int):
            self._curr_value = value
        
    @property
    def peak_value(self) -> int:
        return self._peak_value

    @peak_value.setter
    def peak_value(self, value: int):
            self._peak_value = value
        
    @property
    def peak_time(self) -> str:
        return self._peak_time

    @peak_time.setter
    def peak_time(self, value: str):
            self._peak_time = value
        

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString(self.classModule)
        _encoder.addString(self.className)

        
        # Encode Attribute: total Type: long List: false
        _encoder.addLong( self._total )
        # Encode Attribute: curr_value Type: int List: false
        _encoder.addInt( self._curr_value )
        # Encode Attribute: peak_value Type: int List: false
        _encoder.addInt( self._peak_value )
        # Encode Attribute: peak_time Type: str List: false
        _encoder.addString( self._peak_time )
        return _encoder.buffer


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.classModule = _decoder.getString()
        self.className = _decoder.getString()
        
        #Decode Attribute: total Type:long List: false
        self._total = _decoder.getLong()
        
        #Decode Attribute: curr_value Type:int List: false
        self._curr_value = _decoder.getInt()
        
        #Decode Attribute: peak_value Type:int List: false
        self._peak_value = _decoder.getInt()
        
        #Decode Attribute: peak_time Type:str List: false
        self._peak_time = _decoder.getString()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "total : " + str( self.total) + "\n")
        _buffer.write(self._blanks( _indent ) + "curr_value : " + str( self.curr_value) + "\n")
        _buffer.write(self._blanks( _indent ) + "peak_value : " + str( self.peak_value) + "\n")
        _buffer.write(self._blanks( _indent ) + "peak_time : " + str( self.peak_time) + "\n")
        return _buffer.getvalue()

    def __str__(self) ->str:
        return self.toString()
    
class QueueSizeItem( MessageBase ):

    def __init__(self):
        
        self.classModule = "pymc.msg.generated.net_messages"
        self.className = "QueueSizeItem"
        
        self._size: int
        self._peak_size: int
        self._peak_time: str
    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: int):
            self._size = value
        
    @property
    def peak_size(self) -> int:
        return self._peak_size

    @peak_size.setter
    def peak_size(self, value: int):
            self._peak_size = value
        
    @property
    def peak_time(self) -> str:
        return self._peak_time

    @peak_time.setter
    def peak_time(self, value: str):
            self._peak_time = value
        

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString(self.classModule)
        _encoder.addString(self.className)

        
        # Encode Attribute: size Type: long List: false
        _encoder.addLong( self._size )
        # Encode Attribute: peak_size Type: int List: false
        _encoder.addInt( self._peak_size )
        # Encode Attribute: peak_time Type: str List: false
        _encoder.addString( self._peak_time )
        return _encoder.buffer


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.classModule = _decoder.getString()
        self.className = _decoder.getString()
        
        #Decode Attribute: size Type:long List: false
        self._size = _decoder.getLong()
        
        #Decode Attribute: peak_size Type:int List: false
        self._peak_size = _decoder.getInt()
        
        #Decode Attribute: peak_time Type:str List: false
        self._peak_time = _decoder.getString()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "size : " + str( self.size) + "\n")
        _buffer.write(self._blanks( _indent ) + "peak_size : " + str( self.peak_size) + "\n")
        _buffer.write(self._blanks( _indent ) + "peak_time : " + str( self.peak_time) + "\n")
        return _buffer.getvalue()

    def __str__(self) ->str:
        return self.toString()
    
class ConnectionEntry( MessageBase ):

    def __init__(self):
        
        self.classModule = "pymc.msg.generated.net_messages"
        self.className = "ConnectionEntry"
        
        self._mc_address: str
        self._mc_port: int
        self._connection_id: int
        self._publishers: int
        self._subscribers: int
        self._subscriptions: int
        self._in_retransmissions: int
        self._out_retransmissions: int
        self._deliver_update_queue: QueueSizeItem
        self._xta_total_bytes: int
        self._xta_total_segments: int
        self._xta_total_updates: int
        self._xta_bytes: DataRateItem
        self._xtaSegments: DataRateItem
        self._xta_updates: DataRateItem
        self._xta_bytes_1min: DataRateItem
        self._xta_segments_1min: DataRateItem
        self._xta_updates_1min: DataRateItem
        self._xta_bytes_5min: DataRateItem
        self._xta_segments_5min: DataRateItem
        self._xta_updates_5min: DataRateItem
        self._rcv_total_bytes: int
        self._rcv_total_segments: int
        self._rcv_total_updates: int
        self._rcv_bytes: DataRateItem
        self._rcv_segments: DataRateItem
        self._rcv_updates: DataRateItem
        self._rcv_bytes_1min: DataRateItem
        self._rcv_segments_1min: DataRateItem
        self._rcv_updates_1min: DataRateItem
        self._rcv_bytes_5min: DataRateItem
        self._rcv_segments_5min: DataRateItem
        self._rcv_updates_5min: DataRateItem
    @property
    def mc_address(self) -> str:
        return self._mc_address

    @mc_address.setter
    def mc_address(self, value: str):
            self._mc_address = value
        
    @property
    def mc_port(self) -> int:
        return self._mc_port

    @mc_port.setter
    def mc_port(self, value: int):
            self._mc_port = value
        
    @property
    def connection_id(self) -> int:
        return self._connection_id

    @connection_id.setter
    def connection_id(self, value: int):
            self._connection_id = value
        
    @property
    def publishers(self) -> int:
        return self._publishers

    @publishers.setter
    def publishers(self, value: int):
            self._publishers = value
        
    @property
    def subscribers(self) -> int:
        return self._subscribers

    @subscribers.setter
    def subscribers(self, value: int):
            self._subscribers = value
        
    @property
    def subscriptions(self) -> int:
        return self._subscriptions

    @subscriptions.setter
    def subscriptions(self, value: int):
            self._subscriptions = value
        
    @property
    def in_retransmissions(self) -> int:
        return self._in_retransmissions

    @in_retransmissions.setter
    def in_retransmissions(self, value: int):
            self._in_retransmissions = value
        
    @property
    def out_retransmissions(self) -> int:
        return self._out_retransmissions

    @out_retransmissions.setter
    def out_retransmissions(self, value: int):
            self._out_retransmissions = value
        
    @property
    def deliver_update_queue(self) -> QueueSizeItem:
       return self.deliver_update_queue

    @deliver_update_queue.setter
    def deliver_update_queue(self, value: QueueSizeItem):
        self._deliver_update_queue = value


        
    @property
    def xta_total_bytes(self) -> int:
        return self._xta_total_bytes

    @xta_total_bytes.setter
    def xta_total_bytes(self, value: int):
            self._xta_total_bytes = value
        
    @property
    def xta_total_segments(self) -> int:
        return self._xta_total_segments

    @xta_total_segments.setter
    def xta_total_segments(self, value: int):
            self._xta_total_segments = value
        
    @property
    def xta_total_updates(self) -> int:
        return self._xta_total_updates

    @xta_total_updates.setter
    def xta_total_updates(self, value: int):
            self._xta_total_updates = value
        
    @property
    def xta_bytes(self) -> DataRateItem:
       return self.xta_bytes

    @xta_bytes.setter
    def xta_bytes(self, value: DataRateItem):
        self._xta_bytes = value


        
    @property
    def xtaSegments(self) -> DataRateItem:
       return self.xtaSegments

    @xtaSegments.setter
    def xtaSegments(self, value: DataRateItem):
        self._xtaSegments = value


        
    @property
    def xta_updates(self) -> DataRateItem:
       return self.xta_updates

    @xta_updates.setter
    def xta_updates(self, value: DataRateItem):
        self._xta_updates = value


        
    @property
    def xta_bytes_1min(self) -> DataRateItem:
       return self.xta_bytes_1min

    @xta_bytes_1min.setter
    def xta_bytes_1min(self, value: DataRateItem):
        self._xta_bytes_1min = value


        
    @property
    def xta_segments_1min(self) -> DataRateItem:
       return self.xta_segments_1min

    @xta_segments_1min.setter
    def xta_segments_1min(self, value: DataRateItem):
        self._xta_segments_1min = value


        
    @property
    def xta_updates_1min(self) -> DataRateItem:
       return self.xta_updates_1min

    @xta_updates_1min.setter
    def xta_updates_1min(self, value: DataRateItem):
        self._xta_updates_1min = value


        
    @property
    def xta_bytes_5min(self) -> DataRateItem:
       return self.xta_bytes_5min

    @xta_bytes_5min.setter
    def xta_bytes_5min(self, value: DataRateItem):
        self._xta_bytes_5min = value


        
    @property
    def xta_segments_5min(self) -> DataRateItem:
       return self.xta_segments_5min

    @xta_segments_5min.setter
    def xta_segments_5min(self, value: DataRateItem):
        self._xta_segments_5min = value


        
    @property
    def xta_updates_5min(self) -> DataRateItem:
       return self.xta_updates_5min

    @xta_updates_5min.setter
    def xta_updates_5min(self, value: DataRateItem):
        self._xta_updates_5min = value


        
    @property
    def rcv_total_bytes(self) -> int:
        return self._rcv_total_bytes

    @rcv_total_bytes.setter
    def rcv_total_bytes(self, value: int):
            self._rcv_total_bytes = value
        
    @property
    def rcv_total_segments(self) -> int:
        return self._rcv_total_segments

    @rcv_total_segments.setter
    def rcv_total_segments(self, value: int):
            self._rcv_total_segments = value
        
    @property
    def rcv_total_updates(self) -> int:
        return self._rcv_total_updates

    @rcv_total_updates.setter
    def rcv_total_updates(self, value: int):
            self._rcv_total_updates = value
        
    @property
    def rcv_bytes(self) -> DataRateItem:
       return self.rcv_bytes

    @rcv_bytes.setter
    def rcv_bytes(self, value: DataRateItem):
        self._rcv_bytes = value


        
    @property
    def rcv_segments(self) -> DataRateItem:
       return self.rcv_segments

    @rcv_segments.setter
    def rcv_segments(self, value: DataRateItem):
        self._rcv_segments = value


        
    @property
    def rcv_updates(self) -> DataRateItem:
       return self.rcv_updates

    @rcv_updates.setter
    def rcv_updates(self, value: DataRateItem):
        self._rcv_updates = value


        
    @property
    def rcv_bytes_1min(self) -> DataRateItem:
       return self.rcv_bytes_1min

    @rcv_bytes_1min.setter
    def rcv_bytes_1min(self, value: DataRateItem):
        self._rcv_bytes_1min = value


        
    @property
    def rcv_segments_1min(self) -> DataRateItem:
       return self.rcv_segments_1min

    @rcv_segments_1min.setter
    def rcv_segments_1min(self, value: DataRateItem):
        self._rcv_segments_1min = value


        
    @property
    def rcv_updates_1min(self) -> DataRateItem:
       return self.rcv_updates_1min

    @rcv_updates_1min.setter
    def rcv_updates_1min(self, value: DataRateItem):
        self._rcv_updates_1min = value


        
    @property
    def rcv_bytes_5min(self) -> DataRateItem:
       return self.rcv_bytes_5min

    @rcv_bytes_5min.setter
    def rcv_bytes_5min(self, value: DataRateItem):
        self._rcv_bytes_5min = value


        
    @property
    def rcv_segments_5min(self) -> DataRateItem:
       return self.rcv_segments_5min

    @rcv_segments_5min.setter
    def rcv_segments_5min(self, value: DataRateItem):
        self._rcv_segments_5min = value


        
    @property
    def rcv_updates_5min(self) -> DataRateItem:
       return self.rcv_updates_5min

    @rcv_updates_5min.setter
    def rcv_updates_5min(self, value: DataRateItem):
        self._rcv_updates_5min = value


        

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString(self.classModule)
        _encoder.addString(self.className)

        
        # Encode Attribute: mc_address Type: str List: false
        _encoder.addString( self._mc_address )
        # Encode Attribute: mc_port Type: int List: false
        _encoder.addInt( self._mc_port )
        # Encode Attribute: connection_id Type: long List: false
        _encoder.addLong( self._connection_id )
        # Encode Attribute: publishers Type: int List: false
        _encoder.addInt( self._publishers )
        # Encode Attribute: subscribers Type: int List: false
        _encoder.addInt( self._subscribers )
        # Encode Attribute: subscriptions Type: int List: false
        _encoder.addInt( self._subscriptions )
        # Encode Attribute: in_retransmissions Type: int List: false
        _encoder.addInt( self._in_retransmissions )
        # Encode Attribute: out_retransmissions Type: int List: false
        _encoder.addInt( self._out_retransmissions )
        # Encode Attribute: deliver_update_queue Type: QueueSizeItem List: false
        _encoder.addMessage( self._deliver_update_queue )
        # Encode Attribute: xta_total_bytes Type: long List: false
        _encoder.addLong( self._xta_total_bytes )
        # Encode Attribute: xta_total_segments Type: long List: false
        _encoder.addLong( self._xta_total_segments )
        # Encode Attribute: xta_total_updates Type: long List: false
        _encoder.addLong( self._xta_total_updates )
        # Encode Attribute: xta_bytes Type: DataRateItem List: false
        _encoder.addMessage( self._xta_bytes )
        # Encode Attribute: xtaSegments Type: DataRateItem List: false
        _encoder.addMessage( self._xtaSegments )
        # Encode Attribute: xta_updates Type: DataRateItem List: false
        _encoder.addMessage( self._xta_updates )
        # Encode Attribute: xta_bytes_1min Type: DataRateItem List: false
        _encoder.addMessage( self._xta_bytes_1min )
        # Encode Attribute: xta_segments_1min Type: DataRateItem List: false
        _encoder.addMessage( self._xta_segments_1min )
        # Encode Attribute: xta_updates_1min Type: DataRateItem List: false
        _encoder.addMessage( self._xta_updates_1min )
        # Encode Attribute: xta_bytes_5min Type: DataRateItem List: false
        _encoder.addMessage( self._xta_bytes_5min )
        # Encode Attribute: xta_segments_5min Type: DataRateItem List: false
        _encoder.addMessage( self._xta_segments_5min )
        # Encode Attribute: xta_updates_5min Type: DataRateItem List: false
        _encoder.addMessage( self._xta_updates_5min )
        # Encode Attribute: rcv_total_bytes Type: long List: false
        _encoder.addLong( self._rcv_total_bytes )
        # Encode Attribute: rcv_total_segments Type: long List: false
        _encoder.addLong( self._rcv_total_segments )
        # Encode Attribute: rcv_total_updates Type: long List: false
        _encoder.addLong( self._rcv_total_updates )
        # Encode Attribute: rcv_bytes Type: DataRateItem List: false
        _encoder.addMessage( self._rcv_bytes )
        # Encode Attribute: rcv_segments Type: DataRateItem List: false
        _encoder.addMessage( self._rcv_segments )
        # Encode Attribute: rcv_updates Type: DataRateItem List: false
        _encoder.addMessage( self._rcv_updates )
        # Encode Attribute: rcv_bytes_1min Type: DataRateItem List: false
        _encoder.addMessage( self._rcv_bytes_1min )
        # Encode Attribute: rcv_segments_1min Type: DataRateItem List: false
        _encoder.addMessage( self._rcv_segments_1min )
        # Encode Attribute: rcv_updates_1min Type: DataRateItem List: false
        _encoder.addMessage( self._rcv_updates_1min )
        # Encode Attribute: rcv_bytes_5min Type: DataRateItem List: false
        _encoder.addMessage( self._rcv_bytes_5min )
        # Encode Attribute: rcv_segments_5min Type: DataRateItem List: false
        _encoder.addMessage( self._rcv_segments_5min )
        # Encode Attribute: rcv_updates_5min Type: DataRateItem List: false
        _encoder.addMessage( self._rcv_updates_5min )
        return _encoder.buffer


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.classModule = _decoder.getString()
        self.className = _decoder.getString()
        
        #Decode Attribute: mc_address Type:str List: false
        self._mc_address = _decoder.getString()
        
        #Decode Attribute: mc_port Type:int List: false
        self._mc_port = _decoder.getInt()
        
        #Decode Attribute: connection_id Type:long List: false
        self._connection_id = _decoder.getLong()
        
        #Decode Attribute: publishers Type:int List: false
        self._publishers = _decoder.getInt()
        
        #Decode Attribute: subscribers Type:int List: false
        self._subscribers = _decoder.getInt()
        
        #Decode Attribute: subscriptions Type:int List: false
        self._subscriptions = _decoder.getInt()
        
        #Decode Attribute: in_retransmissions Type:int List: false
        self._in_retransmissions = _decoder.getInt()
        
        #Decode Attribute: out_retransmissions Type:int List: false
        self._out_retransmissions = _decoder.getInt()
        
        #Decode Attribute: deliver_update_queue Type:QueueSizeItem List: false
        self._deliver_update_queue = _decoder.getMessage()
        
        #Decode Attribute: xta_total_bytes Type:long List: false
        self._xta_total_bytes = _decoder.getLong()
        
        #Decode Attribute: xta_total_segments Type:long List: false
        self._xta_total_segments = _decoder.getLong()
        
        #Decode Attribute: xta_total_updates Type:long List: false
        self._xta_total_updates = _decoder.getLong()
        
        #Decode Attribute: xta_bytes Type:DataRateItem List: false
        self._xta_bytes = _decoder.getMessage()
        
        #Decode Attribute: xtaSegments Type:DataRateItem List: false
        self._xtaSegments = _decoder.getMessage()
        
        #Decode Attribute: xta_updates Type:DataRateItem List: false
        self._xta_updates = _decoder.getMessage()
        
        #Decode Attribute: xta_bytes_1min Type:DataRateItem List: false
        self._xta_bytes_1min = _decoder.getMessage()
        
        #Decode Attribute: xta_segments_1min Type:DataRateItem List: false
        self._xta_segments_1min = _decoder.getMessage()
        
        #Decode Attribute: xta_updates_1min Type:DataRateItem List: false
        self._xta_updates_1min = _decoder.getMessage()
        
        #Decode Attribute: xta_bytes_5min Type:DataRateItem List: false
        self._xta_bytes_5min = _decoder.getMessage()
        
        #Decode Attribute: xta_segments_5min Type:DataRateItem List: false
        self._xta_segments_5min = _decoder.getMessage()
        
        #Decode Attribute: xta_updates_5min Type:DataRateItem List: false
        self._xta_updates_5min = _decoder.getMessage()
        
        #Decode Attribute: rcv_total_bytes Type:long List: false
        self._rcv_total_bytes = _decoder.getLong()
        
        #Decode Attribute: rcv_total_segments Type:long List: false
        self._rcv_total_segments = _decoder.getLong()
        
        #Decode Attribute: rcv_total_updates Type:long List: false
        self._rcv_total_updates = _decoder.getLong()
        
        #Decode Attribute: rcv_bytes Type:DataRateItem List: false
        self._rcv_bytes = _decoder.getMessage()
        
        #Decode Attribute: rcv_segments Type:DataRateItem List: false
        self._rcv_segments = _decoder.getMessage()
        
        #Decode Attribute: rcv_updates Type:DataRateItem List: false
        self._rcv_updates = _decoder.getMessage()
        
        #Decode Attribute: rcv_bytes_1min Type:DataRateItem List: false
        self._rcv_bytes_1min = _decoder.getMessage()
        
        #Decode Attribute: rcv_segments_1min Type:DataRateItem List: false
        self._rcv_segments_1min = _decoder.getMessage()
        
        #Decode Attribute: rcv_updates_1min Type:DataRateItem List: false
        self._rcv_updates_1min = _decoder.getMessage()
        
        #Decode Attribute: rcv_bytes_5min Type:DataRateItem List: false
        self._rcv_bytes_5min = _decoder.getMessage()
        
        #Decode Attribute: rcv_segments_5min Type:DataRateItem List: false
        self._rcv_segments_5min = _decoder.getMessage()
        
        #Decode Attribute: rcv_updates_5min Type:DataRateItem List: false
        self._rcv_updates_5min = _decoder.getMessage()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "mc_address : " + str( self.mc_address) + "\n")
        _buffer.write(self._blanks( _indent ) + "mc_port : " + str( self.mc_port) + "\n")
        _buffer.write(self._blanks( _indent ) + "connection_id : " + str( self.connection_id) + "\n")
        _buffer.write(self._blanks( _indent ) + "publishers : " + str( self.publishers) + "\n")
        _buffer.write(self._blanks( _indent ) + "subscribers : " + str( self.subscribers) + "\n")
        _buffer.write(self._blanks( _indent ) + "subscriptions : " + str( self.subscriptions) + "\n")
        _buffer.write(self._blanks( _indent ) + "in_retransmissions : " + str( self.in_retransmissions) + "\n")
        _buffer.write(self._blanks( _indent ) + "out_retransmissions : " + str( self.out_retransmissions) + "\n")
        if self.deliver_update_queue is None:
           _buffer.write(self._blanks( _indent ) + "deliver_update_queue : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "deliver_update_queue : \n" + self.deliver_update_queue.toString( _indent + 2) + "\n")
        _buffer.write(self._blanks( _indent ) + "xta_total_bytes : " + str( self.xta_total_bytes) + "\n")
        _buffer.write(self._blanks( _indent ) + "xta_total_segments : " + str( self.xta_total_segments) + "\n")
        _buffer.write(self._blanks( _indent ) + "xta_total_updates : " + str( self.xta_total_updates) + "\n")
        if self.xta_bytes is None:
           _buffer.write(self._blanks( _indent ) + "xta_bytes : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "xta_bytes : \n" + self.xta_bytes.toString( _indent + 2) + "\n")
        if self.xtaSegments is None:
           _buffer.write(self._blanks( _indent ) + "xtaSegments : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "xtaSegments : \n" + self.xtaSegments.toString( _indent + 2) + "\n")
        if self.xta_updates is None:
           _buffer.write(self._blanks( _indent ) + "xta_updates : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "xta_updates : \n" + self.xta_updates.toString( _indent + 2) + "\n")
        if self.xta_bytes_1min is None:
           _buffer.write(self._blanks( _indent ) + "xta_bytes_1min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "xta_bytes_1min : \n" + self.xta_bytes_1min.toString( _indent + 2) + "\n")
        if self.xta_segments_1min is None:
           _buffer.write(self._blanks( _indent ) + "xta_segments_1min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "xta_segments_1min : \n" + self.xta_segments_1min.toString( _indent + 2) + "\n")
        if self.xta_updates_1min is None:
           _buffer.write(self._blanks( _indent ) + "xta_updates_1min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "xta_updates_1min : \n" + self.xta_updates_1min.toString( _indent + 2) + "\n")
        if self.xta_bytes_5min is None:
           _buffer.write(self._blanks( _indent ) + "xta_bytes_5min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "xta_bytes_5min : \n" + self.xta_bytes_5min.toString( _indent + 2) + "\n")
        if self.xta_segments_5min is None:
           _buffer.write(self._blanks( _indent ) + "xta_segments_5min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "xta_segments_5min : \n" + self.xta_segments_5min.toString( _indent + 2) + "\n")
        if self.xta_updates_5min is None:
           _buffer.write(self._blanks( _indent ) + "xta_updates_5min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "xta_updates_5min : \n" + self.xta_updates_5min.toString( _indent + 2) + "\n")
        _buffer.write(self._blanks( _indent ) + "rcv_total_bytes : " + str( self.rcv_total_bytes) + "\n")
        _buffer.write(self._blanks( _indent ) + "rcv_total_segments : " + str( self.rcv_total_segments) + "\n")
        _buffer.write(self._blanks( _indent ) + "rcv_total_updates : " + str( self.rcv_total_updates) + "\n")
        if self.rcv_bytes is None:
           _buffer.write(self._blanks( _indent ) + "rcv_bytes : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "rcv_bytes : \n" + self.rcv_bytes.toString( _indent + 2) + "\n")
        if self.rcv_segments is None:
           _buffer.write(self._blanks( _indent ) + "rcv_segments : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "rcv_segments : \n" + self.rcv_segments.toString( _indent + 2) + "\n")
        if self.rcv_updates is None:
           _buffer.write(self._blanks( _indent ) + "rcv_updates : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "rcv_updates : \n" + self.rcv_updates.toString( _indent + 2) + "\n")
        if self.rcv_bytes_1min is None:
           _buffer.write(self._blanks( _indent ) + "rcv_bytes_1min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "rcv_bytes_1min : \n" + self.rcv_bytes_1min.toString( _indent + 2) + "\n")
        if self.rcv_segments_1min is None:
           _buffer.write(self._blanks( _indent ) + "rcv_segments_1min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "rcv_segments_1min : \n" + self.rcv_segments_1min.toString( _indent + 2) + "\n")
        if self.rcv_updates_1min is None:
           _buffer.write(self._blanks( _indent ) + "rcv_updates_1min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "rcv_updates_1min : \n" + self.rcv_updates_1min.toString( _indent + 2) + "\n")
        if self.rcv_bytes_5min is None:
           _buffer.write(self._blanks( _indent ) + "rcv_bytes_5min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "rcv_bytes_5min : \n" + self.rcv_bytes_5min.toString( _indent + 2) + "\n")
        if self.rcv_segments_5min is None:
           _buffer.write(self._blanks( _indent ) + "rcv_segments_5min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "rcv_segments_5min : \n" + self.rcv_segments_5min.toString( _indent + 2) + "\n")
        if self.rcv_updates_5min is None:
           _buffer.write(self._blanks( _indent ) + "rcv_updates_5min : None \n")
        else:
                    
           _buffer.write(self._blanks( _indent ) + "rcv_updates_5min : \n" + self.rcv_updates_5min.toString( _indent + 2) + "\n")
        return _buffer.getvalue()

    def __str__(self) ->str:
        return self.toString()
    
class DistExploreConnectionRqst( MessageBase ):

    def __init__(self):
        
        self.classModule = "pymc.msg.generated.net_messages"
        self.className = "DistExploreConnectionRqst"
        
        self._distributor_id: int
        self._connection_id: int
    @property
    def distributor_id(self) -> int:
        return self._distributor_id

    @distributor_id.setter
    def distributor_id(self, value: int):
            self._distributor_id = value
        
    @property
    def connection_id(self) -> int:
        return self._connection_id

    @connection_id.setter
    def connection_id(self, value: int):
            self._connection_id = value
        

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString(self.classModule)
        _encoder.addString(self.className)

        
        # Encode Attribute: distributor_id Type: long List: false
        _encoder.addLong( self._distributor_id )
        # Encode Attribute: connection_id Type: long List: false
        _encoder.addLong( self._connection_id )
        return _encoder.buffer


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.classModule = _decoder.getString()
        self.className = _decoder.getString()
        
        #Decode Attribute: distributor_id Type:long List: false
        self._distributor_id = _decoder.getLong()
        
        #Decode Attribute: connection_id Type:long List: false
        self._connection_id = _decoder.getLong()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "distributor_id : " + str( self.distributor_id) + "\n")
        _buffer.write(self._blanks( _indent ) + "connection_id : " + str( self.connection_id) + "\n")
        return _buffer.getvalue()

    def __str__(self) ->str:
        return self.toString()
    
class DistExploreConnectionRsp( MessageBase ):

    def __init__(self):
        
        self.classModule = "pymc.msg.generated.net_messages"
        self.className = "DistExploreConnectionRsp"
        
        self._connection: ConnectionEntry
    @property
    def connection(self) -> ConnectionEntry:
       return self.connection

    @connection.setter
    def connection(self, value: ConnectionEntry):
        self._connection = value


        

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString(self.classModule)
        _encoder.addString(self.className)

        
        # Encode Attribute: connection Type: ConnectionEntry List: false
        _encoder.addMessage( self._connection )
        return _encoder.buffer


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.classModule = _decoder.getString()
        self.className = _decoder.getString()
        
        #Decode Attribute: connection Type:ConnectionEntry List: false
        self._connection = _decoder.getMessage()
        

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

    def __str__(self) ->str:
        return self.toString()
    
class DistExploreSubscriptionsRqst( MessageBase ):

    def __init__(self):
        
        self.classModule = "pymc.msg.generated.net_messages"
        self.className = "DistExploreSubscriptionsRqst"
        
        self._distributor_id: int
        self._connection_id: int
    @property
    def distributor_id(self) -> int:
        return self._distributor_id

    @distributor_id.setter
    def distributor_id(self, value: int):
            self._distributor_id = value
        
    @property
    def connection_id(self) -> int:
        return self._connection_id

    @connection_id.setter
    def connection_id(self, value: int):
            self._connection_id = value
        

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString(self.classModule)
        _encoder.addString(self.className)

        
        # Encode Attribute: distributor_id Type: long List: false
        _encoder.addLong( self._distributor_id )
        # Encode Attribute: connection_id Type: long List: false
        _encoder.addLong( self._connection_id )
        return _encoder.buffer


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.classModule = _decoder.getString()
        self.className = _decoder.getString()
        
        #Decode Attribute: distributor_id Type:long List: false
        self._distributor_id = _decoder.getLong()
        
        #Decode Attribute: connection_id Type:long List: false
        self._connection_id = _decoder.getLong()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "distributor_id : " + str( self.distributor_id) + "\n")
        _buffer.write(self._blanks( _indent ) + "connection_id : " + str( self.connection_id) + "\n")
        return _buffer.getvalue()

    def __str__(self) ->str:
        return self.toString()
    
class DistExploreSubscriptionsRsp( MessageBase ):

    def __init__(self):
        
        self.classModule = "pymc.msg.generated.net_messages"
        self.className = "DistExploreSubscriptionsRsp"
        
        self._mc_address: str
        self._mc_port: int
        self._subscriptions: list
    @property
    def mc_address(self) -> str:
        return self._mc_address

    @mc_address.setter
    def mc_address(self, value: str):
            self._mc_address = value
        
    @property
    def mc_port(self) -> int:
        return self._mc_port

    @mc_port.setter
    def mc_port(self, value: int):
            self._mc_port = value
        
    @property
    def subscriptions(self) -> list:
        return self._subscriptions

    @subscriptions.setter
    def subscriptions(self, value: list):
        self._subscriptions = value
        

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString(self.classModule)
        _encoder.addString(self.className)

        
        # Encode Attribute: mc_address Type: str List: false
        _encoder.addString( self._mc_address )
        # Encode Attribute: mc_port Type: int List: false
        _encoder.addInt( self._mc_port )
        # Encode Attribute: subscriptions Type: str List: true
            # Encode str list
        MessageAux.addStringList( _encoder, self._subscriptions  )
        return _encoder.buffer


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.classModule = _decoder.getString()
        self.className = _decoder.getString()
        
        #Decode Attribute: mc_address Type:str List: false
        self._mc_address = _decoder.getString()
        
        #Decode Attribute: mc_port Type:int List: false
        self._mc_port = _decoder.getInt()
        
        #Decode Attribute: subscriptions Type:str List: true
        self._subscriptions = MessageAux.getStringList( _decoder )

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "mc_address : " + str( self.mc_address) + "\n")
        _buffer.write(self._blanks( _indent ) + "mc_port : " + str( self.mc_port) + "\n")
        _buffer.write(self._blanks( _indent ) + "subscriptions : " + str( self.subscriptions) + "\n")
        return _buffer.getvalue()

    def __str__(self) ->str:
        return self.toString()
    
class DistExploreRetransmissionsRqst( MessageBase ):

    def __init__(self):
        
        self.classModule = "pymc.msg.generated.net_messages"
        self.className = "DistExploreRetransmissionsRqst"
        
        self._distributor_id: int
        self._connection_id: int
    @property
    def distributor_id(self) -> int:
        return self._distributor_id

    @distributor_id.setter
    def distributor_id(self, value: int):
            self._distributor_id = value
        
    @property
    def connection_id(self) -> int:
        return self._connection_id

    @connection_id.setter
    def connection_id(self, value: int):
            self._connection_id = value
        

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString(self.classModule)
        _encoder.addString(self.className)

        
        # Encode Attribute: distributor_id Type: long List: false
        _encoder.addLong( self._distributor_id )
        # Encode Attribute: connection_id Type: long List: false
        _encoder.addLong( self._connection_id )
        return _encoder.buffer


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.classModule = _decoder.getString()
        self.className = _decoder.getString()
        
        #Decode Attribute: distributor_id Type:long List: false
        self._distributor_id = _decoder.getLong()
        
        #Decode Attribute: connection_id Type:long List: false
        self._connection_id = _decoder.getLong()
        

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "distributor_id : " + str( self.distributor_id) + "\n")
        _buffer.write(self._blanks( _indent ) + "connection_id : " + str( self.connection_id) + "\n")
        return _buffer.getvalue()

    def __str__(self) ->str:
        return self.toString()
    
class DistExploreRetransmissonsRsp( MessageBase ):

    def __init__(self):
        
        self.classModule = "pymc.msg.generated.net_messages"
        self.className = "DistExploreRetransmissonsRsp"
        
        self._mc_address: str
        self._mc_port: int
        self._total_in_rqst: int
        self._total_out_rqst: int
        self._total_seen_rqst: int
        self._in_hosts: list
        self._out_hosts: list
    @property
    def mc_address(self) -> str:
        return self._mc_address

    @mc_address.setter
    def mc_address(self, value: str):
            self._mc_address = value
        
    @property
    def mc_port(self) -> int:
        return self._mc_port

    @mc_port.setter
    def mc_port(self, value: int):
            self._mc_port = value
        
    @property
    def total_in_rqst(self) -> int:
        return self._total_in_rqst

    @total_in_rqst.setter
    def total_in_rqst(self, value: int):
            self._total_in_rqst = value
        
    @property
    def total_out_rqst(self) -> int:
        return self._total_out_rqst

    @total_out_rqst.setter
    def total_out_rqst(self, value: int):
            self._total_out_rqst = value
        
    @property
    def total_seen_rqst(self) -> int:
        return self._total_seen_rqst

    @total_seen_rqst.setter
    def total_seen_rqst(self, value: int):
            self._total_seen_rqst = value
        
    @property
    def in_hosts(self) -> list:
        return self._in_hosts

    @in_hosts.setter
    def in_hosts(self, value: list):
        self._in_hosts = value
        
    @property
    def out_hosts(self) -> list:
        return self._out_hosts

    @out_hosts.setter
    def out_hosts(self, value: list):
        self._out_hosts = value
        

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString(self.classModule)
        _encoder.addString(self.className)

        
        # Encode Attribute: mc_address Type: str List: false
        _encoder.addString( self._mc_address )
        # Encode Attribute: mc_port Type: int List: false
        _encoder.addInt( self._mc_port )
        # Encode Attribute: total_in_rqst Type: int List: false
        _encoder.addInt( self._total_in_rqst )
        # Encode Attribute: total_out_rqst Type: int List: false
        _encoder.addInt( self._total_out_rqst )
        # Encode Attribute: total_seen_rqst Type: int List: false
        _encoder.addInt( self._total_seen_rqst )
        # Encode Attribute: in_hosts Type: str List: true
            # Encode str list
        MessageAux.addStringList( _encoder, self._in_hosts  )
        # Encode Attribute: out_hosts Type: str List: true
            # Encode str list
        MessageAux.addStringList( _encoder, self._out_hosts  )
        return _encoder.buffer


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.classModule = _decoder.getString()
        self.className = _decoder.getString()
        
        #Decode Attribute: mc_address Type:str List: false
        self._mc_address = _decoder.getString()
        
        #Decode Attribute: mc_port Type:int List: false
        self._mc_port = _decoder.getInt()
        
        #Decode Attribute: total_in_rqst Type:int List: false
        self._total_in_rqst = _decoder.getInt()
        
        #Decode Attribute: total_out_rqst Type:int List: false
        self._total_out_rqst = _decoder.getInt()
        
        #Decode Attribute: total_seen_rqst Type:int List: false
        self._total_seen_rqst = _decoder.getInt()
        
        #Decode Attribute: in_hosts Type:str List: true
        self._in_hosts = MessageAux.getStringList( _decoder )
        #Decode Attribute: out_hosts Type:str List: true
        self._out_hosts = MessageAux.getStringList( _decoder )

    def _blanks( self, _indent ) -> str:
        if _indent == 0:
          return ""
        else:
          return "                                             "[:_indent]

    def toString(self, _indent: int = 0 ) -> str:
        _buffer: StringIO = StringIO()
        
        _buffer.write(self._blanks( _indent ) + "mc_address : " + str( self.mc_address) + "\n")
        _buffer.write(self._blanks( _indent ) + "mc_port : " + str( self.mc_port) + "\n")
        _buffer.write(self._blanks( _indent ) + "total_in_rqst : " + str( self.total_in_rqst) + "\n")
        _buffer.write(self._blanks( _indent ) + "total_out_rqst : " + str( self.total_out_rqst) + "\n")
        _buffer.write(self._blanks( _indent ) + "total_seen_rqst : " + str( self.total_seen_rqst) + "\n")
        _buffer.write(self._blanks( _indent ) + "in_hosts : " + str( self.in_hosts) + "\n")
        _buffer.write(self._blanks( _indent ) + "out_hosts : " + str( self.out_hosts) + "\n")
        return _buffer.getvalue()

    def __str__(self) ->str:
        return self.toString()
    
class NameValuePair( MessageBase ):

    def __init__(self):
        
        self.classModule = "pymc.msg.generated.net_messages"
        self.className = "NameValuePair"
        
        self._name: str
        self._value: str
        self._code: str
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
            self._name = value
        
    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str):
            self._value = value
        
    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, value: str):
            self._code = value
        

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString(self.classModule)
        _encoder.addString(self.className)

        
        # Encode Attribute: name Type: str List: false
        _encoder.addString( self._name )
        # Encode Attribute: value Type: str List: false
        _encoder.addString( self._value )
        # Encode Attribute: code Type: str List: false
        _encoder.addString( self._code )
        return _encoder.buffer


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.classModule = _decoder.getString()
        self.className = _decoder.getString()
        
        #Decode Attribute: name Type:str List: false
        self._name = _decoder.getString()
        
        #Decode Attribute: value Type:str List: false
        self._value = _decoder.getString()
        
        #Decode Attribute: code Type:str List: false
        self._code = _decoder.getString()
        

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

    def __str__(self) ->str:
        return self.toString()
    