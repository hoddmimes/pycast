import threading

class Link:
    def __init__(self, obj: object):
        self._flink = None
        self._blink = None
        self._object = obj

class QueItr:

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
class Queue:

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




    def dump(self):
        self._mutex.acquire()
        _itm = self._header._flink
        while _itm != self._header:
            print( str( _itm._object))
            _itm = _itm._flink

        self._mutex.release()


    def iterrator(self) -> QueItr:
        return QueItr( self._header )



