import threading
import socket
import datetime
from pymc.aux.aux import Aux

class Aux_UUID:
    # The Aux_UUID is a long 64bit consisting of
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
        _uuid = Aux_UUID()
        _uuid.getNextId()