import uuid
import datetime
import threading
import ctypes
import time
import netifaces as ni
from threading import Timer
import socket
import os
from pymc.aux.distributor_exception import  DistributorTheadExitException

class Aux:
    _allocated_server_sockets = []

    @staticmethod
    def swap_int(value: int):
        if value <= 0xffff:
            return ((value & 0xff)  << 8) + ((value >> 8) & 0xff)
        elif value <= 0xffffffff:
            return ((value & 0xff)  << 24) + ((value >> 8 & 0xff)  << 16) + ((value >> 16 & 0xff)  << 8) + (value >> 24 & 0xff)
        else:
            return (((value & 0xff) << 56) + ((value >> 8 & 0xff) << 48) + ((value >> 16 & 0xff) << 40) + ((value >> 24 & 0xff) << 32)
                    + ((value >> 32 & 0xff) << 24) + ((value >> 40 & 0xff) << 16) + ((value >> 48 & 0xff) << 8) + (value >> 56))



    @staticmethod
    def ip_addr_str_to_int(addr_str: str) -> int :
        arr = socket.inet_aton( addr_str )
        addr = (int(arr[3]) << 24) + (int(arr[2]) << 16) + (int(arr[1]) << 8) + int(arr[0])
        return addr

    @staticmethod
    def ip_addr_int_to_str(addr: int) -> str :
        array = bytearray(4)
        array[0] = (addr & 0xff)
        array[1] = ((addr >> 8) & 0xff)
        array[2] = ((addr >> 16) & 0xff)
        array[3] = ((addr >> 24) & 0xff)
        return "{}.{}.{}.{}".format(array[0],array[1], array[2], array[3])

    @staticmethod
    def current_milliseconds() -> int:
        _now = datetime.datetime.now()
        return int(_now.timestamp() * 1000)

    @staticmethod
    def current_seconds() -> int:
        _now: int = int(time.time())
        return _now

    @staticmethod
    def timerEvent(callback, args):
        timer = Timer(callback, args)
        timer.start()

    @staticmethod
    def hash32(string: str) -> int:
        _hash: int = 1717
        for x in string.encode():
            _hash = (37 * _hash) + x
            # _hash = ((_hash << 5) + _hash) + x
            _hash = _hash * 3737;
        return _hash & 0xffffffff


    @staticmethod
    def sleep_ms(time_ms: int):
        _time_sec:float = float(time_ms) / 1000.0
        _start_time = time.perf_counter()
        while True:
            _elapsed_time = time.perf_counter() - _start_time
            _remaining_time = _time_sec - _elapsed_time
            if _remaining_time <= 0:
                break
            elif _remaining_time >= 0.02:  # 20 ms
                time.sleep(_remaining_time / 1.42)  # Sleep for the remaining time or minimum sleep interval
            elif _remaining_time > 0.01:  # 20
                time.sleep(max(_remaining_time/2, 0.0001))  # Sleep for the remaining time or minimum sleep interval
            else:
                pass

    @staticmethod
    def get_application_id() -> int:
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
            _tim = datetime.datetime.fromtimestamp( float( time_stamp ) / 1000.0)
        return _tim.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    @staticmethod
    def time_string( time_stamp:int=None) -> str:
        if not time_stamp:
            _tim = datetime.datetime.now()
        else:
            if time_stamp == 0:
                return '00:00:00.000'
            if time_stamp <= 0x7fffffff:
                _tim = datetime.datetime.fromtimestamp(int(time_stamp))
            else:
                _tim = datetime.datetime.fromtimestamp( float( time_stamp ) / 1000.0)
        return _tim.strftime('%H:%M:%S.%f')[:-3]


    @staticmethod
    def allocate_server_port_id(portOffset:int):
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
    def get_uuid4() -> str:
       return uuid.uuid4().hex


class AuxThread(threading.Thread):

    def __int__(self):
        self._time_to_exit = False

    @property
    def thread_id(self):
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    @property
    def is_stopped(self) -> bool:
        return self._time_to_exit

    def stop(self):
        self._time_to_exit = True
        _id = self.thread_id
        _sts = res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(_id), ctypes.py_object(DistributorTheadExitException))
        #print("id: {} status: {}".format( _id,  _sts ))

    def set_name(self, name: str):
        super().name = name
