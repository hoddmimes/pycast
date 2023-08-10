from pymc.msg.net_msg import NetMsg
from pymc.msg.segment import Segment
from pymc.aux.aux import Aux
from io import StringIO

class NetMsgHeartbeat(NetMsg):
    def __init__(self, segment:Segment):
        super().__init__(segment)
        self.mMcAddress:int = None
        self.mMcPort:int = None
        self.mSenderId:int = None
        self.mSeqno:int = None

    def encode(self):
        super().encode()
        _encoder = super().getEncoder()
        _encoder.addInt(self.mMcAddress)
        _encoder.addInt(self.mMcPort)
        _encoder.addInt(self.mSenderId)
        _encoder.addInt(self.mSeqno)

    def decode(self):
        super().decode()
        _decoder = super().getDecoder()
        self.mMcAddress = _decoder.readInt()
        self.mMcPort = _decoder.readInt()
        self.mSenderId = _decoder.readInt()
        self.mSeqno = _decoder.readInt()
        self.mSegment.mSeqno = self.mSeqno

    def set(self, mc_addr:int, mc_port:int, sender_id:int, sequence_no:int):
        self.mMcAddress = mc_addr
        self.mMcPort = mc_port
        self.mSenderId = sender_id
        self.mSeqno = sequence_no


    def __str__(self):
        sb = StringIO()
        sb.write(super().__str__())
        sb.write("\n    <")
        sb.write("MC addr: " + Aux.ipAddrIntToStr(self.mMcAddress))
        sb.write(" MC dst-port: " + str(self.getMcPort()))
        sb.write(" SndrId: " + hex(self.getSenderId()))
        sb.write(" Seqno: " + str(self.getSeqno()))
        sb.write(">")
        return sb.getvalue()
