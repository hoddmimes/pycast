import socket
from typing import Callable
import threading
import struct
from aux import Aux


class IPMC:
    mSocket: socket.socket
    mPort: int
    mGroupAddr: str
    mInterface: str


    mTTL : int
    mBufferSize : int
    mLocalAddr : str

    mCallback: Callable[ ..., None]
    mErrorCallback: Callable[..., None]

    def __init__(self, interface:str, TTL: int=None, bufferSize: int=None):
        self.mTTL = TTL or 32
        self.mBufferSize = bufferSize or 8192
        self.mLocalAddr = Aux.getIpAddress(interface)
        self.mInterface = interface
        self.mLock = threading.Lock()




    def open(self, address: str, port: int):

        self.mGroupAddr = address
        self.mPort = port

        # Create UDP datagram socket
        self.mSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP )

        #Allow other to connect to the same MCA
        self.mSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


        self.mSocket.bind(('', port))

        # Join MC group
        mreq = struct.pack("=4s4s", socket.inet_aton(self.mGroupAddr), socket.inet_aton(self.mLocalAddr))
        self.mSocket.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, mreq )

        # Enable local loopback
        self.mSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

        # Set TTL
        self.mSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.mTTL)
        self.mSocket.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.mLocalAddr))

    def info(self) -> str:
        return 'grpaddr: '+ self.mGroupAddr + ' port: ' + str(self.mPort) + ' interface: '  + self.mInterface

    def startReader(self, callback, errorCallback ):
        self.mCallback = callback
        self.mErrorCallback = errorCallback
        # Start read thread
        readThread = threading.Thread( target=self.readingThread )
        readThread.start()

    def readingThread(self):
        while True:
            try:
                data, addr = self.mSocket.recvfrom( self.mBufferSize )
                self.mCallback( data, addr )
            except Exception as e:
                self.mErrorCallback(e)
                return

    def send(self, data: bytearray) -> int:
        self.mLock.acquire()
        try:
            bytesSent = self.mSocket.sendto(data, (self.mGroupAddr, self.mPort))
        except Exception as e:
            self.mLock.release()
            raise e

        self.mLock.release()

        return bytesSent

