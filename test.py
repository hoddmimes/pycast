from __future__ import annotations
import logging
import sys
import threading
import time
from pymc.aux import PCUUID
from pymc.aux import Aux
import netifaces as ni
from threading import Timer
from io import StringIO
import socket
import os




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


class TestClass:


    def __init__(self):
        self.frotz = 'frotz'
        self.x = threading.Thread( target=self.workingThread, args=[self])
        self.x.start()

    def workingThread(self, args):
        for i in range(10):
            print("working thread loop {}".format(i))
            time.sleep(0.8)




def main():
   x:int = 0x1A2B3C
   print("HEX value: {0:x}".format(x))







if __name__ == '__main__':
    main()