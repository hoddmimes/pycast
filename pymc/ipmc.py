import socket
from time import perf_counter
from typing import Callable
import threading
import struct
from pymc.aux.aux import Aux


class IPMC:

    def __init__(self, interface:str = '', TTL: int=None, bufferSize: int=None):
        self.mTTL:int = TTL or 32
        self.mBufferSize:int = bufferSize or 8192
        self.mLocalAddrStr:str = Aux.getIpAddress(interface)
        self.mInterface:str = interface
        self.mLock:threading.Lock= threading.Lock()

        self.mSocket: socket.socket = None
        self.mMcPort: int = None
        self.mMcAddr: int = None
        self.mMcAddrStr: str = None

        self.mCallback: Callable[ [bytearray,str], None] = None
        self.mErrorCallback: Callable[ [Exception], None] = None


    def __str__(self):
        return "mc_addr: {} mc_port: {}".format( self.mMcAddrStr, self.mMcPort)


    def open(self, address: str, port: int):

        self.mMcAddrStr = address
        self.mMcPort = port
        self.mMcAddr = Aux.ipAddrStrToInt( address )

        # Create UDP datagram socket
        self.mSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP )

        #Allow other to connect to the same MCA
        self.mSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.mSocket.bind(('', port))

        # Join MC group
        tReq = struct.pack("=4s4s", socket.inet_aton(self.mMcAddrStr), socket.inet_aton(self.mLocalAddrStr))
        self.mSocket.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, tReq )

        # Enable local loopback
        self.mSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

        # Set TTL
        self.mSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.mTTL)
        self.mSocket.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.mLocalAddrStr))

    def __str__(self) -> str:
        return 'grpaddr: {} port: {} interface: {}'.format(self.mGroupAddr, self.mPort, self.mInterface)

    def startReader(self, callback, errorCallback ):
        self.mCallback = callback
        self.mErrorCallback = errorCallback
        # Start read thread
        readThread = threading.Thread( target=self.readingThread )
        readThread.start()

    def readingThread(self):
        while True:
            try:
                tData, tAddr = self.mSocket.recvfrom( self.mBufferSize )
                self.mCallback( tData, tAddr )
            except Exception as e:
                self.mErrorCallback(e)
                return

    def send(self, data: bytearray) -> int:
        with self.mLock:
            _start = perf_counter()
            _bytes_sent = self.mSocket.sendto(data, (self.mMcAddrStr, self.mMcPort))
            if _bytes_sent != len(data):
                raise Exception('incomplete send {} <> {}'.format( _bytes_sent, len(data)))
            _sndtim_usec = int((perf_counter() - _start) * 1000000)
            return _sndtim_usec

    def read(self) -> tuple[bytearray,tuple[str,int]]:
        tData, tAddr = self.mSocket.recvfrom(self.mBufferSize)
        return tData, tAddr