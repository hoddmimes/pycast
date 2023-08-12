from __future__ import annotations
import threading

class DummyLock(object):

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def __enter__(self):
        pass

class Link:
    def __init__(self, obj: object):
        self._flink = None
        self._blink = None
        self._object = obj

class ListItr:

    def __init__(self, linked_list: LinkedList, forward:bool=True):
        self.linked_list:LinkedList = linked_list
        self._forward = forward
        if forward:
            self._curr_item = linked_list._header._flink
        else:
            self._curr_item = linked_list._header._blink
        if linked_list._locking:
            self._mutex = threading.RLock()
        else:
            self._mutex = DummyLock()

    def has_next(self) -> bool:
        if self._forward and self._curr_item._flink != self.linked_list._header:
            return True
        if not self._forward and self._curr_item._blink != self.linked_list._header:
            return True
        return False


    def next(self) ->object:
        with self._mutex:
            if self._forward:
                self._curr_item = self._curr_item._flink
            else:
                self._curr_item = self._curr_item._blink
            _item = self._curr_item._object
            return _item

    def remove(self):
        with self._mutex:
            if self._curr_item == self.linked_list._header:
                return None
            else:
                _item = self._curr_item._object
                self._curr_item._blink._flink = self._curr_item._flink
                self._curr_item._flink._blink = self._curr_item._blink
                self.linked_list._size -= 1
                return _item
class LinkedList:

    def __init__(self, locking:bool = TRUE):
        self._header = Link(None)
        self._header._blink = self._header
        self._header._flink = self._header
        self._locking = locking
        self._size = 0
        if locking:
            self._mutex = threading.RLock()
        else:
            self._mutex = DummyLock()

    def isEmpty(self) -> bool:
        if self._header._blink == self._header:
            return True
        else:
            return False

    def clear(self):
        with self._mutex:
            while self._header._flink != self._header:
                self.removeFirst()

    def size(self) -> int:
            return self._size

    def peekFirst(self) -> object:
        with self._mutex:
            if self._header._flink == self._header:
                return None
            else:
                _itm:Link = self._header._flink
                return _itm._object

    def peekLast(self) -> object:
        with self._mutex:
            if self._header._blink == self._header:
                return None
            else:
                _itm:Link = self._header._blink
                return _itm._object

    def removeFirst(self) -> Link:
        with self._mutex:
            if self._header._flink == self._header:
                return None
            else:
                _itm:Link = self._header._flink
                _itm._flink._blink = _itm._blink
                _itm._blink._flink = _itm._flink
                self._size -= 1
                return _itm._object

    def removeLast(self) -> Link:
        with self._mutex:
            if self._header._flink == self._header:
                return None
            else:
                _itm: Link = self._header._blink
                _itm._flink._blink = _itm._blink
                _itm._blink._flink = _itm._flink
                self._size -= 1
                return _itm._object

    # insert item at the tail of the queue
    def add(self, item: object ):
        with self._mutex:
            _itm = Link(item)
            # Set new item links
            _itm._flink = self._header
            _itm._blink = self._header._blink

            self._header._blink._flink = _itm
            self._header._blink = _itm
            self._size += 1

    def addhdr(self, item: object ):
        with self._mutex:
            _itm = Link(item)
            # Set new item links
            _itm._flink = self._header._flink
            _itm._blink = self._header

            self._header._flink._blink = _itm
            self._header._flink = _itm
            self._size += 1

    def remove(self, item: object ) -> bool:
        with self._mutex:
            _itr = self.iterrator()
            while _itr.has_next():
                _obj = _itr.next()
                if _obj == item:
                    _itr.remove()
                    return True
            return False