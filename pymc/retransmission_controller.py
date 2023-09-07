import logging
from collections import deque
from threading import Timer

from pymc.client_controller import ClientDeliveryController
from pymc.connection_configuration import ConnectionConfiguration
from pymc.distributor_events import DistributorNaggingErrorEvent


class NaggingMonitorTask:
    def __init__(self, configuration: ConnectionConfiguration):
        self._interval_count:int = 0
        self._last_interval_count:int = 0
        self._consequtive_ticks:int = 0
        self._cfg_window_interval:int = configuration.nagging_window_interval_ms()
        self._cfg_check_interval:int= configuration.nagging_check_interval_ms
        self._cfg_max_retransmissions:int  = configuration.nagging_max_retransmit()

    def clear(self):
        self._interval_count = 0
        self._last_interval_count = 0
        self._consequtive_ticks = 0

    def execute(self, connection: 'Connection'):
        try:
            if self._interval_count > self._last_interval_count:
                self._consequtive_ticks += self._cfg_window_interval
                if self._consequtive_ticks >= self._cfg_check_interval:
                    if self._cfg_max_retransmissions == 0 or (0 < self._cfg_max_retransmissions <= self._interval_count):
                        _event = DistributorNaggingErrorEvent(connection.mIpmg.mInetAddress, connection.mIpmg.mPort)
                        ClientDeliveryController.get_instance().queue_event(connection.connection_id, _event)
                    else:
                        self.clear()
            else:
                self.clear()
        except Exception as e:
            connection.log_exception(e)


class RetransmissionController:
    def __init__(self, connection: 'Connection'):
        self._connection = connection
        self._nagging_monitor = NaggingMonitorTask(connection.connection_id, connection.configuration)
        self.mRetransmissionRequestQueue = deque()
        if connection.configuration.nagging_window_interval > 0:
            Timer(connection.configuration.nagging_window_interval, self._nagging_monitor.start()

    def close(self):
        if not self.mRetransmissionRequestQueue:
            return
        with self.mRetransmissionRequestQueue:
            for item in self.mRetransmissionRequestQueue:
                item.cancel()
            self.mRetransmissionRequestQueue.clear()
        self._nagging_monitor.cancel()

    def createRetransmissionRequest(self, pRemoteConnection, pLowSeqNo, pHighSeqNo):
        tRqstTask = self.RetransmissionRequestItem(self._connection._connection_id, pRemoteConnection.mRemoteConnectionId, pLowSeqNo, pHighSeqNo)
        self.mRetransmissionRequestQueue.append(tRqstTask)
        Timer(0, self._connection._configuration.getRetransmissionTimeout(), tRqstTask).start()

    def updateRetransmissions(self, pSegment):
        if not self.mRetransmissionRequestQueue:
            return
        with self.mRetransmissionRequestQueue:
            for item in self.mRetransmissionRequestQueue:
                item.adjustSeqNo(pSegment.getSeqno())

    def processRetransmissionNAK(self, pSegment):
        if not self.mRetransmissionRequestQueue:
            return
        tMsg = NetMsgRetransmissionNAK(pSegment)
        tMsg.decode()
        tNakSeqNo = tMsg.getNakSeqNo()
        tRqst = None
        with self.mRetransmissionRequestQueue:
            for i in range(len(tNakSeqNo)):
                for item in self.mRetransmissionRequestQueue:
                    tRqst = item
                    if tNakSeqNo[i] >= tRqst.mLowSeqNo and tNakSeqNo[i] <= tRqst.mHighSeqNo:
                        tRemoteConnection = self._connection.mConnectionReceiver.mRemoteConnectionController.getConnection(pSegment)
                        tRqst.requestNakSmoked(tRemoteConnection, tNakSeqNo[i])
                        self.mRetransmissionRequestQueue.remove(item)

    class RetransmissionRequestItem:
        def __init__(self, pDistributorConnectionId, pRemoteConnectionId, pLowSeqNo, pHighSeqNo):
            self.mRemoteConnectionId = pRemoteConnectionId
            self.mLowSeqNo = pLowSeqNo
            self.mHighSeqNo = pHighSeqNo
            self.mRetries = 0
            self.mServedList = []
            self.mServedListIndex = 0

        def queueRetransmissionRqstMessage(self, pConnection, pRemoteConnection):
            tRqstMsg = NetMsgRetransmissionRqst(XtaSegment(pConnection._configuration.getSmallSegmentSize()))
            tRqstMsg.setHeader(
                Segment.MSG_TYPE_RETRANSMISSION_RQST,
                Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END,
                pConnection.mConnectionSender.mLocalAddress,
                pConnection.mConnectionSender.mSenderId,
                pConnection.mConnectionSender.mConnectionStartTime & 0xffffffff,
                pConnection.mDistributor.getAppId()
            )
            tRqstMsg.set(
                pConnection.mConnectionSender.mLocalAddress,
                self.mLowSeqNo,
                self.mHighSeqNo,
                pConnection.mConnectionSender.mLocalAddress.getHostName(),
                pConnection.mApplicationConfiguration.getApplicationName(),
                pRemoteConnection.mRemoteSenderId,
                pRemoteConnection.mRemoteStartTime & 0xffffffff
            )
            pConnection.mRetransmissionStatistics.updateOutStatistics(
                pConnection.mIpmg.mInetAddress,
                pConnection.mIpmg.mPort,
                pRemoteConnection.mRemoteHostInetAddress
            )
            tRqstMsg.encode()
            pConnection.mConnectionSender.send_segment(tRqstMsg._segment)

        def requestNakSmoked(self, tRemoteConnection, pNakSeqNo):
            tEvent = DistributorRetransmissionNAKErrorEvent(
                self.mConnection.mIpmg.mInetAddress,
                self.mConnection.mIpmg.mPort
            )
            if self.mConnection.isLogFlagSet(DistributorApplicationConfiguration.LOG_RETRANSMISSION_EVENTS):
                self.mConnection.log(
                    f"RETRANSMISSION: RCV NAK (NakSeqNo: {pNakSeqNo})  Remote Addr: {tRemoteConnection.mRemoteHostAddressString} Remote Sender Id: {tRemoteConnection.mRemoteSenderId} LowSeqNo: {self.mLowSeqNo} HighSeqNo: {tRemoteConnection.mHighiestSeenSeqNo}"
                )
            ClientDeliveryController.get_instance().queue_event(self.mConnection._connection_id, tEvent)

        def adjustSeqNo(self, pSeqNo):
            if pSeqNo > self.mHighSeqNo or pSeqNo < self.mLowSeqNo:
                return
            if pSeqNo in self.mServedList:
                return
            self.mServedList.append(pSeqNo)
            self.mServedListIndex += 1
            if pSeqNo == self.mHighSeqNo:
                self.mHighSeqNo -= 1
            if pSeqNo == self.mLowSeqNo:
                self.mLowSeqNo += 1

        def execute(self, pConnection):
            tResend = False
            tFailed = False
            tRemoteConnection = pConnection.mConnectionReceiver.mRemoteConnectionController.getRemoteConnection(self.mRemoteConnectionId)
            try:
                if pConnection.mTimeToDie:
                    self.cancel()
                    return
                if self.mServedListIndex == len(self.mServedList):
                    self.mRetransmissionRequestQueue.remove(self)
                    self.cancel()
                    return
                elif self.mRetries > pConnection._configuration.getRetransmissionRetries():
                    tFailed = True
                else:
                    tResend = True
                if tResend:
                    if self.mConnection.isLogFlagSet(DistributorApplicationConfiguration.LOG_RETRANSMISSION_EVENTS):
                        self.mConnection.log(
                            f"RETRANSMISSION: XTA REQUEST RETRANSMISSION Segments [{self.mLowSeqNo}:{self.mHighSeqNo}] Retry: [{self.mRetries}] Remote Addr: {tRemoteConnection.mRemoteHostAddressString} Remote Sender Id: {tRemoteConnection.mRemoteSenderId} ({self.mServedListIndex}) served out of ({len(self.mServedList)}) requested"
                        )
                    self.queueRetransmissionRqstMessage(pConnection, tRemoteConnection)
                    self.mRetries += 1
                elif tFailed:
                    self.cancel()
                    with self.mRetransmissionRequestQueue:
                        self.mRetransmissionRequestQueue.remove(self)
                    tEvent = DistributorTooManyRetransmissionRetriesErrorEvent(
                        self.mConnection.mIpmg.mInetAddress,
                        self.mConnection.mIpmg.mPort
                    )
                    if self.mConnection.isLogFlagSet(DistributorApplicationConfiguration.LOG_RETRANSMISSION_EVENTS):
                        self.mConnection.log(
                            f"RETRANSMISSION: RCV TO MANY RETRANSMISSION  Remote Addr: {tRemoteConnection.mRemoteHostAddressString} Remote Sender Id: {tRemoteConnection.mRemoteSenderId} LowSeqNo: {self.mLowSeqNo} HighSeqNo: {self.mHighSeqNo}"
                        )
                    ClientDeliveryController.get_instance().queue_event(self.mConnection._connection_id, tEvent)
            except Exception as e:
                print(e)

