from __future__ import annotations
import logging
import sys

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

    @staticmethod
    def getInstance() -> LogManager:
        if not LogManager._instance:
            LogManager._instance = LogManager()
        return LogManager._instance


    def getLogger( self, moduleName:str ) -> logging.Logger:
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

