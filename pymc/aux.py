import sys
import threading
import uuid
import logging
import queue
import datetime
import netifaces as ni
from threading import Timer

class Aux:
    @staticmethod
    def timestamp() -> int:
        _now= datetime.now()
        return  int(_now.timestamp() * 1000)

    @staticmethod
    def timerEvent(callback, args):
        timer = Timer(callback, args)
        timer.start()


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

    @staticmethod
    def getUUID() -> str:
       return uuid.uuid4().hex

class PCLogger:

    def __init__(self, module:str, level=logging.INFO, levelFile=None, fileName:str=None, logFlags:int=0xffffffff):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(module)
        self.toConsole = True
        self.toFile = True
        self.logFlags = logFlags

        _formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        if fileName:
            self._fh = logging.FileHandler(fileName)
            self._fh.setFormatter( _formatter )
            self.logger.addHandler( self._fh )
            if levelFile:
                self._fh.setLevel( levelFile )
            else:
                self._fh.setLevel( level )
            self._fh.setLevel(level)

        self._sc = logging.StreamHandler(sys.stdout)
        self._sc.setFormatter( _formatter )
        self._sc.setLevel(level)
        self.logger.addHandler( self._sc )
        self.logger.propagate = False

    def isLogFlagSet(self, mask: int ) -> bool:
        if ((self.logFlags & mask) != 0):
            return True
        else:
            return False

    def info(self, msg:str):
        self.logger.info(msg)

    def warn(self, msg:str):
        self.logger.warning(msg)
    def fatal(self, msg:str):
        self.logger.critical(msg)

    def debug(self, msg:str):
        self.logger.debug(msg)

    def exception(self, msg:str):
        self.logger.exception(msg)

    def flush(self):
        self._sc.flush()
        if self._fh:
            self._fh.flush()


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

    def empty(self) -> bool:
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




