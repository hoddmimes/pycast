import threading

class AtomicInt():
    def __init__(self, value=0):
        self._value = int(value)
        self._lock = threading.Lock()

    def increment(self, d=1) -> int:
        with self._lock:
            if self._value == 0x7FFFFFFF: # wrap around
                self._value = 1
            self._value += int(d)
            return self._value
    def decrement(self, d=1):
        with self._lock:
            self._value -= int(d)
            return self._value

    def incrementAndGet(self, d=1):
        with self._lock:
            if self._value == 0x7FFFFFFF: # wrap around
                self._value = 1
            self._value += int(d)
            return self._value

    def decrementAndGet(self, d=1):
        return self.incrementAndGet(-d)

    def get(self):
        with self._lock:
            return self._value

    def set(self, v):
        with self._lock:
            self._value = int(v)
            return self._value

class AtomicLong():
    def __init__(self, value=0):
        self._value = int(value)
        self._lock = threading.Lock()

    def increment(self, d=1) -> int:
        with self._lock:
            self._value += int(d)
            return self._value
    def decrement(self, d=1):
        with self._lock:
            self._value -= int(d)
            return self._value

    def incrementAndGet(self, d=1):
        with self._lock:
            self._value += int(d)
            return self._value

    def decrementAndGet(self, d=1):
        return self.incrementAndGet(-d)

    def get(self):
        with self._lock:
            return self._value

    def set(self, v):
        with self._lock:
            self._value = int(v)
            return self._value