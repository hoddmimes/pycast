import sys
import threading
import uuid
import logging
import queue
import datetime
import netifaces as ni
from threading import Timer
import socket
import os


class Aux:
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
    def timestamp() -> int:
        _now= datetime.now()
        return  int(_now.timestamp() * 1000)

    @staticmethod
    def timerEvent(callback, args):
        timer = Timer(callback, args)
        timer.start()

    @staticmethod
    def getApplicationId() -> int:
        _ipAddr:str = Aux.getIpAddress('')
        _addr:bytearray = socket.inet_aton( _ipAddr )
        _pid = os.getpid()
        _id = (int(_addr[2]) << 24) + (int(_addr[3]) << 16 ) + (_pid & 0xffff)
        return _id

    @staticmethod
    def timestampStr() -> str:
        _now= datetime.now()
        return _now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    @staticmethod
    def timestampToStr( timestamp: int ) -> str:
        _now= datetime.datetime.fromtimestamp( timestamp)
        return _now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

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
    def getUUID() -> str:
       return uuid.uuid4().hex

class DistributorException( Exception ):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class LogManager(object):
    _instance = None
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance

    @staticmethod
    def setConfiguration(toConsole=True, toFile=True, fileName='Distributor.log',level=logging.DEBUG):
        if not LogManager._instance:
            LogManager._instance = LogManager()
        LogManager._instance.mToConsole = toConsole
        LogManager._instance.mToFile = toFile
        LogManager._instance.mFilename = fileName
        LogManager._instance.mLevel = level

    def getLogger(self, moduleName ) -> logging.Logger:
        _logger = logging.Logger( moduleName )
        if not LogManager._instance.mToConsole and not LogManager._instance.mToFile:
            _logger.addHandler( logging.NullHandler())
            _logger.propagate = False
            return _logger


        logging.basicConfig(level=logging.DEBUG,encoding='utf-8')
        _logger.propagate = False

        _formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        if self.mToFile and self.mFilename and len(self.mFilename) > 0:
            _fh = logging.FileHandler(self.mFilename)
            _fh.setFormatter( _formatter )
            _logger.addHandler( _fh )


        if self.mToConsole:
            _sc = logging.StreamHandler(sys.stdout)
            _sc.setFormatter( _formatter )
            _logger.addHandler( _sc )

        return _logger


class BlockingQueue:

    def __init__(self):
        self._event = threading.Event()
        self._mutex = threading.Lock()
        self._queue = queue.Queue()

    def add(self, item:object):
        self._mutex.acquire()
        self._queue.put(item)
        self._event.set()
        self._mutex.release()

    def isEmpty(self) -> bool:
        return self._queue.empty()

    def take(self) -> object:
         self._mutex.acquire()
         if not self._queue.empty():
            _item = self._queue.get()
            if self._queue.empty():
                self._event.clear()
            self._mutex.release()
            return _item

         self._event.clear()
         self._mutex.release()
         self._event.wait()
         self._mutex.acquire()
         _item = self._queue.get()
         if self._queue.empty():
             self._event.clear()
         self._mutex.release()
         return _item

    def drain(self, max_items=0x7fffffff) ->[]:
        self._mutex.acquire()
        if not self._queue.empty():
            _length = min( self._queue.qsize(), max_items )
            _list = []
            for i in range( _length ):
                _list.append( self._queue.get())
            if self._queue.empty():
                self._event.clear()
            self._mutex.release()
            return _list

        self._event.clear()
        self._mutex.release()
        self._event.wait()

        self._mutex.acquire()
        _length = min( self._queue.qsize(), max_items )
        _list = []
        for i in range( _length ):
            _list.append( self._queue.get())
        if self._queue.empty():
            self._event.clear()
        self._mutex.release()
        return _list

    def clear(self):
        self._mutex.acquire()
        self._queue.clear()
        self._mutex.release()

class PCUUID:
    # The PCUUID is a long 64bit consisting of
    # 1) milliseconds since beginning of month (32 bit)
    # 2) Host nibble (8 bit)
    # 3) Port nibble (7 bit)
    # 4) Sequence number (17 bit)


    def __init__(self):
        self._mutex = threading.RLock()
        self._timestamp:int = self._getStartOfMonthTime(True)
        self._hostNibble:int = self._getHostNibble()
        self._portNibble:int = self._getPortNibble()
        self._seqno:int = 0


    def _getStartOfMonthTime(self, firstTime:bool) -> int:
        self._mutex.acquire()

        if firstTime:
            self._timestamp = 0

        _diff =  self._timestamp


        while self._timestamp == _diff:
            _now = datetime.datetime.now()
            _startOfMonth = _now.replace( day=1, hour=0, minute=0, second=0, microsecond=0 )
            _diff: int = int(_now.timestamp() * 1000) - int(_startOfMonth.timestamp() * 1000)

        self._mutex.release()
        return _diff

    def _getHostNibble(self) ->int:
        self._mutex.acquire()
        _ipAddr:str = Aux.getIpAddress('')
        bytarr = socket.inet_aton( _ipAddr)
        self._mutex.release()
        return int(bytarr[3])

    def _getPortNibble(self) -> int:
        self._mutex.acquire()
        _i = 1
        _offset = 60123
        _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while _i < 127:
            try:
                _sock.bind(('', _offset + _i ))
                _pn = _offset + _i
                self._mutex.release()
                return _pn
            except Exception as e:
                print(e)
                _i += 1

        self._mutex.release()
        raise Exception("Can not allocate port nibble")

    def _incSeqno(self) -> int:
        self._seqno += 1
        if self._seqno >= 0x7f:
            self._timestamp = self._getStartOfMonthTime(False)
            self._seqno = 1
        return self._seqno

    def getNextId(self) -> int:
        self._mutex.acquire()
        _id = self._incSeqno()
        _id += (self._timestamp & 0xffffffff) << 32
        _id += self._hostNibble << 24
        _id += self._portNibble << 17
        self._mutex.release()
        return _id

    def getNextHexId(self) -> str:
        _x = self.getNextId()
        return "{0:x}".format(_x)

    @staticmethod
    def getId() -> int:
        _uuid = PCUUID()
        _uuid.getNextId()


class Link:
    def __init__(self, obj: object):
        self._flink = None
        self._blink = None
        self._object = obj

class ListItr:

    def __init__(self, header: Link):
        self._header = header
        self._curr_item = header
        self._mutex = threading.Lock();

    def has_next(self) -> bool:
        if self._curr_item._flink != self._header:
            return True
        else:
            return False

    def next(self) ->object:
        self._mutex.acquire()
        self._curr_item = self._curr_item._flink
        _item = self._curr_item._object
        self._mutex.release()
        return _item

    def remove(self):
        self._mutex.acquire()
        if self._curr_item == self._header:
            self._mutex.release()
            return None
        else:
            _item = self._curr_item._object
            self._curr_item._blink._flink = self._curr_item._flink
            self._curr_item._flink._blink = self._curr_item._blink
            self._mutex.release()
            return _item
class LinkedList:

    def __init__(self):
        self._header = Link(None)
        self._header._blink = self._header
        self._header._flink = self._header
        self._mutex = threading.Lock()

    # insert item at the tail of the queue
    def add(self, item: object ):
        self._mutex.acquire()
        _itm = Link(item)
        # Set new item links
        _itm._flink = self._header
        _itm._blink = self._header._blink

        self._header._blink._flink = _itm
        self._header._blink = _itm
        self._mutex.release()

    def addhdr(self, item: object ):
        self._mutex.acquire()
        _itm = Link(item)
        # Set new item links
        _itm._flink = self._header._flink
        _itm._blink = self._header

        self._header._flink._blink = _itm
        self._header._flink = _itm

        self._mutex.release()

    def remove(self, item: object ) -> bool:
        self._mutex.acquire()
        _itr = self.iterrator()
        while _itr.has_next():
            _obj = _itr.next()
            if _obj == item:
                _itr.remove()
                self._mutex.release()
                return True
        self._mutex.release()
        return False

