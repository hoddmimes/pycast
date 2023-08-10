import threading


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
        with self._mutex:
            self._curr_item = self._curr_item._flink
            _item = self._curr_item._object
            return _item

    def remove(self):
        with self._mutex:
            if self._curr_item == self._header:
                return None
            else:
                _item = self._curr_item._object
                self._curr_item._blink._flink = self._curr_item._flink
                self._curr_item._flink._blink = self._curr_item._blink
                return _item
class LinkedList:

    def __init__(self):
        self._header = Link(None)
        self._header._blink = self._header
        self._header._flink = self._header
        self._mutex = threading.Lock()

    # insert item at the tail of the queue
    def add(self, item: object ):
        with self._mutex:
            _itm = Link(item)
            # Set new item links
            _itm._flink = self._header
            _itm._blink = self._header._blink

            self._header._blink._flink = _itm
            self._header._blink = _itm

    def addhdr(self, item: object ):
        with self._mutex:
            _itm = Link(item)
            # Set new item links
            _itm._flink = self._header._flink
            _itm._blink = self._header

            self._header._flink._blink = _itm
            self._header._flink = _itm

    def remove(self, item: object ) -> bool:
        with self._mutex:
            _itr = self.iterrator()
            while _itr.has_next():
                _obj = _itr.next()
                if _obj == item:
                    _itr.remove()
                    return True
            return False