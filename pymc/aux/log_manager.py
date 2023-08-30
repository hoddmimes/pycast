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
    def setConfiguration(to_console=True, to_file=True, file_name='Distributor.log', level=logging.DEBUG):
        if not LogManager._instance:
            LogManager._instance = LogManager()
        LogManager._instance.to_console = to_console
        LogManager._instance.to_file = to_file
        LogManager._instance.filename = file_name
        LogManager._instance.level = level

    @staticmethod
    def getInstance() -> LogManager:
        if not LogManager._instance:
            LogManager._instance = LogManager()
        return LogManager._instance

    def getLogger(self, module_name: str) -> logging.Logger:
        _logger = logging.Logger(module_name)
        if not LogManager._instance.to_console and not LogManager._instance.to_file:
            _logger.addHandler(logging.NullHandler())
            _logger.propagate = False
            return _logger

        logging.basicConfig(level=logging.DEBUG, encoding='utf-8')
        _logger.propagate = False

        _formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s - %(name)s - %(message)s',
                                       datefmt='%Y-%m-%d %H:%M:%S')

        if LogManager._instance.to_file and LogManager._instance.filename and len(LogManager._instance.filename) > 0:
            _fh = logging.FileHandler(LogManager._instance.filename)
            _fh.setFormatter(_formatter)
            _logger.addHandler(_fh)

        if LogManager._instance.to_console:
            _sc = logging.StreamHandler(sys.stdout)
            _sc.setFormatter(_formatter)
            _logger.addHandler(_sc)

        return _logger

""" ============================================
            Test
============================================ """

def main():
    LogManager.setConfiguration(True, True, 'test.log', logging.DEBUG)
    log = LogManager.getInstance().getLogger('foobar')
    log.info("test info message")
    log.error("test error message")
    try:
        raise Exception("test exception")
    except Exception as e:
        log.exception(e)

if __name__ == '__main__':
    main()