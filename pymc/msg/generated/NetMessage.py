
from pymc.msg.messageif import MessageBase
from pymc.msg.messages import MessageAux
from pymc.msg.decoder import Decoder
from pymc.msg.encoder import Encoder
from io import StringIO
            
class DistNetMsg( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.DistNetMsg"
        
        self.request: int = None
        self.timestamp: int = None
        self.is_request_message: bool = None
        self.message: MessageBase = None
    def set_request(self, value: int):
        self.request = value

    def get_request(self) -> int:
        return self.request
    def set_timestamp(self, value: int):
        self.timestamp = value

    def get_timestamp(self) -> int:
        return self.timestamp
    def set_is_request_message(self, value: bool):
        self.is_request_message = value

    def get_is_request_message(self) -> bool:
        return self.is_request_message
    def set_message(self, value: MessageBase):
        self.message = value

    def get_message(self) -> MessageBase:
        return self.message

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: request Type: long List: false
        _encoder.addLong( self.request )
        # Encode Attribute: timestamp Type: long List: false
        _encoder.addLong( self.timestamp )
        # Encode Attribute: is_request_message Type: bool List: false
        _encoder.addBool( self.is_request_message )
        # Encode Attribute: message Type: MessageBase List: false
        _encoder.addMessage( self.message )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: request Type:long List: false
        self.request = _decoder.getLong()
        
        #Decode Attribute: timestamp Type:long List: false
        self.timestamp = _decoder.getLong()
        
        #Decode Attribute: is_request_message Type:bool List: false
        self.is_request_message = _decoder.getBool()
        
        #Decode Attribute: message Type:MessageBase List: false
        self.message = _decoder.getMessage()
        

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
        self.className = "pymc.msg.generated.DistDomainConnectionEntry"
        
        self.connection_id: int = None
        self.mc_address: str = None
        self.mc_port: int = None
        self.subscriptions: int = None
        self.in_retransmissions: int = None
        self.out_retransmissions: int = None
    def set_connection_id(self, value: int):
        self.connection_id = value

    def get_connection_id(self) -> int:
        return self.connection_id
    def set_mc_address(self, value: str):
        self.mc_address = value

    def get_mc_address(self) -> str:
        return self.mc_address
    def set_mc_port(self, value: int):
        self.mc_port = value

    def get_mc_port(self) -> int:
        return self.mc_port
    def set_subscriptions(self, value: int):
        self.subscriptions = value

    def get_subscriptions(self) -> int:
        return self.subscriptions
    def set_in_retransmissions(self, value: int):
        self.in_retransmissions = value

    def get_in_retransmissions(self) -> int:
        return self.in_retransmissions
    def set_out_retransmissions(self, value: int):
        self.out_retransmissions = value

    def get_out_retransmissions(self) -> int:
        return self.out_retransmissions

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: connection_id Type: long List: false
        _encoder.addLong( self.connection_id )
        # Encode Attribute: mc_address Type: str List: false
        _encoder.addString( self.mc_address )
        # Encode Attribute: mc_port Type: int List: false
        _encoder.addInt( self.mc_port )
        # Encode Attribute: subscriptions Type: int List: false
        _encoder.addInt( self.subscriptions )
        # Encode Attribute: in_retransmissions Type: int List: false
        _encoder.addInt( self.in_retransmissions )
        # Encode Attribute: out_retransmissions Type: int List: false
        _encoder.addInt( self.out_retransmissions )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: connection_id Type:long List: false
        self.connection_id = _decoder.getLong()
        
        #Decode Attribute: mc_address Type:str List: false
        self.mc_address = _decoder.getString()
        
        #Decode Attribute: mc_port Type:int List: false
        self.mc_port = _decoder.getInt()
        
        #Decode Attribute: subscriptions Type:int List: false
        self.subscriptions = _decoder.getInt()
        
        #Decode Attribute: in_retransmissions Type:int List: false
        self.in_retransmissions = _decoder.getInt()
        
        #Decode Attribute: out_retransmissions Type:int List: false
        self.out_retransmissions = _decoder.getInt()
        

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
        self.className = "pymc.msg.generated.DistDomainDistributorEntry"
        
        self.distributor_id: int = None
        self.hostname: str = None
        self.hosta_ddress: str = None
        self.application_name: str = None
        self.application_id: int = None
        self.start_time: str = None
        self.in_retransmissions: int = None
        self.out_retransmissions: int = None
        self.connections: list = None
    def set_distributor_id(self, value: int):
        self.distributor_id = value

    def get_distributor_id(self) -> int:
        return self.distributor_id
    def set_hostname(self, value: str):
        self.hostname = value

    def get_hostname(self) -> str:
        return self.hostname
    def set_hosta_ddress(self, value: str):
        self.hosta_ddress = value

    def get_hosta_ddress(self) -> str:
        return self.hosta_ddress
    def set_application_name(self, value: str):
        self.application_name = value

    def get_application_name(self) -> str:
        return self.application_name
    def set_application_id(self, value: int):
        self.application_id = value

    def get_application_id(self) -> int:
        return self.application_id
    def set_start_time(self, value: str):
        self.start_time = value

    def get_start_time(self) -> str:
        return self.start_time
    def set_in_retransmissions(self, value: int):
        self.in_retransmissions = value

    def get_in_retransmissions(self) -> int:
        return self.in_retransmissions
    def set_out_retransmissions(self, value: int):
        self.out_retransmissions = value

    def get_out_retransmissions(self) -> int:
        return self.out_retransmissions
    def set_connections(self, value: list):
        self.connections = value

    def get_connections(self) -> list:
        return self.connections

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: distributor_id Type: long List: false
        _encoder.addLong( self.distributor_id )
        # Encode Attribute: hostname Type: str List: false
        _encoder.addString( self.hostname )
        # Encode Attribute: hosta_ddress Type: str List: false
        _encoder.addString( self.hosta_ddress )
        # Encode Attribute: application_name Type: str List: false
        _encoder.addString( self.application_name )
        # Encode Attribute: application_id Type: int List: false
        _encoder.addInt( self.application_id )
        # Encode Attribute: start_time Type: str List: false
        _encoder.addString( self.start_time )
        # Encode Attribute: in_retransmissions Type: int List: false
        _encoder.addInt( self.in_retransmissions )
        # Encode Attribute: out_retransmissions Type: int List: false
        _encoder.addInt( self.out_retransmissions )
        # Encode Attribute: connections Type: DistDomainConnectionEntry List: true
        MessageAux.addMessageList( _encoder, self.connections)
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: distributor_id Type:long List: false
        self.distributor_id = _decoder.getLong()
        
        #Decode Attribute: hostname Type:str List: false
        self.hostname = _decoder.getString()
        
        #Decode Attribute: hosta_ddress Type:str List: false
        self.hosta_ddress = _decoder.getString()
        
        #Decode Attribute: application_name Type:str List: false
        self.application_name = _decoder.getString()
        
        #Decode Attribute: application_id Type:int List: false
        self.application_id = _decoder.getInt()
        
        #Decode Attribute: start_time Type:str List: false
        self.start_time = _decoder.getString()
        
        #Decode Attribute: in_retransmissions Type:int List: false
        self.in_retransmissions = _decoder.getInt()
        
        #Decode Attribute: out_retransmissions Type:int List: false
        self.out_retransmissions = _decoder.getInt()
        
        #Decode Attribute: connections Type:DistDomainConnectionEntry List: true
        self.connections = MessageAux.getMessageList( _decoder )

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

    def __str__(self) ->str:
        return self.toString()
    
class DistExploreDomainRsp( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.DistExploreDomainRsp"
        
        self.distributor: DistDomainDistributorEntry = None
    def set_distributor(self, value: DistDomainDistributorEntry):
        self.distributor = value

    def get_distributor(self) -> DistDomainDistributorEntry:
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

    def __str__(self) ->str:
        return self.toString()
    
class DistributorEntry( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.DistributorEntry"
        
        self.host_name: str = None
        self.hosta_address: str = None
        self.application_name: str = None
        self.application_id: int = None
        self.start_time: str = None
        self.connections: int = None
        self.distributor_id: int = None
        self.mem_max: int = None
        self.mem_used: int = None
        self.mem_free: int = None
        self.in_retransmissions: int = None
        self.out_retransmissions: int = None
        self.subscriptions: int = None
    def set_host_name(self, value: str):
        self.host_name = value

    def get_host_name(self) -> str:
        return self.host_name
    def set_hosta_address(self, value: str):
        self.hosta_address = value

    def get_hosta_address(self) -> str:
        return self.hosta_address
    def set_application_name(self, value: str):
        self.application_name = value

    def get_application_name(self) -> str:
        return self.application_name
    def set_application_id(self, value: int):
        self.application_id = value

    def get_application_id(self) -> int:
        return self.application_id
    def set_start_time(self, value: str):
        self.start_time = value

    def get_start_time(self) -> str:
        return self.start_time
    def set_connections(self, value: int):
        self.connections = value

    def get_connections(self) -> int:
        return self.connections
    def set_distributor_id(self, value: int):
        self.distributor_id = value

    def get_distributor_id(self) -> int:
        return self.distributor_id
    def set_mem_max(self, value: int):
        self.mem_max = value

    def get_mem_max(self) -> int:
        return self.mem_max
    def set_mem_used(self, value: int):
        self.mem_used = value

    def get_mem_used(self) -> int:
        return self.mem_used
    def set_mem_free(self, value: int):
        self.mem_free = value

    def get_mem_free(self) -> int:
        return self.mem_free
    def set_in_retransmissions(self, value: int):
        self.in_retransmissions = value

    def get_in_retransmissions(self) -> int:
        return self.in_retransmissions
    def set_out_retransmissions(self, value: int):
        self.out_retransmissions = value

    def get_out_retransmissions(self) -> int:
        return self.out_retransmissions
    def set_subscriptions(self, value: int):
        self.subscriptions = value

    def get_subscriptions(self) -> int:
        return self.subscriptions

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: host_name Type: str List: false
        _encoder.addString( self.host_name )
        # Encode Attribute: hosta_address Type: str List: false
        _encoder.addString( self.hosta_address )
        # Encode Attribute: application_name Type: str List: false
        _encoder.addString( self.application_name )
        # Encode Attribute: application_id Type: int List: false
        _encoder.addInt( self.application_id )
        # Encode Attribute: start_time Type: str List: false
        _encoder.addString( self.start_time )
        # Encode Attribute: connections Type: int List: false
        _encoder.addInt( self.connections )
        # Encode Attribute: distributor_id Type: long List: false
        _encoder.addLong( self.distributor_id )
        # Encode Attribute: mem_max Type: long List: false
        _encoder.addLong( self.mem_max )
        # Encode Attribute: mem_used Type: long List: false
        _encoder.addLong( self.mem_used )
        # Encode Attribute: mem_free Type: long List: false
        _encoder.addLong( self.mem_free )
        # Encode Attribute: in_retransmissions Type: int List: false
        _encoder.addInt( self.in_retransmissions )
        # Encode Attribute: out_retransmissions Type: int List: false
        _encoder.addInt( self.out_retransmissions )
        # Encode Attribute: subscriptions Type: int List: false
        _encoder.addInt( self.subscriptions )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: host_name Type:str List: false
        self.host_name = _decoder.getString()
        
        #Decode Attribute: hosta_address Type:str List: false
        self.hosta_address = _decoder.getString()
        
        #Decode Attribute: application_name Type:str List: false
        self.application_name = _decoder.getString()
        
        #Decode Attribute: application_id Type:int List: false
        self.application_id = _decoder.getInt()
        
        #Decode Attribute: start_time Type:str List: false
        self.start_time = _decoder.getString()
        
        #Decode Attribute: connections Type:int List: false
        self.connections = _decoder.getInt()
        
        #Decode Attribute: distributor_id Type:long List: false
        self.distributor_id = _decoder.getLong()
        
        #Decode Attribute: mem_max Type:long List: false
        self.mem_max = _decoder.getLong()
        
        #Decode Attribute: mem_used Type:long List: false
        self.mem_used = _decoder.getLong()
        
        #Decode Attribute: mem_free Type:long List: false
        self.mem_free = _decoder.getLong()
        
        #Decode Attribute: in_retransmissions Type:int List: false
        self.in_retransmissions = _decoder.getInt()
        
        #Decode Attribute: out_retransmissions Type:int List: false
        self.out_retransmissions = _decoder.getInt()
        
        #Decode Attribute: subscriptions Type:int List: false
        self.subscriptions = _decoder.getInt()
        

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
        self.className = "pymc.msg.generated.DistExploreDistributorRqst"
        
        self.distributor_id: int = None
    def set_distributor_id(self, value: int):
        self.distributor_id = value

    def get_distributor_id(self) -> int:
        return self.distributor_id

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: distributor_id Type: long List: false
        _encoder.addLong( self.distributor_id )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: distributor_id Type:long List: false
        self.distributor_id = _decoder.getLong()
        

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
        self.className = "pymc.msg.generated.DistExploreDistributorRsp"
        
        self.distributor: DistributorEntry = None
    def set_distributor(self, value: DistributorEntry):
        self.distributor = value

    def get_distributor(self) -> DistributorEntry:
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

    def __str__(self) ->str:
        return self.toString()
    
class DataRateItem( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.DataRateItem"
        
        self.total: int = None
        self.curr_value: int = None
        self.peak_value: int = None
        self.peak_time: str = None
    def set_total(self, value: int):
        self.total = value

    def get_total(self) -> int:
        return self.total
    def set_curr_value(self, value: int):
        self.curr_value = value

    def get_curr_value(self) -> int:
        return self.curr_value
    def set_peak_value(self, value: int):
        self.peak_value = value

    def get_peak_value(self) -> int:
        return self.peak_value
    def set_peak_time(self, value: str):
        self.peak_time = value

    def get_peak_time(self) -> str:
        return self.peak_time

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: total Type: long List: false
        _encoder.addLong( self.total )
        # Encode Attribute: curr_value Type: int List: false
        _encoder.addInt( self.curr_value )
        # Encode Attribute: peak_value Type: int List: false
        _encoder.addInt( self.peak_value )
        # Encode Attribute: peak_time Type: str List: false
        _encoder.addString( self.peak_time )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: total Type:long List: false
        self.total = _decoder.getLong()
        
        #Decode Attribute: curr_value Type:int List: false
        self.curr_value = _decoder.getInt()
        
        #Decode Attribute: peak_value Type:int List: false
        self.peak_value = _decoder.getInt()
        
        #Decode Attribute: peak_time Type:str List: false
        self.peak_time = _decoder.getString()
        

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
        self.className = "pymc.msg.generated.QueueSizeItem"
        
        self.size: int = None
        self.peak_size: int = None
        self.peak_time: str = None
    def set_size(self, value: int):
        self.size = value

    def get_size(self) -> int:
        return self.size
    def set_peak_size(self, value: int):
        self.peak_size = value

    def get_peak_size(self) -> int:
        return self.peak_size
    def set_peak_time(self, value: str):
        self.peak_time = value

    def get_peak_time(self) -> str:
        return self.peak_time

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: size Type: long List: false
        _encoder.addLong( self.size )
        # Encode Attribute: peak_size Type: int List: false
        _encoder.addInt( self.peak_size )
        # Encode Attribute: peak_time Type: str List: false
        _encoder.addString( self.peak_time )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: size Type:long List: false
        self.size = _decoder.getLong()
        
        #Decode Attribute: peak_size Type:int List: false
        self.peak_size = _decoder.getInt()
        
        #Decode Attribute: peak_time Type:str List: false
        self.peak_time = _decoder.getString()
        

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
        self.className = "pymc.msg.generated.ConnectionEntry"
        
        self.mc_address: str = None
        self.mc_port: int = None
        self.connection_id: int = None
        self.publishers: int = None
        self.subscribers: int = None
        self.subscriptions: int = None
        self.in_retransmissions: int = None
        self.out_retransmissions: int = None
        self.deliver_update_queue: QueueSizeItem = None
        self.xta_total_bytes: int = None
        self.xta_total_segments: int = None
        self.xta_total_updates: int = None
        self.xta_bytes: DataRateItem = None
        self.xtaSegments: DataRateItem = None
        self.xta_updates: DataRateItem = None
        self.xta_bytes_1min: DataRateItem = None
        self.xta_segments_1min: DataRateItem = None
        self.xta_updates_1min: DataRateItem = None
        self.xta_bytes_5min: DataRateItem = None
        self.xta_segments_5min: DataRateItem = None
        self.xta_updates_5min: DataRateItem = None
        self.rcv_total_bytes: int = None
        self.rcv_total_segments: int = None
        self.rcv_total_updates: int = None
        self.rcv_bytes: DataRateItem = None
        self.rcv_segments: DataRateItem = None
        self.rcv_updates: DataRateItem = None
        self.rcv_bytes_1min: DataRateItem = None
        self.rcv_segments_1min: DataRateItem = None
        self.rcv_updates_1min: DataRateItem = None
        self.rcv_bytes_5min: DataRateItem = None
        self.rcv_segments_5min: DataRateItem = None
        self.rcv_updates_5min: DataRateItem = None
    def set_mc_address(self, value: str):
        self.mc_address = value

    def get_mc_address(self) -> str:
        return self.mc_address
    def set_mc_port(self, value: int):
        self.mc_port = value

    def get_mc_port(self) -> int:
        return self.mc_port
    def set_connection_id(self, value: int):
        self.connection_id = value

    def get_connection_id(self) -> int:
        return self.connection_id
    def set_publishers(self, value: int):
        self.publishers = value

    def get_publishers(self) -> int:
        return self.publishers
    def set_subscribers(self, value: int):
        self.subscribers = value

    def get_subscribers(self) -> int:
        return self.subscribers
    def set_subscriptions(self, value: int):
        self.subscriptions = value

    def get_subscriptions(self) -> int:
        return self.subscriptions
    def set_in_retransmissions(self, value: int):
        self.in_retransmissions = value

    def get_in_retransmissions(self) -> int:
        return self.in_retransmissions
    def set_out_retransmissions(self, value: int):
        self.out_retransmissions = value

    def get_out_retransmissions(self) -> int:
        return self.out_retransmissions
    def set_deliver_update_queue(self, value: QueueSizeItem):
        self.deliver_update_queue = value

    def get_deliver_update_queue(self) -> QueueSizeItem:
        return self.deliver_update_queue
    def set_xta_total_bytes(self, value: int):
        self.xta_total_bytes = value

    def get_xta_total_bytes(self) -> int:
        return self.xta_total_bytes
    def set_xta_total_segments(self, value: int):
        self.xta_total_segments = value

    def get_xta_total_segments(self) -> int:
        return self.xta_total_segments
    def set_xta_total_updates(self, value: int):
        self.xta_total_updates = value

    def get_xta_total_updates(self) -> int:
        return self.xta_total_updates
    def set_xta_bytes(self, value: DataRateItem):
        self.xta_bytes = value

    def get_xta_bytes(self) -> DataRateItem:
        return self.xta_bytes
    def set_xtaSegments(self, value: DataRateItem):
        self.xtaSegments = value

    def get_xtaSegments(self) -> DataRateItem:
        return self.xtaSegments
    def set_xta_updates(self, value: DataRateItem):
        self.xta_updates = value

    def get_xta_updates(self) -> DataRateItem:
        return self.xta_updates
    def set_xta_bytes_1min(self, value: DataRateItem):
        self.xta_bytes_1min = value

    def get_xta_bytes_1min(self) -> DataRateItem:
        return self.xta_bytes_1min
    def set_xta_segments_1min(self, value: DataRateItem):
        self.xta_segments_1min = value

    def get_xta_segments_1min(self) -> DataRateItem:
        return self.xta_segments_1min
    def set_xta_updates_1min(self, value: DataRateItem):
        self.xta_updates_1min = value

    def get_xta_updates_1min(self) -> DataRateItem:
        return self.xta_updates_1min
    def set_xta_bytes_5min(self, value: DataRateItem):
        self.xta_bytes_5min = value

    def get_xta_bytes_5min(self) -> DataRateItem:
        return self.xta_bytes_5min
    def set_xta_segments_5min(self, value: DataRateItem):
        self.xta_segments_5min = value

    def get_xta_segments_5min(self) -> DataRateItem:
        return self.xta_segments_5min
    def set_xta_updates_5min(self, value: DataRateItem):
        self.xta_updates_5min = value

    def get_xta_updates_5min(self) -> DataRateItem:
        return self.xta_updates_5min
    def set_rcv_total_bytes(self, value: int):
        self.rcv_total_bytes = value

    def get_rcv_total_bytes(self) -> int:
        return self.rcv_total_bytes
    def set_rcv_total_segments(self, value: int):
        self.rcv_total_segments = value

    def get_rcv_total_segments(self) -> int:
        return self.rcv_total_segments
    def set_rcv_total_updates(self, value: int):
        self.rcv_total_updates = value

    def get_rcv_total_updates(self) -> int:
        return self.rcv_total_updates
    def set_rcv_bytes(self, value: DataRateItem):
        self.rcv_bytes = value

    def get_rcv_bytes(self) -> DataRateItem:
        return self.rcv_bytes
    def set_rcv_segments(self, value: DataRateItem):
        self.rcv_segments = value

    def get_rcv_segments(self) -> DataRateItem:
        return self.rcv_segments
    def set_rcv_updates(self, value: DataRateItem):
        self.rcv_updates = value

    def get_rcv_updates(self) -> DataRateItem:
        return self.rcv_updates
    def set_rcv_bytes_1min(self, value: DataRateItem):
        self.rcv_bytes_1min = value

    def get_rcv_bytes_1min(self) -> DataRateItem:
        return self.rcv_bytes_1min
    def set_rcv_segments_1min(self, value: DataRateItem):
        self.rcv_segments_1min = value

    def get_rcv_segments_1min(self) -> DataRateItem:
        return self.rcv_segments_1min
    def set_rcv_updates_1min(self, value: DataRateItem):
        self.rcv_updates_1min = value

    def get_rcv_updates_1min(self) -> DataRateItem:
        return self.rcv_updates_1min
    def set_rcv_bytes_5min(self, value: DataRateItem):
        self.rcv_bytes_5min = value

    def get_rcv_bytes_5min(self) -> DataRateItem:
        return self.rcv_bytes_5min
    def set_rcv_segments_5min(self, value: DataRateItem):
        self.rcv_segments_5min = value

    def get_rcv_segments_5min(self) -> DataRateItem:
        return self.rcv_segments_5min
    def set_rcv_updates_5min(self, value: DataRateItem):
        self.rcv_updates_5min = value

    def get_rcv_updates_5min(self) -> DataRateItem:
        return self.rcv_updates_5min

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: mc_address Type: str List: false
        _encoder.addString( self.mc_address )
        # Encode Attribute: mc_port Type: int List: false
        _encoder.addInt( self.mc_port )
        # Encode Attribute: connection_id Type: long List: false
        _encoder.addLong( self.connection_id )
        # Encode Attribute: publishers Type: int List: false
        _encoder.addInt( self.publishers )
        # Encode Attribute: subscribers Type: int List: false
        _encoder.addInt( self.subscribers )
        # Encode Attribute: subscriptions Type: int List: false
        _encoder.addInt( self.subscriptions )
        # Encode Attribute: in_retransmissions Type: int List: false
        _encoder.addInt( self.in_retransmissions )
        # Encode Attribute: out_retransmissions Type: int List: false
        _encoder.addInt( self.out_retransmissions )
        # Encode Attribute: deliver_update_queue Type: QueueSizeItem List: false
        _encoder.addMessage( self.deliver_update_queue )
        # Encode Attribute: xta_total_bytes Type: long List: false
        _encoder.addLong( self.xta_total_bytes )
        # Encode Attribute: xta_total_segments Type: long List: false
        _encoder.addLong( self.xta_total_segments )
        # Encode Attribute: xta_total_updates Type: long List: false
        _encoder.addLong( self.xta_total_updates )
        # Encode Attribute: xta_bytes Type: DataRateItem List: false
        _encoder.addMessage( self.xta_bytes )
        # Encode Attribute: xtaSegments Type: DataRateItem List: false
        _encoder.addMessage( self.xtaSegments )
        # Encode Attribute: xta_updates Type: DataRateItem List: false
        _encoder.addMessage( self.xta_updates )
        # Encode Attribute: xta_bytes_1min Type: DataRateItem List: false
        _encoder.addMessage( self.xta_bytes_1min )
        # Encode Attribute: xta_segments_1min Type: DataRateItem List: false
        _encoder.addMessage( self.xta_segments_1min )
        # Encode Attribute: xta_updates_1min Type: DataRateItem List: false
        _encoder.addMessage( self.xta_updates_1min )
        # Encode Attribute: xta_bytes_5min Type: DataRateItem List: false
        _encoder.addMessage( self.xta_bytes_5min )
        # Encode Attribute: xta_segments_5min Type: DataRateItem List: false
        _encoder.addMessage( self.xta_segments_5min )
        # Encode Attribute: xta_updates_5min Type: DataRateItem List: false
        _encoder.addMessage( self.xta_updates_5min )
        # Encode Attribute: rcv_total_bytes Type: long List: false
        _encoder.addLong( self.rcv_total_bytes )
        # Encode Attribute: rcv_total_segments Type: long List: false
        _encoder.addLong( self.rcv_total_segments )
        # Encode Attribute: rcv_total_updates Type: long List: false
        _encoder.addLong( self.rcv_total_updates )
        # Encode Attribute: rcv_bytes Type: DataRateItem List: false
        _encoder.addMessage( self.rcv_bytes )
        # Encode Attribute: rcv_segments Type: DataRateItem List: false
        _encoder.addMessage( self.rcv_segments )
        # Encode Attribute: rcv_updates Type: DataRateItem List: false
        _encoder.addMessage( self.rcv_updates )
        # Encode Attribute: rcv_bytes_1min Type: DataRateItem List: false
        _encoder.addMessage( self.rcv_bytes_1min )
        # Encode Attribute: rcv_segments_1min Type: DataRateItem List: false
        _encoder.addMessage( self.rcv_segments_1min )
        # Encode Attribute: rcv_updates_1min Type: DataRateItem List: false
        _encoder.addMessage( self.rcv_updates_1min )
        # Encode Attribute: rcv_bytes_5min Type: DataRateItem List: false
        _encoder.addMessage( self.rcv_bytes_5min )
        # Encode Attribute: rcv_segments_5min Type: DataRateItem List: false
        _encoder.addMessage( self.rcv_segments_5min )
        # Encode Attribute: rcv_updates_5min Type: DataRateItem List: false
        _encoder.addMessage( self.rcv_updates_5min )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: mc_address Type:str List: false
        self.mc_address = _decoder.getString()
        
        #Decode Attribute: mc_port Type:int List: false
        self.mc_port = _decoder.getInt()
        
        #Decode Attribute: connection_id Type:long List: false
        self.connection_id = _decoder.getLong()
        
        #Decode Attribute: publishers Type:int List: false
        self.publishers = _decoder.getInt()
        
        #Decode Attribute: subscribers Type:int List: false
        self.subscribers = _decoder.getInt()
        
        #Decode Attribute: subscriptions Type:int List: false
        self.subscriptions = _decoder.getInt()
        
        #Decode Attribute: in_retransmissions Type:int List: false
        self.in_retransmissions = _decoder.getInt()
        
        #Decode Attribute: out_retransmissions Type:int List: false
        self.out_retransmissions = _decoder.getInt()
        
        #Decode Attribute: deliver_update_queue Type:QueueSizeItem List: false
        self.deliver_update_queue = _decoder.getMessage()
        
        #Decode Attribute: xta_total_bytes Type:long List: false
        self.xta_total_bytes = _decoder.getLong()
        
        #Decode Attribute: xta_total_segments Type:long List: false
        self.xta_total_segments = _decoder.getLong()
        
        #Decode Attribute: xta_total_updates Type:long List: false
        self.xta_total_updates = _decoder.getLong()
        
        #Decode Attribute: xta_bytes Type:DataRateItem List: false
        self.xta_bytes = _decoder.getMessage()
        
        #Decode Attribute: xtaSegments Type:DataRateItem List: false
        self.xtaSegments = _decoder.getMessage()
        
        #Decode Attribute: xta_updates Type:DataRateItem List: false
        self.xta_updates = _decoder.getMessage()
        
        #Decode Attribute: xta_bytes_1min Type:DataRateItem List: false
        self.xta_bytes_1min = _decoder.getMessage()
        
        #Decode Attribute: xta_segments_1min Type:DataRateItem List: false
        self.xta_segments_1min = _decoder.getMessage()
        
        #Decode Attribute: xta_updates_1min Type:DataRateItem List: false
        self.xta_updates_1min = _decoder.getMessage()
        
        #Decode Attribute: xta_bytes_5min Type:DataRateItem List: false
        self.xta_bytes_5min = _decoder.getMessage()
        
        #Decode Attribute: xta_segments_5min Type:DataRateItem List: false
        self.xta_segments_5min = _decoder.getMessage()
        
        #Decode Attribute: xta_updates_5min Type:DataRateItem List: false
        self.xta_updates_5min = _decoder.getMessage()
        
        #Decode Attribute: rcv_total_bytes Type:long List: false
        self.rcv_total_bytes = _decoder.getLong()
        
        #Decode Attribute: rcv_total_segments Type:long List: false
        self.rcv_total_segments = _decoder.getLong()
        
        #Decode Attribute: rcv_total_updates Type:long List: false
        self.rcv_total_updates = _decoder.getLong()
        
        #Decode Attribute: rcv_bytes Type:DataRateItem List: false
        self.rcv_bytes = _decoder.getMessage()
        
        #Decode Attribute: rcv_segments Type:DataRateItem List: false
        self.rcv_segments = _decoder.getMessage()
        
        #Decode Attribute: rcv_updates Type:DataRateItem List: false
        self.rcv_updates = _decoder.getMessage()
        
        #Decode Attribute: rcv_bytes_1min Type:DataRateItem List: false
        self.rcv_bytes_1min = _decoder.getMessage()
        
        #Decode Attribute: rcv_segments_1min Type:DataRateItem List: false
        self.rcv_segments_1min = _decoder.getMessage()
        
        #Decode Attribute: rcv_updates_1min Type:DataRateItem List: false
        self.rcv_updates_1min = _decoder.getMessage()
        
        #Decode Attribute: rcv_bytes_5min Type:DataRateItem List: false
        self.rcv_bytes_5min = _decoder.getMessage()
        
        #Decode Attribute: rcv_segments_5min Type:DataRateItem List: false
        self.rcv_segments_5min = _decoder.getMessage()
        
        #Decode Attribute: rcv_updates_5min Type:DataRateItem List: false
        self.rcv_updates_5min = _decoder.getMessage()
        

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
        self.className = "pymc.msg.generated.DistExploreConnectionRqst"
        
        self.distributor_id: int = None
        self.connection_id: int = None
    def set_distributor_id(self, value: int):
        self.distributor_id = value

    def get_distributor_id(self) -> int:
        return self.distributor_id
    def set_connection_id(self, value: int):
        self.connection_id = value

    def get_connection_id(self) -> int:
        return self.connection_id

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: distributor_id Type: long List: false
        _encoder.addLong( self.distributor_id )
        # Encode Attribute: connection_id Type: long List: false
        _encoder.addLong( self.connection_id )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: distributor_id Type:long List: false
        self.distributor_id = _decoder.getLong()
        
        #Decode Attribute: connection_id Type:long List: false
        self.connection_id = _decoder.getLong()
        

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
        self.className = "pymc.msg.generated.DistExploreConnectionRsp"
        
        self.connection: ConnectionEntry = None
    def set_connection(self, value: ConnectionEntry):
        self.connection = value

    def get_connection(self) -> ConnectionEntry:
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

    def __str__(self) ->str:
        return self.toString()
    
class DistExploreSubscriptionsRqst( MessageBase ):

    def __init__(self):
        self.className = "pymc.msg.generated.DistExploreSubscriptionsRqst"
        
        self.distributor_id: int = None
        self.connection_id: int = None
    def set_distributor_id(self, value: int):
        self.distributor_id = value

    def get_distributor_id(self) -> int:
        return self.distributor_id
    def set_connection_id(self, value: int):
        self.connection_id = value

    def get_connection_id(self) -> int:
        return self.connection_id

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: distributor_id Type: long List: false
        _encoder.addLong( self.distributor_id )
        # Encode Attribute: connection_id Type: long List: false
        _encoder.addLong( self.connection_id )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: distributor_id Type:long List: false
        self.distributor_id = _decoder.getLong()
        
        #Decode Attribute: connection_id Type:long List: false
        self.connection_id = _decoder.getLong()
        

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
        self.className = "pymc.msg.generated.DistExploreSubscriptionsRsp"
        
        self.mc_address: str = None
        self.mc_port: int = None
        self.subscriptions: list = None
    def set_mc_address(self, value: str):
        self.mc_address = value

    def get_mc_address(self) -> str:
        return self.mc_address
    def set_mc_port(self, value: int):
        self.mc_port = value

    def get_mc_port(self) -> int:
        return self.mc_port
    def set_subscriptions( self, value: list ):
        self.subscriptions = value

    def get_subscriptions(self) -> list:
        return self.subscriptions

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: mc_address Type: str List: false
        _encoder.addString( self.mc_address )
        # Encode Attribute: mc_port Type: int List: false
        _encoder.addInt( self.mc_port )
        # Encode Attribute: subscriptions Type: str List: true
            # Encode str list
        MessageAux.addStringList( _encoder, self.subscriptions  )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: mc_address Type:str List: false
        self.mc_address = _decoder.getString()
        
        #Decode Attribute: mc_port Type:int List: false
        self.mc_port = _decoder.getInt()
        
        #Decode Attribute: subscriptions Type:str List: true
        self.subscriptions = MessageAux.getStringList( _decoder )

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
        self.className = "pymc.msg.generated.DistExploreRetransmissionsRqst"
        
        self.distributor_id: int = None
        self.connection_id: int = None
    def set_distributor_id(self, value: int):
        self.distributor_id = value

    def get_distributor_id(self) -> int:
        return self.distributor_id
    def set_connection_id(self, value: int):
        self.connection_id = value

    def get_connection_id(self) -> int:
        return self.connection_id

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: distributor_id Type: long List: false
        _encoder.addLong( self.distributor_id )
        # Encode Attribute: connection_id Type: long List: false
        _encoder.addLong( self.connection_id )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: distributor_id Type:long List: false
        self.distributor_id = _decoder.getLong()
        
        #Decode Attribute: connection_id Type:long List: false
        self.connection_id = _decoder.getLong()
        

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
        self.className = "pymc.msg.generated.DistExploreRetransmissonsRsp"
        
        self.mc_address: str = None
        self.mc_port: int = None
        self.total_in_rqst: int = None
        self.total_out_rqst: int = None
        self.total_seen_rqst: int = None
        self.in_hosts: list = None
        self.out_hosts: list = None
    def set_mc_address(self, value: str):
        self.mc_address = value

    def get_mc_address(self) -> str:
        return self.mc_address
    def set_mc_port(self, value: int):
        self.mc_port = value

    def get_mc_port(self) -> int:
        return self.mc_port
    def set_total_in_rqst(self, value: int):
        self.total_in_rqst = value

    def get_total_in_rqst(self) -> int:
        return self.total_in_rqst
    def set_total_out_rqst(self, value: int):
        self.total_out_rqst = value

    def get_total_out_rqst(self) -> int:
        return self.total_out_rqst
    def set_total_seen_rqst(self, value: int):
        self.total_seen_rqst = value

    def get_total_seen_rqst(self) -> int:
        return self.total_seen_rqst
    def set_in_hosts( self, value: list  ):
        self.in_hosts = value

    def get_in_hosts(self) -> list:
        return self.in_hosts
    def set_out_hosts( self, value: list ):
        self.out_hosts = value

    def get_out_hosts(self) -> list:
        return self.out_hosts

    def toBytes(self) -> bytearray:
       return self.encode()

        
    def encode(self) -> bytearray:
        _encoder = Encoder()
        _encoder.addString( self.className )

        
        # Encode Attribute: mc_address Type: str List: false
        _encoder.addString( self.mc_address )
        # Encode Attribute: mc_port Type: int List: false
        _encoder.addInt( self.mc_port )
        # Encode Attribute: total_in_rqst Type: int List: false
        _encoder.addInt( self.total_in_rqst )
        # Encode Attribute: total_out_rqst Type: int List: false
        _encoder.addInt( self.total_out_rqst )
        # Encode Attribute: total_seen_rqst Type: int List: false
        _encoder.addInt( self.total_seen_rqst )
        # Encode Attribute: in_hosts Type: str List: true
            # Encode str list
        MessageAux.addStringList( _encoder, self.in_hosts  )
        # Encode Attribute: out_hosts Type: str List: true
            # Encode str list
        MessageAux.addStringList( _encoder, self.out_hosts  )
        return _encoder.get_bytes()


        
    def decode( self, buffer: bytearray):
        _decoder = Decoder( buffer )
        self.className = _decoder.getString()
        
        #Decode Attribute: mc_address Type:str List: false
        self.mc_address = _decoder.getString()
        
        #Decode Attribute: mc_port Type:int List: false
        self.mc_port = _decoder.getInt()
        
        #Decode Attribute: total_in_rqst Type:int List: false
        self.total_in_rqst = _decoder.getInt()
        
        #Decode Attribute: total_out_rqst Type:int List: false
        self.total_out_rqst = _decoder.getInt()
        
        #Decode Attribute: total_seen_rqst Type:int List: false
        self.total_seen_rqst = _decoder.getInt()
        
        #Decode Attribute: in_hosts Type:str List: true
        self.in_hosts = MessageAux.getStringList( _decoder )
        #Decode Attribute: out_hosts Type:str List: true
        self.out_hosts = MessageAux.getStringList( _decoder )

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
        self.className = "pymc.msg.generated.NameValuePair"
        
        self.name: str = None
        self.value: str = None
        self.code: str = None
    def set_name(self, value: str):
        self.name = value

    def get_name(self) -> str:
        return self.name
    def set_value(self, value: str):
        self.value = value

    def get_value(self) -> str:
        return self.value
    def set_code(self, value: str):
        self.code = value

    def get_code(self) -> str:
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

    def __str__(self) ->str:
        return self.toString()
    