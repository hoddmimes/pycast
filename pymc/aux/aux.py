import uuid
import datetime
import time
import netifaces as ni
from threading import Timer
import socket
import os


class Aux:
    _allocated_server_sockets = []

    @staticmethod
    def ipAddrStrToInt( addr_str: str ) -> int :
        arr = socket.inet_aton( addr_str )
        addr = (int(arr[3]) << 24) + (int(arr[2]) << 16) + (int(arr[1]) << 8) + int(arr[0])
        return addr;

    def ipAddrIntToStr( addr: str ) -> str :
        array = bytearray(4)
        array[0] = (addr & 0xff)
        array[1] = ((addr >> 8) & 0xff)
        array[2] = ((addr >> 16) & 0xff)
        array[3] = ((addr >> 24) & 0xff)
        return "{}.{}.{}.{}".format(array[0],array[1], array[2], array[3])

    @staticmethod
    def currentMilliseconds() -> int:
        _now = datetime.datetime.now()
        return int(_now.timestamp() * 1000)

    @staticmethod
    def currentSeconds() -> int:
        _now = datetime.datetime.now()
        return int(_now.timestamp())

    @staticmethod
    def timerEvent(callback, args):
        timer = Timer(callback, args)
        timer.start()

    @staticmethod
    def sleepMs( time_ms: int ):
        _time_sec:float = float(time_ms) / 1000.0
        _start_time = time.perf_counter()
        while True:
            _elapsed_time = time.perf_counter() - _start_time
            _remaining_time = _time_sec - _elapsed_time
            if _remaining_time <= 0:
                break
            if _remaining_time > 0.02:  # Sleep for 5ms if remaining time is greater
                time.sleep(max(_remaining_time/2, 0.0001))  # Sleep for the remaining time or minimum sleep interval
            else:
                pass

    @staticmethod
    def getApplicationId() -> int:
        _ipAddr:str = Aux.getIpAddress('')
        _addr:bytearray = socket.inet_aton( _ipAddr )
        _pid = os.getpid()
        _id = (int(_addr[2]) << 24) + (int(_addr[3]) << 16 ) + (_pid & 0xffff)
        return _id

    @staticmethod
    def datetime_string( time_stamp=None) -> str:
        if not time_stamp:
            _tim = datetime.datetime.now()
        else:
            if time_stamp == 0:
                return 'N/A'
            _tim = datetime.fromtimestamp( float( time_stamp ) / 1000.0)
        return _tim.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    @staticmethod
    def time_string( time_stamp:int=None) -> str:
        if not time_stamp:
            _tim = datetime.datetime.now()
        else:
            if time_stamp == 0:
                return '00:00:00.000'
            _tim = datetime.fromtimestamp( float( time_stamp ) / 1000.0)
        return _tim.strftime('%H:%M:%S.%f')[:-3]


    @staticmethod
    def allocateServerPortId( portOffset:int ):
        _srv_port = portOffset
        while True:
            _srv_addr = ('127.0.0.1', _srv_port)
            try:
                _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                _socket.bind( _srv_addr )
                Aux._allocated_server_sockets.append( _socket )
                return _srv_port
            except OSError as e:
                if e.errno == 48:
                    _srv_port += 1
                else:
                    raise e

    @staticmethod
    def getIpAddress( eth_interface: str ) -> str:
        if eth_interface is not None and eth_interface != '':
            return ni.ifaddresses( eth_interface )[ni.AF_INET][0]['addr']
        else:
            # Just take first available IP4 address != 127.0.0.1
            _interfaces = ni.interfaces()
            for _iface in _interfaces:
                _ip_info = ni.ifaddresses( _iface )
                if ni.AF_INET in _ip_info:
                    _ip_addr = _ip_info[ni.AF_INET][0]['addr']
                    if _ip_addr != '127.0.0.1':
                        return _ip_addr
            return '127.0.0.1'

    @staticmethod
    def getUUID4() -> str:
       return uuid.uuid4().hex




