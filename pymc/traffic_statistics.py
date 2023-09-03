from pymc.aux.aux import Aux
from pymc.aux.atomic import AtomicInt, AtomicLong
from pymc.connection_timers import ConnectionTimerTask
import pymc.msg.net_msg_update as netmsg
from pymc.msg.segment import Segment
from abc import ABC, abstractmethod
from distributor_interfaces import ConnectionBase
from threading import Lock

class CounterElement(object):

    def __init__(self, attribute_name):
        self.mAttributeName = attribute_name
        self.mTotal:int = 0
        self.mCurrValueSec:int = 0
        self.mValueSec:int = 0
        self.mMaxValueSec:int = 0
        self.mMaxValueSecTime:int = 0
        self.lock = Lock()

    def getTotal(self):
        return self.mTotal

    def getPeakPerSec(self):
        return self.mMaxValueSec

    def getPeakTime(self) -> str:
        return Aux.time_string(self.mMaxValueSecTime)

    def getValueSec(self) -> int:
        return self.mValueSec

    def update(self, pValue):
        with self.lock:
            self.mTotal += pValue
            self.mCurrValueSec += pValue

    def calculate(self, time_diff):
        if time_diff > 0:
            with self.lock:
                self.mValueSec = (self.mCurrValueSec * 1000)  # time_diff
                if self.mValueSec > self.mMaxValueSec:
                    self.mMaxValueSec = self.mValueSec
                    self.mMaxValueSecTime = Aux.currentMilliseconds()

    def __str__(self) ->str:
        _tim_str = Aux.time_string( self.mMaxValueSecTime)
        return self.mAttributeName + " Total: " + str(self.mTotal) + " " + \
               self.mAttributeName + "/Sec : " + str(self.mValueSec) + " Max " + \
               self.mAttributeName + "/Sec : " + str(self.mMaxValueSec) + " Max Time: " + _tim_str

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
    def getRcv1MinMessages(self) ->CounterElement:
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
    def  getXtaAvgMessageFillRate(self)-> float:
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
    def getXtaTotalNumberOfBytes(self) ->int:
        pass

    ## Returns average values / sec for aggregated updates under 1 min
    @abstractmethod
    def getXta1MinUpdates(self) ->CounterElement:
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
class TrafficStatisticTimerTask(ConnectionTimerTask, DistributorPublisherStatisticsIf, DistributorSubscriberStatisticsIf):
    def __init__(self, pDistributorConnectionId):
        super().__init__(pDistributorConnectionId)
        _now = Aux.currentMilliseconds()
        self.mStartTime:int = _now
        self.mLastTimeStamp = _now
        self.mLastTimeStamp_1_min = _now
        self.mLastTimeStamp_5_min = _now
        self.mXtaBytes = CounterElement("XtaBytes")
        self.mXtaMsgs = CounterElement("XtaMsgs")
        self.mXtaUpdates = CounterElement("XtaUpdates")
        self.mXtaBytes1min = CounterElement("XtaBytes_1_min")
        self.mXtaMsgs1min = CounterElement("XtaMsgs_1_min")
        self.mXtaUpdates1min = CounterElement("XtaUpdates_1_min")
        self.mXtaBytes5min = CounterElement("XtaBytes_5_min")
        self.mXtaMsgs5min = CounterElement("XtaMsgs_5_min")
        self.mXtaUpdates5min = CounterElement("XtaUpdates_5_min")
        self.mRcvBytes = CounterElement("RcvBytes")
        self.mRcvMsgs = CounterElement("RcvMsgs")
        self.mRcvUpdates = CounterElement("RcvUpdates")
        self.mRcvBytes1min = CounterElement("RcvBytes_1_min")
        self.mRcvMsgs1min = CounterElement("RcvMsgs_1_min")
        self.mRcvUpdates1min = CounterElement("RcvUpdates_1_min")
        self.mRcvBytes5min = CounterElement("RcvBytes_5_min")
        self.mRcvMsgs5min = CounterElement("RcvMsgs_5_min")
        self.mRcvUpdates5min = CounterElement("RcvUpdates_5_min")
        self.mXtaTotalBytes:AtomicLong = AtomicLong(0)
        self.mXtaTotalUserDataUpdates:AtomicLong = AtomicLong(0)
        self.mXtaTotalSegments:AtomicLong = AtomicLong(0)
        self.mRcvTotalBytes:AtomicLong = AtomicLong(0)
        self.mRcvTotalUpdates:AtomicLong = AtomicLong(0)
        self.mRcvTotalSegments:AtomicLong = AtomicLong(0)
        self.mXtaUpdSendTimeUsec:AtomicLong = AtomicLong(0)
        self.mXtaUpdFillTotalBufferAllocateSize:AtomicLong = AtomicLong(0)
        self.mXtaUpdFillTotalUpdateBytes:AtomicLong = AtomicLong(0)
        self.mXtaUpdPackages:AtomicLong = AtomicLong(0)

    def transform(self, pCE) -> netmsg.DataRateItem:
        tDR = netmsg.DataRateItem()
        tDR.setCurrValue(pCE.getValueSec())
        tDR.setPeakValue(pCE.getPeakPerSec())
        tDR.setPeakTime(pCE.getPeakTime())
        tDR.setTotal(pCE.getTotal())
        return tDR

    def getXtaBytesInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.mXtaBytes)

    def getXtaMsgsInfo(self)-> netmsg.DataRateItem:
        return self.transform(self.mXtaMsgs)

    def getXtaUpdatesInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.mXtaUpdates)

    def getXtaBytes1MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.mXtaBytes1min)

    def getXtaMsgs1MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.mXtaMsgs1min)

    def getXtaUpdates1MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.mXtaUpdates1min)

    def getXtaBytes5MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.mXtaBytes5min)

    def getXtaMsgs5MinInfo(self)-> netmsg.DataRateItem:
        return self.transform(self.mXtaMsgs5min)

    def getXtaUpdates5MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.mXtaUpdates5min)

    def getRcvBytesInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.mRcvBytes)

    def getRcvMsgsInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.mRcvMsgs)

    def getRcvUpdatesInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.mRcvUpdates)

    def getRcvBytes1MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.mRcvBytes1min)

    def getRcvMsgs1MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.mRcvMsgs1min)

    def getRcvUpdates1MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.mRcvUpdates1min)

    def getRcvBytes5MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.mRcvBytes5min)

    def getRcvMsgs5MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.mRcvMsgs5min)

    def getRcvUpdates5MinInfo(self) -> netmsg.DataRateItem:
        return self.transform(self.mRcvUpdates5min)

    def getTotalXtaBytes(self) -> int:
        return self.mXtaTotalBytes.get()

    def getTotalXtaSegments(self) -> int:
        return self.mXtaTotalSegments.get()

    def getTotalXtaUpdates(self) -> int:
        return self.mXtaTotalUserDataUpdates.get()

    def getTotalRcvBytes(self) -> int:
        return self.mRcvTotalBytes.get()

    def getTotalRcvSegments(self) -> int:
        return self.mRcvTotalSegments.get()

    def getTotalRcvUpdates(self)  -> int:
        return self.mRcvTotalUpdates.get()

    def getStatistics(self) ->[]:
        tResult = [None] * 6
        tResult[0] = str(self.mXtaBytes)
        tResult[1] = str(self.mXtaUpdates)
        tResult[2] = str(self.mXtaMsgs)
        tResult[3] = str(self.mRcvBytes)
        tResult[4] = str(self.mRcvUpdates)
        tResult[5] = str(self.mRcvMsgs)
        return tResult

    def updateXtaStatistics(self, pSegment: Segment, pXtaTimeUsec: int):
        self.mXtaMsgs.update(1)
        self.mXtaMsgs1min.update(1)
        self.mXtaMsgs5min.update(1)
        self.mXtaBytes.update(pSegment.getSize())
        self.mXtaBytes1min.update(pSegment.getSize())
        self.mXtaBytes5min.update(pSegment.getSize())
        self.mXtaTotalBytes.addAndGet(pSegment.getSize())
        self.mXtaTotalSegments.incrementAndGet()
        if (pSegment.isUpdateMessage()
                and ((pSegment.getHeaderSegmentFlags() & Segment.FLAG_M_SEGMENT_START) == Segment.FLAG_M_SEGMENT_START)
                and (pSegment.getHeaderMessageType() == Segment.MSG_TYPE_UPDATE)):
            tUpdateCount = pSegment.getUpdateUpdateCount()
            self.mXtaUpdates.update(tUpdateCount)
            self.mXtaUpdates1min.update(tUpdateCount)
            self.mXtaUpdates5min.update(tUpdateCount)
            self.mXtaTotalUserDataUpdates.addAndGet(tUpdateCount)
            self.mXtaUpdPackages.incrementAndGet()
            self.mXtaUpdSendTimeUsec.addAndGet(pXtaTimeUsec)
            self.mXtaUpdFillTotalUpdateBytes.addAndGet(pSegment.getSize())
            self.mXtaUpdFillTotalBufferAllocateSize.addAndGet(pSegment.getBufferAllocationSize())
        elif (pSegment.isUpdateMessage()):
            self.mXtaUpdPackages.incrementAndGet()
            self.mXtaUpdSendTimeUsec.addAndGet(pXtaTimeUsec)

    def updateRcvStatistics(self, segment):
        self.mRcvMsgs.update(1)
        self.mRcvMsgs1min.update(1)
        self.mRcvMsgs5min.update(1)
        self.mRcvBytes.update(segment.getLength())
        self.mRcvBytes1min.update(segment.getLength())
        self.mRcvBytes5min.update(segment.getLength())
        self.mRcvTotalBytes += segment.getLength()
        self.mRcvTotalSegments += 1
        if (segment.isUpdateMessage() and
            (segment.getHeaderSegmentFlags() & Segment.FLAG_M_SEGMENT_START == Segment.FLAG_M_SEGMENT_START) and
            (segment.getHeaderMessageType() == Segment.MSG_TYPE_UPDATE)):
                tUpdateCount = segment.getUpdateUpdateCount()
                self.mRcvUpdates.update(tUpdateCount)
                self.mRcvUpdates1min.update(tUpdateCount)
                self.mRcvUpdates5min.update(tUpdateCount)
                self.mRcvTotalUpdates += tUpdateCount

    def execute(self, connection:ConnectionBase):
        _current_time = Aux.currentMilliseconds()
        _tim_diff = _current_time - self.mLastTimeStamp
        self.mLastTimeStamp = _current_time
        self.mXtaMsgs.calculate(_tim_diff)
        self.mXtaBytes.calculate(_tim_diff)
        self.mXtaUpdates.calculate(_tim_diff)
        self.mRcvMsgs.calculate(_tim_diff)
        self.mRcvBytes.calculate(_tim_diff)
        self.mRcvUpdates.calculate(_tim_diff)
        if _current_time <= (self.mLastTimeStamp_1_min + 60000):
            _tim_diff = _current_time - self.mLastTimeStamp_1_min
            self.mLastTimeStamp_1_min = _tim_diff
            self.mXtaMsgs1min.calculate(_tim_diff)
            self.mXtaBytes1min.calculate(_tim_diff)
            self.mXtaUpdates1min.calculate(_tim_diff)
            self.mRcvMsgs1min.calculate(_tim_diff)
            self.mRcvBytes1min.calculate(_tim_diff)
            self.mRcvUpdates1min.calculate(_tim_diff)
        if _current_time<= (self.mLastTimeStamp_5_min + 300000):
            _tim_diff = _current_time - self.mLastTimeStamp_1_min
            mLastTimeStamp_5_min = _current_time
            self.mXtaMsgs5min.calculate(_tim_diff)
            self.mXtaBytes5min.calculate(_tim_diff)
            self.mXtaUpdates5min.calculate(_tim_diff)
            self.mRcvMsgs5min.calculate(_tim_diff)
            self.mRcvBytes5min.calculate(_tim_diff)
            self.mRcvUpdates5min.calculate(_tim_diff)

    def getXtaAvgMessageFillRate(self) -> int:
        if self.mXtaUpdFillTotalBufferAllocateSize == 0:
            return 0
        x = (self.mXtaUpdFillTotalUpdateBytes.get() * 10000) / self.mXtaUpdFillTotalBufferAllocateSize.get()
        tRatio = x / 100.0
        return tRatio # perecentage 0-100

    def getXtaAvgUpdatesPerMessage(self) -> int:
        if self.mXtaUpdPackages == 0:
            return 0
        x = (self.mXtaTotalUserDataUpdates.get() * 100.0) / self.mXtaUpdPackages.get()
        tRatio = x / 100
        return tRatio

    def getXtaAvgIOXTimeUsec(self) -> int:
        if self.mXtaTotalSegments.get() == 0:
            return 0
        else:
            return int(self.mXtaUpdSendTimeUsec.get() / self.mXtaTotalSegments.get())

    def getXtaTotalNumberOfUpdates(self) -> int:
        return self.mXtaTotalUserDataUpdates.get()

    def getXtaTotalNumberOfMessages(self) -> int:
        return self.mXtaTotalSegments.get()

    def getXtaTotalNumberOfBytes(self) -> int:
        return self.mXtaTotalBytes.get()

    def getXta1MinUpdates(self) -> int:
        return self.mXtaUpdates1min.mValueSec

    def getXta1MinMessages(self):
        return self.mXtaMsgs1min.mValueSec

    def getXta1MinBytes(self):
        return self.mXtaBytes1min.mValueSec

    def getRcvTotalNumberOfUpdates(self):
        return self.mRcvTotalUpdates.get()

    def getRcvTotalNumberOfMessages(self):
        return self.mRcvTotalSegments.get()

    def getRcvTotalNumberOfBytes(self):
        return self.mRcvTotalBytes.get()

    def getRcv1MinUpdates(self):
        return self.mRcvUpdates1min.mValueSec

    def getRcv1MinMessages(self):
        return self.mRcvMsgs1min.mValueSec

    def getRcv1MinBytes(self):
        return self.mRcvBytes1min.mValueSec

    def getInitTimeString(self) -> str:
        return Aux.time_string( self.mStartTime)

    def getSecondsSinceInit(self) ->int:
        tSec = (Aux.currentMilliseconds() - self.mStartTime) / 1000
        return int(tSec & 0xffffffff)