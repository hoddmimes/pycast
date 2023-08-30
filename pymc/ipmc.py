import socket
from time import perf_counter
from typing import Callable
import threading
import struct
from pymc.aux.aux import Aux


class IPMC:

    def __init__(self, interface:str = '', TTL: int=None, bufferSize: int=None):
        self._ttl: int = TTL or 32
        self._buffer_size:int = bufferSize or 8192
        self._local_address_string: str = Aux.getIpAddress(interface)
        self._interface: str = interface
        self._mutex: threading.Lock= threading.Lock()

        self._socket: socket.socket
        self._mc_port: int = 0
        self._mc_addr: int = 0
        self._mc_addr_string: str = ''

        self._callback: Callable[ [bytes, str], None] = None
        self._error_callback: Callable[ [Exception], None] = None


    def __str__(self):
        return "mc_addr: {} mc_port: {}".format( self._mc_addr_string, self._mc_port)


    def open(self, address: str, port: int):

        self._mc_addr_string = address
        self._mc_port = port
        self._mc_addr = Aux.ipAddrStrToInt( address )

        # Create UDP datagram socket
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP )

        #Allow other to connect to the same MCA
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self._socket.bind(('', port))

        # Join MC group
        tReq = struct.pack("=4s4s", socket.inet_aton(self._mc_addr_string), socket.inet_aton(self._local_address_string))
        self._socket.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, tReq )

        # Enable local loopback
        self._socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

        # Set TTL
        self._socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self._ttl)
        self._socket.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self._local_address_string))

    @property
    def local_address(self) -> int:
        return Aux.ipAddrStrToInt(self._local_address_string)

    @property
    def mc_address(self) -> int:
        return self._mc_addr
    @property
    def mc_address_string(self) -> str:
        return self._mc_addr_string

    @property
    def mc_port(self):
        return self._mc_port

    def __str__(self) -> str:
        return 'grpaddr: {} port: {} interface: {}'.format(self._mc_addr_string, self._mc_port, self._interface)

    def startReader(self, callback, error_callback ):
        self._callback = callback
        self._error_callback = error_callback
        # Start read thread
        read_thread = threading.Thread( target=self.readingThread )
        read_thread.start()

    def readingThread(self):
        while True:
            try:
                _data, _addr = self._socket.recvfrom( self._buffer_size )
                self._callback( _data, _addr )
            except Exception as e:
                self._error_callback(e)
                return

    def send(self, data: bytearray) -> int:
        with self._mutex:
            _bytes_sent = self._socket.sendto(data, (self._mc_addr_string, self._mc_port))
            if _bytes_sent != len(data):
                raise Exception('incomplete send {} <> {}'.format( _bytes_sent, len(data)))

    def read(self) -> tuple[bytes,tuple[str,int]]:
        _data, _addr = self._socket.recvfrom(self._buffer_size)
        return _data, _addr
