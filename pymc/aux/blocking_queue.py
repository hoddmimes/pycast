import threading
import queue


class BlockingQueue:

    def __init__(self):
        self._event = threading.Event()
        self._mutex = threading.Lock()
        self._queue = queue.Queue()

    def add(self, item: object):
        with self._mutex:
            self._queue.put(item)
            self._event.set()

    def is_empty(self) -> bool:
        return self._queue.empty()

    def take(self) -> object:
        with self._mutex:
            if not self._queue.empty():
                _item = self._queue.get()
                if self._queue.empty():
                    self._event.clear()
                return _item

            self._event.clear()

        self._event.wait()
        with self._mutex:
            _item = self._queue.get()
            if self._queue.empty():
                self._event.clear()
            return _item

    def drain(self, max_items=0x7fffffff) -> []:
        with self._mutex:
            if not self._queue.empty():
                _length = min(self._queue.qsize(), max_items)
                _list = []
                for i in range(_length):
                    _list.append(self._queue.get())
                if self._queue.empty():
                    self._event.clear()
                return _list

            self._event.clear()

        self._event.wait()
        with self._mutex:
            _length = min(self._queue.qsize(), max_items)
            _list = [_length]
            for i in range(_length):
                _list.append(self._queue.get())
            if self._queue.empty():
                self._event.clear()
        return _list

    def clear(self):
        with self._mutex:
            self._queue.queue.clear()
            self._event.clear()

    def __str__(self) -> str:
        with self._mutex:
            if self._event.is_set():
                return 'queue-size: {} event-is-set'.format(self._queue.qsize())
            else:
                return 'queue-size: {} event-is-not-set'.format(self._queue.qsize())
