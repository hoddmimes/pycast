import time
from datetime import datetime
from inspect import currentframe, getframeinfo
from io import StringIO


def _current_milliseconds() -> int:
    _now = datetime.now()
    return int(_now.timestamp() * 1000)


def _time_string(time_stamp: int) -> str:
    _tim = datetime.fromtimestamp(float(time_stamp) / 1000.0)
    return _tim.strftime('%H:%M:%S.%f')[:-3]


class Trace(object):
    enabled: bool = True
    print_limit_usec: int  = 3000

    def __init__(self, verbose: bool = True):
        if not Trace.enabled:
            return

        self._verbose: bool = verbose
        self._time_stamps: list[int] = []
        self._tags: list[str] = []
        if verbose:
            self._files: list[str] = []
            self._lineno: list[int] = []
            cf = currentframe()
            self._files.append(getframeinfo(cf.f_back).filename)
            self._lineno.append(cf.f_back.f_lineno)

        self._tags.append("bootstrap")
        self._time_stamps.append(int(time.perf_counter_ns() / 1000.0))

        self._init_time_ms = _current_milliseconds()

    def add(self, tag: str):
        if not Trace.enabled:
            return

        if self._verbose:
            cf = currentframe()
            self._files.append(getframeinfo(cf.f_back).filename)
            self._lineno.append(cf.f_back.f_lineno)
        self._tags.append(tag)
        self._time_stamps.append(int(time.perf_counter_ns() / 1000.0))

    def dump(self):
        if not Trace.enabled:
            return

        if self._time_stamps[-1] - self._time_stamps[0] < Trace.print_limit_usec:
            return

        sb = StringIO()
        if self._verbose:
            sb.write('Trace init {} file: {} lineno: {}\n'
                     .format(_time_string(self._init_time_ms),
                             self._files[0], self._lineno[0]))
        else:
            sb.write('Trace init {}\n'.format(_time_string(self._init_time_ms)))

        for i in range(1, len(self._time_stamps)):
            if self._verbose:
                _componets = self._files[i].split('/')
                _filename = _componets[-1]
                sb.write('    [{}] time: {} (usec) tag: "{}" file: {} lineno: {} ({} usec)\n'
                         .format(i,
                                 str(self._time_stamps[i] - self._time_stamps[i - 1]).rjust(0),
                                 self._tags[i].ljust(16),
                                 _filename.ljust(16),
                                 self._lineno[i],
                                 str(self._time_stamps[i] - self._time_stamps[0]).rjust(0)))
            else:
                sb.write('    [{}] time: {} tag: "{}"({} usec)\n'
                         .format(i,
                                 str(self._time_stamps[i] - self._time_stamps[i - 1]).rjust(8),
                                 self._tags[i].ljust(16),
                                 str(self._time_stamps[i] - self._time_stamps[0]).rjust(0)))

        print(sb.getvalue())


def c(trace: Trace):
    trace.add("calling c")


def b(trace: Trace):
    trace.add("calling b")
    c(trace)


def a(trace: Trace):
    trace.add("calling a")
    b(trace)


def test():
    print("===================== Verbose Mode ============================")
    trace: Trace = Trace(verbose=True)
    a(trace)
    trace.add("at the end")
    trace.dump()

    print("===================== Plain Mode ============================")
    trace: Trace = Trace(verbose=False)
    a(trace)
    trace.add("at the end")
    trace.dump()


if __name__ == '__main__':
    test()
