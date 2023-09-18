from pymc.aux.aux import Aux
from pymc.aux.atomic import AtomicInt, AtomicLong
import pymc.msg.generated.net_messages as netmsg
from pymc.event_timers.connection_timer_event import ConnectionTimerEvent
from pymc.msg.segment import Segment
from abc import ABC, abstractmethod
from threading import Lock


class CounterElement(object):

    def __init__(self, attribute_name):
        self._attribute_name = attribute_name
        self._total: int = 0
        self._curr_value_sec: int = 0
        self._value_sec: int = 0
        self._max_value_sec: int = 0
        self._max_value_sec_time: int = 0
        self._lock = Lock()

    @property
    def total(self) -> int:
        return self._total

    @property
    def peak_per_sec(self) -> int:
        return self._max_value_sec

    @property
    def peak_time(self) -> str:
        return Aux.time_string(self._max_value_sec_time)

    @property
    def value_sec(self) -> int:
        return self._value_sec

    def update(self, value: int):
        with self._lock:
            self._total += value
            self._curr_value_sec += value

    def calculate(self, time_diff):
        if time_diff > 0:
            with self._lock:
                self._value_sec = (self._curr_value_sec * 1000)  # time_diff
                if self._value_sec > self._max_value_sec:
                    self._max_value_sec = self._value_sec
                    self._max_value_sec_time = Aux.current_milliseconds()

    def __str__(self) -> str:
        _tim_str = Aux.time_string(self._max_value_sec_time)
        return self._attribute_name + " Total: " + str(self._total) + " " + \
            self._attribute_name + "/Sec : " + str(self._value_sec) + " Max " + \
            self._attribute_name + "/Sec : " + str(self._max_value_sec) + " Max Time: " + _tim_str


class DistributorSubscriberStatisticsIf(ABC):

    ## Returns the total number of user updates received
    @abstractmethod
    def getRcvTotalNumberOfUpdates(self) -> int:
        pass

    ## Return total number of UDP messages being received
    @abstractmethod
    def getRcvTotalNumberOfMessages(self) -> int:
        pass

    ## Returns, total number of bytes received
    @abstractmethod
    def getRcvTotalNumberOfBytes(self) -> int:
        pass

    ## Returns average values / sec for aggregated updates under 1 min
    @abstractmethod
    def getRcv1MinUpdates(self) -> CounterElement:
        pass

    ## Returns average values / sec for aggregated segment/messages under 1 min
    @abstractmethod
    def getRcv1MinMessages(self) -> CounterElement:
        pass

    ## Returns average values / sec for aggregated bytes under 1 min
    @abstractmethod
    def getRcv1MinBytes(self) -> CounterElement:
        pass

    @abstractmethod
    def getInitTimeString(self) -> str:
        pass

    ## return seconds since starting to collect statistics
    @abstractmethod
    def getSecondsSinceInit(self) -> int:
        pass


class DistributorPublisherStatisticsIf(ABC):

    ## Returns the average fill rate of allocated segments when being sent
    @abstractmethod
    def getXtaAvgMessageFillRate(self) -> float:
        pass

    ## Returns the average number of updates per sent UDP message
    @abstractmethod
    def getXtaAvgUpdatesPerMessage(self) -> float:
        pass

    ##Return the average I/O transmission time when sending user data UPD packages

    def getXtaAvgIOXTimeUsec(self) -> float:
        pass

    ## Returns the total number of user updates sent
    @abstractmethod
    def getXtaTotalNumberOfUpdates(self) -> int:
        pass

    ## Return total number of UDP messages being sent
    @abstractmethod
    def getXtaTotalNumberOfMessages(self) -> int:
        pass

    ## Returns, total number of bytes published
    @abstractmethod
    def getXtaTotalNumberOfBytes(self) -> int:
        pass

    ## Returns average values / sec for aggregated updates under 1 min
    @abstractmethod
    def getXta1MinUpdates(self) -> CounterElement:
        pass

    ## Returns average values / sec for aggregated segment/messages under 1 min
    @abstractmethod
    def getXta1MinMessages(self) -> CounterElement:
        pass

    ## Returns average values / sec for aggregated bytes under 1 min
    @abstractmethod
    def getXta1MinBytes(self) -> CounterElement:
        pass

    ## Return the time string "yyyy-MM-dd HH:mm:ss.SSS" when the collection of statistics started
    @abstractmethod
    def getInitTimeString(self) -> str:
        pass

    ## return seconds since starting to collect statistics
    @abstractmethod
    def getSecondsSinceInit(self) -> int:
        pass


class TrafficStatisticTimerTask(ConnectionTimerEvent, DistributorPublisherStatisticsIf,
                                DistributorSubscriberStatisticsIf):
    def __init__(self, pDistributorConnectionId):
        super().__init__(pDistributorConnectionId)
        _now = Aux.current_milliseconds()
        self.start_time: int = _now
        self.last_timestamp = _now
        self.last_timestamp_1_min = _now
        self.last_timestamp_5_min = _now
        self.xta_bytes = CounterElement("XtaBytes")
        self.xta_msgs = CounterElement("XtaMsgs")
        self.xta_updates = CounterElement("XtaUpdates")
        self.xta_bytes_1_min = CounterElement("XtaBytes_1_min")
        self.xta_msgs_1_min = CounterElement("XtaMsgs_1_min")
        self.xta_updates_1_min = CounterElement("XtaUpdates_1_min")
        self.xta_bytes_5_min = CounterElement("XtaBytes_5_min")
        self.xta_msgs_5_min = CounterElement("XtaMsgs_5_min")
        self.xta_updates_5_min = CounterElement("XtaUpdates_5_min")
        self.rcv_bytes = CounterElement("RcvBytes")
        self.rcv_msgs = CounterElement("RcvMsgs")
        self.rcv_updates = CounterElement("RcvUpdates")
        self.rcv_bytes_1_min = CounterElement("RcvBytes_1_min")
        self.rcv_msgs_1_min = CounterElement("RcvMsgs_1_min")
        self.rcv_updates_1_min = CounterElement("RcvUpdates_1_min")
        self.rcv_bytes_5_min = CounterElement("RcvBytes_5_min")
        self.rcv_msgs_5_min = CounterElement("RcvMsgs_5_min")
        self.rcv_updates_5_min = CounterElement("RcvUpdates_5_min")
        self.xta_total_bytes: AtomicLong = AtomicLong(0)
        self.xta_total_user_updates: AtomicLong = AtomicLong(0)
        self.xta_total_segments: AtomicLong = AtomicLong(0)
        self.rcv_total_bytes: AtomicLong = AtomicLong(0)
        self.rcv_total_user_updates: AtomicLong = AtomicLong(0)
        self.rcv_total_segments: AtomicLong = AtomicLong(0)
        self.xta_update_send_times: AtomicLong = AtomicLong(0)
        self.xta_update_fill_total_buffer_allocate_size: AtomicLong = AtomicLong(0)
        self.xta_update_fill_total_update_bytes: AtomicLong = AtomicLong(0)
        self.xta_update_packages: AtomicLong = AtomicLong(0)

    def transform(self, pCE) -> netmsg:
        tDR = netmsg.DataRateItem()
        tDR.setCurr_value(pCE.getValueSec())
        tDR.setPeak_value(pCE.getPeakPerSec())
        tDR.setPeak_time(pCE.getPeakTime())
        tDR.setTotal(pCE.getTotal())
        return tDR

    def getXtaBytesInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.xta_bytes)

    def getXtaMsgsInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.xta_msgs)

    def getXtaUpdatesInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.xta_updates)

    def getXtaBytes1MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.xta_bytes_1_min)

    def getXtaMsgs1MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.xta_msgs_1_min)

    def getXtaUpdates1MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.xta_updates_1_min)

    def getXtaBytes5MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.xta_bytes_5_min)

    def getXtaMsgs5MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.xta_msgs_5_min)

    def getXtaUpdates5MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.xta_updates_5_min)

    def getRcvBytesInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.rcv_bytes)

    def getRcvMsgsInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.rcv_msgs)

    def getRcvUpdatesInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.rcv_updates)

    def getRcvBytes1MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.rcv_bytes_1_min)

    def getRcvMsgs1MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.rcv_msgs_1_min)

    def getRcvUpdates1MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.rcv_updates_1_min)

    def getRcvBytes5MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.rcv_bytes_5_min)

    def getRcvMsgs5MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.rcv_msgs_5_min)

    def getRcvUpdates5MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.rcv_updates_5_min)

    def getTotalXtaBytes(self) -> int:
        return self.xta_total_bytes.get()

    def getTotalXtaSegments(self) -> int:
        return self.xta_total_segments.get()

    def getTotalXtaUpdates(self) -> int:
        return self.xta_total_user_updates.get()

    def getTotalRcvBytes(self) -> int:
        return self.rcv_total_bytes.get()

    def getTotalRcvSegments(self) -> int:
        return self.rcv_total_segments.get()

    def getTotalRcvUpdates(self) -> int:
        return self.rcv_total_user_updates.get()

    def getStatistics(self) -> [str]:
        _result = []
        _result.append(str(self.xta_bytes))
        _result.append(str(self.xta_updates))
        _result.append(str(self.xta_msgs))
        _result.append(str(self.rcv_bytes))
        _result.append(str(self.rcv_updates))
        _result.append(str(self.rcv_msgs))
        return _result

    def updateXtaStatistics(self, segment: Segment, xta_time_usec: int):
        self.xta_msgs.update(1)
        self.xta_msgs_1_min.update(1)
        self.xta_msgs_5_min.update(1)
        self.xta_bytes.update(segment.length)
        self.xta_bytes_1_min.update(segment.length)
        self.xta_bytes_5_min.update(segment.length)
        self.xta_total_bytes.increment(segment.length)
        self.xta_total_segments.incrementAndGet()
        if segment.is_update_message and segment.is_start_segment and segment.is_end_segment:
            _update_count = segment.update_count()
            self.xta_updates.update(_update_count)
            self.xta_updates_1_min.update(_update_count)
            self.xta_updates_5_min.update(_update_count)
            self.xta_total_user_updates.increment(_update_count)
            self.xta_update_packages.increment()
            self.xta_update_send_times.increment(xta_time_usec)
            self.xta_update_fill_total_update_bytes.increment(segment.length)
            self.xta_update_fill_total_buffer_allocate_size.increment(segment.allocate_size)
        elif (segment.is_update_message):
            self.xta_update_packages.increment()
            self.xta_update_send_times.increment(xta_time_usec)

    def update_rcv_statistics(self, segment):
        self.rcv_msgs.update(1)
        self.rcv_msgs_1_min.update(1)
        self.rcv_msgs_5_min.update(1)
        self.rcv_bytes.update(segment.length)
        self.rcv_bytes_1_min.update(segment.length)
        self.rcv_bytes_5_min.update(segment.length)
        self.rcv_total_bytes.increment(segment.length)
        self.rcv_total_segments.increment()
        if segment.is_update_message and segment.is_start_segment:
            _update_count = segment.update_count()
            self.rcv_updates.update(_update_count)
            self.rcv_updates_1_min.update(_update_count)
            self.rcv_updates_5_min.update(_update_count)
            self.rcv_total_user_updates.increment(_update_count)

    def execute(self, connection: 'Connection'):
        _current_time = Aux.current_milliseconds()
        _tim_diff = _current_time - self.last_timestamp
        self.last_timestamp = _current_time
        self.xta_msgs.calculate(_tim_diff)
        self.xta_bytes.calculate(_tim_diff)
        self.xta_updates.calculate(_tim_diff)
        self.rcv_msgs.calculate(_tim_diff)
        self.rcv_bytes.calculate(_tim_diff)
        self.rcv_updates.calculate(_tim_diff)
        if _current_time <= (self.last_timestamp_1_min + 60000):
            _tim_diff = _current_time - self.last_timestamp_1_min
            self.last_timestamp_1_min = _tim_diff
            self.xta_msgs_1_min.calculate(_tim_diff)
            self.xta_bytes_1_min.calculate(_tim_diff)
            self.xta_updates_1_min.calculate(_tim_diff)
            self.rcv_msgs_1_min.calculate(_tim_diff)
            self.rcv_bytes_1_min.calculate(_tim_diff)
            self.rcv_updates_1_min.calculate(_tim_diff)
        if _current_time <= (self.last_timestamp_5_min + 300000):
            _tim_diff = _current_time - self.last_timestamp_1_min
            mLastTimeStamp_5_min = _current_time
            self.xta_msgs_5_min.calculate(_tim_diff)
            self.xta_bytes_5_min.calculate(_tim_diff)
            self.xta_updates_5_min.calculate(_tim_diff)
            self.rcv_msgs_5_min.calculate(_tim_diff)
            self.rcv_bytes_5_min.calculate(_tim_diff)
            self.rcv_updates_5_min.calculate(_tim_diff)

    def getXtaAvgMessageFillRate(self) -> int:
        if self.xta_update_fill_total_buffer_allocate_size == 0:
            return 0
        x = (
                        self.xta_update_fill_total_update_bytes.get() * 10000) / self.xta_update_fill_total_buffer_allocate_size.get()
        tRatio = x / 100.0
        return tRatio  # perecentage 0-100

    def getXtaAvgUpdatesPerMessage(self) -> int:
        if self.xta_update_packages == 0:
            return 0
        x = (self.xta_total_user_updates.get() * 100.0) / self.xta_update_packages.get()
        tRatio = x / 100
        return tRatio

    def getXtaAvgIOXTimeUsec(self) -> int:
        if self.xta_total_segments.get() == 0:
            return 0
        else:
            return int(self.xta_update_send_times.get() / self.xta_total_segments.get())

    def getXtaTotalNumberOfUpdates(self) -> int:
        return self.xta_total_user_updates.get()

    def getXtaTotalNumberOfMessages(self) -> int:
        return self.xta_total_segments.get()

    def getXtaTotalNumberOfBytes(self) -> int:
        return self.xta_total_bytes.get()

    def getXta1MinUpdates(self) -> int:
        return self.xta_updates_1_min._value_sec

    def getXta1MinMessages(self):
        return self.xta_msgs_1_min._value_sec

    def getXta1MinBytes(self):
        return self.xta_bytes_1_min._value_sec

    def getRcvTotalNumberOfUpdates(self):
        return self.rcv_total_user_updates.get()

    def getRcvTotalNumberOfMessages(self):
        return self.rcv_total_segments.get()

    def getRcvTotalNumberOfBytes(self):
        return self.rcv_total_bytes.get()

    def getRcv1MinUpdates(self):
        return self.rcv_updates_1_min._value_sec

    def getRcv1MinMessages(self):
        return self.rcv_msgs_1_min._value_sec

    def getRcv1MinBytes(self):
        return self.rcv_bytes_1_min._value_sec

    def getInitTimeString(self) -> str:
        return Aux.time_string(self.start_time)

    def getSecondsSinceInit(self) -> int:
        tSec = (Aux.current_milliseconds() - self.start_time) / 1000
        return int(tSec & 0xffffffff)

    def __str__(self):
        return ("Out-msgs {} In-msgs: {} Out-upds: {} In-upds: {}".
                format( self.xta_msgs.total, self.rcv_msgs.total, self.xta_updates.total, self.rcv_updates.total))