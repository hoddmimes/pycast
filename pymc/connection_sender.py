import random

from distributor_interfaces import ConnectionBase, ConnectionSenderBase, DistributorBase
from pymc.msg.net_msg_update import NetMsgUpdate
from pymc.msg.net_msg_heartbeat import NetMsgHeartbeat
from pymc.msg.net_msg_configuration import NetMsgConfiguration
from pymc.msg.net_msg_retransmission import NetMsgRetransmissionRqst, NetMsgRetransmissionNAK
from pymc.msg.xta_update import XtaUpdate
from pymc.msg.xta_segment import XtaSegment
from pymc.msg.segment import Segment

from pymc.aux.aux import Aux
from pymc.distributor_events import DistributorCommunicationErrorEvent
from pymc.aux.aux_uuid import Aux_UUID
from pymc.aux.log_manager import LogManager
from pymc.traffic_flow_task import TrafficFlowTask
from connection_configuration import ConnectionConfiguration
from aux.distributor_exception import DistributorException
from pymc.send_holdback_task import SenderHoldbackTimerTask
from pymc.connection_timers import ConnectionTimerExecutor,ConnectionTimerTask
from pymc.distributor_configuration import DistributorLogFlags
from pymc.client_controller import ClientDeliveryController
from pymc.connection import Connection
from logging import Logger


class SendHeartbeatTask(ConnectionTimerTask):
    def __init__(self, connection_id):
        super().__init__(connection_id)
        self.mConnectionIsSending = False

    def dataHasBeenPublished(self):
        self.mConnectionIsSending = True

    def execute(self, connection:Connection):
        if connection.mTimeToDie:
            self.cancel()
            return
        if connection.mPublishers.isEmpty() and not connection.mIsCmaConnection:
            return
        if not self.mConnectionIsSending:
            self.sendHeartbeat(connection)
        self.mConnectionIsSending = False

    def sendHeartbeat(self, connection:Connection):
        tHeartbeat = NetMsgHeartbeat(XtaSegment(connection.mConfiguration.smallsegment_size ))
        tHeartbeat.setHeader(
            Segment.MSG_TYPE_HEARTBEAT,
            Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END,
            connection.mConnectionSender.mLocalAddress,
            connection.mConnectionSender.mSenderId,
            self.getStartTimeAsInt(),
            connection.mDistributor.getAppId()
        )
        tHeartbeat.set(
            connection.mIpmg.mInetAddress,
            connection.mIpmg.mPort,
            connection.mConnectionSender.mSenderId,
            connection.mConnectionSender.mCurrentSeqNo
        )
        tHeartbeat.encode()
        connection.mConnectionSender.sendSegment(XtaSegment(tHeartbeat.mSegment))
        tHeartbeat = None

class SendConfigurationTask(ConnectionTimerTask):
    def __init__(self, connection_id:int):
        super().__init__(connection_id)

    def sendConfiguration(self, connection:Connection):
        connection.pushOutConfiguration()
        connection.pushOutConfiguration()

    def execute(self, connection:Connection):
        if self.mConnection.mTimeToDie:
            self.cancel()
            return
        if self.mConnection.mPublishers.isEmpty() and not self.mConnection.mIsCmaConnection:
            return
        self.sendConfiguration(connection)

## =====================================================================
## ConnectionSender
## ======================================================================
class ConnectionSender(ConnectionSenderBase):

    _cLogger:Logger = None

    def __init__(self, connectionBase: ConnectionBase):
        self.mConnectionId = Aux_UUID.getId()
        self.mErrorSignaled:bool = False
        self.mLastUpdateFlushSeqno:int = 0
        self.mConnectionStartTime:int = Aux.currentMilliseconds()
        self.mConnection:ConnectionBase = connectionBase
        self.mConfiguration:ConnectionConfiguration = connectionBase.getConfiguration()
        self.mDistributor:DistributorBase = connectionBase.getDistributor()
        self.mCurrentUpdate:NetMsgUpdate = self.getNewCurrentUpdate()          #  initialize self.mCurrentUpdate:NetMsgUpdate
        self.mHeartbeatTimerTask = SendHeartbeatTask(connection_id=self.mConnectionId)
        if ConnectionSender._cLogger == None:
            ConnectionSender._cLogger = LogManager.getInstance().getLogger('ConnectionSender')

        if self.mConfiguration.sender_id_port == 0:
            self.mSenderId = Aux.allocateServerPortId(self.mConfiguration.sender_id_port_offset)
        else:
            self.mSenderId = self.mConfiguration.sender_id_port

        self.mCurrentSeqNo = 1
        self.mLocalAddress:int = self.mDistributor.getLocalInetAddr()
        self.mCurrentSeqNo:int = 0
        self.mTrafficFlowTask:TrafficFlowTask = TrafficFlowTask( connection_id=self.mConnectionId)

    def logInfo(self, msg):
        ConnectionSender._cLogger.info( msg )

    def logWarning(self, msg):
        ConnectionSender._cLogger.warning( msg )
    def logError(self, msg):
        ConnectionSender._cLogger.error( msg )
    def logThrowable(self, exception):
        ConnectionSender._cLogger.exception( exception )

    def getStartTimeAsInt(self) -> int:
        return (self.mConnectionStartTime & 0x7fffffff)

    def getNewCurrentUpdate(self) -> NetMsgUpdate:
        if self.mCurrentUpdate:
            raise DistributorException("Illegal state: mCurrentUpdate is not null")

        _msg = NetMsgUpdate( XtaSegment( self.mConnection.getConfiguration().segment_size ))


        _msg.setHeader( messageType=Segment.MSG_TYPE_UPDATE,
                                       segmentFlags=Segment.FLAG_M_SEGMENT_START,
                                       localAddress=self.mDistributor.getLocalInetAddr(),
                                       senderId=self.mSenderId,
                                       senderStartTime=self.getStartTimeAsInt(),
                                       appId=self.mDistributor.getId())

        return _msg

    def logProtocolData(self, segment:Segment):
        _msg_type = segment.getHeaderMessageType()
        _segment = segment.copy()

        if _msg_type == Segment.MSG_TYPE_CONFIGURATION:
            _msg = NetMsgConfiguration(_segment)
            _msg.decode()
            self.logInfo("PROTOCOL [XTA] " + str(_msg))
        elif _msg_type == Segment.MSG_TYPE_HEARTBEAT:
            _msg = NetMsgHeartbeat(_segment)
            _msg.decode()
            self.logInfo("PROTOCOL [XTA] " + str(_msg))
        elif _msg_type == Segment.MSG_TYPE_RETRANSMISSION:
            _msg = NetMsgUpdate(_segment)
            _msg.decode()
            self.logInfo("PROTOCOL [XTA] <retrans>" + str(_msg))
        elif _msg_type == Segment.MSG_TYPE_RETRANSMISSION_NAK:
            _msg = NetMsgRetransmissionNAK(_segment)
            _msg.decode()
            self.logInfo("PROTOCOL [XTA] " + str(_msg))
        elif _msg_type == Segment.MSG_TYPE_RETRANSMISSION_RQST:
            _msg = NetMsgRetransmissionRqst(_segment)
            _msg.decode()
            self.logInfo("PROTOCOL [XTA] " + str(_msg))
        elif _msg_type == Segment.MSG_TYPE_UPDATE:
            _msg = NetMsgUpdate(_segment)
            _msg.decode()
            self.logInfo("PROTOCOL [XTA] " + str(_msg))
        else:
            self.logInfo("PROTOCOL [XTA] unknown message: " + Segment.getMessageTypeString(_msg_type))


    def publishUpdate( self, xtaUpdate:XtaUpdate):
        return self.updateToSegment(xtaUpdate);


    def updateToSegment(self, xtaUpdate:XtaUpdate):
        if xtaUpdate.getSize() > self.mConfiguration.segment_size - NetMsgUpdate.MIN_UPDATE_HEADER_SIZE:
            self.largeUpdateToSegments(xtaUpdate)
        else:
            self.smallUpdateToSegment(xtaUpdate)

        if (self.mConfiguration.send_holdback_delay_ms > 0 and
            self. mTrafficFlowTask.getUpdateRate() > self.mConfiguration.send_holdback_threshold and
            (Aux.currentMilliseconds() - self.mCurrentUpdate.mCreateTime)  < self.mConfiguration.send_holdback_delay_ms):
                if self.mLastUpdateFlushSeqno < self.mCurrentUpdate.mFlushSequenceNumber:
                    self.mLastUpdateFlushSeqno = self.mCurrentUpdate.mFlushSequenceNumber
                    _timerTask:SenderHoldbackTimerTask = SenderHoldbackTimerTask( self.mConnection.getConnectionId(), self.mLastUpdateFlushSeqno)
                    ConnectionTimerExecutor.getInstance().add( self.mConfiguration.send_holdback_delay_ms, _timerTask)
                return 0
        # send message
        return self.queueCurrentUpdate(Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END)

    def smallUpdateToSegment(self, xtaUpdate:XtaUpdate):
        if not self.mCurrentUpdate.addUpdate( xtaUpdate ):
            # send current segment and allocate a new empty one
            self.queueCurrentUpdate(Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END)

            if not self.mCurrentUpdate.addUpdate( xtaUpdate ):
                raise DistributorException('Update did not fit into segment, {} bytes'.format(xtaUpdate.getSize()))


    def largeUpdateToSegments(self, xtaUpdate:XtaUpdate):
        # If we have updates in the current segment, queue and get a new segment
        self.queueCurrentUpdate(Segment.FLAG_M_SEGMENT_START + Segment.FLAG_M_SEGMENT_END)

        _offset:int = 0
        _segment_count = 0

        self.mCurrentUpdate.addLargeUpdateHeader( xtaUpdate.mSubject, xtaUpdate.mDataLength )

        while _offset < xtaUpdate.mDataLength:
            _offset += self.mCurrentUpdate.addLargeData(xtaUpdate, _offset)
            self.mCurrentUpdate.mUpdateCount = 1
            if _segment_count == 0:
                self.queueCurrentUpdate(Segment.FLAG_M_SEGMENT_START)
            elif _offset == xtaUpdate.mDataLength:
                self.queueCurrentUpdate(Segment.FLAG_M_SEGMENT_END)
            else:
                self.queueCurrentUpdate(Segment.FLAG_M_SEGMENT_MORE)
            _segment_count += 1

    def queueCurrentUpdate(self, segment_flags:int) -> int:

        if self.mCurrentUpdate.mUpdateCount == 0:
            return 0;   # No updates in segment we can continue to use this one


        self.mCurrentUpdate.setSequenceNumber( self.mCurrentSeqNo )
        self.mCurrentUpdate.setHeaderSegmentFlags( (segment_flags & 0xff) )

        self.mCurrentUpdate.encode()
        _send_delay = self.sendSegment( self.mCurrentUpdate.getSegment() )
        self.mCurrentUpdate = self.getNewCurrentUpdate()
        return _send_delay

    def isLoggingEnabled(self, flag:int ):
        if self.mDistributor.getConfiguration().logFlags & flag:
            return True
        else:
            return False

    def logInfo(self, message:str ):
        ConnectionSender.cLogger.info( message )

    def logThrowable(self, exception):
        ConnectionSender.cLogger.exception( exception )

    def randomError(self, probability:int ): #  n/1000
        x = random.randrange(0,1000)
        if x <= probability:
            return True
        return False

    def sendSegment(self, segment:XtaSegment):

        _send_time_usec:int = 0

        if self.mErrorSignaled:
            segment = None
            return 0

        if segment.getHeaderMessageType() == Segment.MSG_TYPE_UPDATE:
            if self.mConfiguration.max_bandwidth_kbit > 0:
                self.mTrafficFlowTask.increment(segment.getLength());
                _wait_ms = self.mTrafficFlowTask.calculateWaitTimeMs()
                Aux.sleepMs( _wait_ms )


        if self.isLoggingEnabled( DistributorLogFlags.LOG_SEGMENTS_EVENTS ):
            self.logInfo.info('XTA Segment: ' + segment.toString())

        if self.isLoggingEnabled( DistributorLogFlags.LOG_DATA_PROTOCOL_XTA ):
            self.logProtocolData( segment )

        if (self.mConfiguration.fake_xta_error_rate > 0 and
            self.randomError( self.mConfiguration.fake_xta_error_rate ) and
            segment.mHdrMsgType == Segment.MSG_TYPE_UPDATE):
                    self.logInfo('SIMULATED XTA Error Segment [{}] dropped'.format(segment.getSeqno()))
        else:
            try:
                _send_time_usec = self.mConnection.send( segment )
                self.mConnection.updateTrafficStatistics( segment, _send_time_usec)
            except Exception as e:
                self.mErrorSignaled = True
                self.logThrowable( e )
                tEvent:DistributorCommunicationErrorEvent = DistributorCommunicationErrorEvent( direction="[SEND]",
                                                                                                mc_addr=self.mConnection.getMcAddress(),
                                                                                                mc_port=self.mConnection.getMcPort(),
                                                                                                reason=str(e))
                ClientDeliveryController.getInstance().queueEvent( tEvent )

            if segment.getHeaderMessageType() == Segment.MSG_TYPE_UPDATE:
                self.mRetransmissionCache.addSentUpdate(segment);
                self.mHeartbeatTimerTask.dataHasBeenPublished();
            else:
                segment = None



        return _send_time_usec
