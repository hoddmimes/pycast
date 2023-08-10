import socket
from pymc.msg.segment import Segment
from pymc.msg.net_msg import NetMsg
from pymc.aux.aux import Aux
from io import StringIO


##=================================================================
##  NetMsgRetransmissionRqst
##=================================================================
class NetMsgRetransmissionRqst(NetMsg):
    def __init__(self, segment):
        super().__init__(segment)
        self.mApplName:str = None
        self.mHostName:str = None

    def set(self, requestor_addr:int, low_seqno:int, high_seqno:int, host_name:str, appl_name:str, sender_id:int, sender_start_time:int):
        self.mRequesstorAddress:int = requestor_addr
        self.mLowSeqno:int = low_seqno
        self.mHighSeqno:int = high_seqno
        self.mHostName:str = host_name
        self.mApplName:str = appl_name
        self.mSenderId:int = sender_id
        self.mSenderStartTime:int = sender_start_time


    def encode(self):
        super().encode()
        _encoder = super().getEncoder()
        _encoder.addInt(self.mRequesstorAddress)
        _encoder.addInt(self.mSenderId)
        _encoder.addInt(self.mSenderStartTime)
        _encoder.addInt(self.mLowSeqno)
        _encoder.addInt(self.mHighSeqno)
        _encoder.addString(self.mHostName)
        _encoder.addString(self.mApplName)

    def decode(self):
        super().decode()
        _decoder = super().getDecoder()
        mRequesstorAddress = _decoder.readInt()
        self.mSenderId = _decoder.readInt()
        self.mSenderStartTime = _decoder.readInt()
        self.mLowSeqno = _decoder.readInt()
        self.mHighSeqno = _decoder.readInt()
        self.mHostName = _decoder.readString()
        self.mApplName = _decoder.readString()



    def __str__(self):
        sb = StringIO
        sb.write(super().__str__())
        sb.write("\n    <")
        sb.write("Rqstr addr: " + Aux.ipAddrIntToStr(self.mRequesstorAddress))
        sb.write(" Rqstr appl name: " + self.mApplName)
        sb.write(" SndrId: " + hex(self.mSenderId))
        sb.write(" StartTime: " + Aux.time_string(self.mSenderStartTime))
        sb.write(" Seqno Lo: " + str(self.mLowSeqno))
        sb.write(" Seqno Hi: " + str(self.mHighSeqno))
        sb.write(">")
        return sb.getvalue()

##=================================================================
##  NetMsgRetransmissionNAK
##=================================================================
class NetMsgRetransmissionNAK(NetMsg):
    def __init__(self, segment):
        super().__init__(segment)
        self.mMcAddress:int = None
        self.mMcPort:int = None
        self.mSenderId:int = None
        self.mNakSequenceNumbers:list[int] = []

    def encode(self):
        super().encode()
        _encoder = super().getEncoder()
        _encoder.addInt(self.mMcAddress)
        _encoder.addInt(self.mMcPort)
        _encoder.addInt(self.mSenderId)
        _encoder.addInt(len(self.mNakSequenceNumbers))
        for i in range(len(self.mNakSequenceNumbers)):
            _encoder.addInt(self.mNakSequenceNumbers[i])

    def decode(self):
        super().decode()
        _decoder = self.mSegment.getDecoder()
        self.mMcAddress = _decoder.readInt()
        self.mMcPort = _decoder.readInt()
        self.mSenderId = _decoder.readInt()
        tElements = _decoder.readInt()
        self.mNakSequenceNumbers.clear()
        for i in range(tElements):
            self.mNakSequenceNumbers.append(_decoder.readInt())

    def set(self, mc_addr:int, mc_port:int, sender_id:int):
        self.mMcAddress = mc_addr
        self.mMcPort = mc_port
        self.mSenderId = sender_id


    def setNakSeqNo(self, nak_list:list[int]):
        self.mNakSequenceNumbers.clear()
        self.mNakSequenceNumbers.extend(nak_list)

    def getNakSeqNo(self):
        return self.mNakSequenceNumbers

    def __str__(self):
        sb = StringIO()
        sb.write(super().__str__())
        sb.write("\n    <")
        sb.write("MC addr: " + str(self.getMcAddress()))
        sb.write(" MC port: " + str(self.getMcPort()))
        sb.write(" SndrId: " + hex(self.getSenderId()))
        sb.write(" NAK count: " + str(len(self.mNakSequenceNumbers)))
        sb.write(" NAKSeqno:  ")
        for i in range(len(self.mNakSequenceNumbers)):
            sb.write(str(self.mNakSequenceNumbers[i]) + ", ")
        sb.truncate(len(sb.getvalue()) - 2) ## truncate the last two char i.e. ', '
        sb.append(">")
        return sb.getvalue()