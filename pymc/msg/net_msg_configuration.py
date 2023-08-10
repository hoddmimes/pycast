from pymc.msg.segment import Segment
from pymc.msg.net_msg import NetMsg
from io import StringIO
from pymc.aux.aux import Aux

class NetMsgConfiguration(NetMsg):
    def __init__(self, segment):
        super().__init__(segment)
        self.mMcAddress:int = None
        self.mMcPort:int = None
        self.mHbIntervalMs:int = None
        self.mCfgIntervalMs:int = None
        self.mApplName:int = None
        self.mSenderId:int = None
        self.mHostAddress:int = None
        self.mSenderStartTime:int = None

    def set(self, mc_addr:int, mc_port:int, sender_id:int, start_time:int, heartbeat_interval:int, config_interval:int, host_addr:int, appl_name:str):
        self.mMcAddress = mc_addr
        self.mMcPort = mc_port
        self.mHbIntervalMs = heartbeat_interval
        self.mSenderStartTime = start_time
        self.mSenderId = sender_id
        self.mCfgIntervalMs = config_interval
        self.mHostAddress = host_addr
        self.mApplName = appl_name

    def encode(self):
        super().encode()
        _encoder = super().getEncoder()
        _encoder.addInt(self.mMcAddress)
        _encoder.addInt(self.mMcPort)
        _encoder.addInt(self.mSenderId)
        _encoder.addInt(self.mSenderStartTime)
        _encoder.addInt(self.mHbInterval)
        _encoder.addInt(self.mCfgInterval)
        _encoder.addInt(self.mHostAddress)
        _encoder.addString(self.mApplName)

    def decode(self):
        super().decode()
        _decoder = super().getDecoder()
        self.mMcAddress = _decoder.readInt()
        self.mMcPort = _decoder.readInt()
        self.mSenderId = _decoder.readInt()
        self.mSenderStartTime = _decoder.readLong()
        self.mHbInterval = _decoder.readInt()
        self.mCfgInterval = _decoder.readInt()
        self.mHostAddress = _decoder.readInt()
        self.mApplName = _decoder.readString()



    def __str__(self):
        sb = StringIO()
        sb.write(super().__str__())
        sb.write("\n    <")
        sb.write("MC Addr: " + Aux.ipAddrIntToStr(self.getMcAddress()))
        sb.write(" MC port: " + str(self.getMcPort()))
        sb.write(" HB intval: " + str(self.getHeartbeatInterval()))
        sb.write(" CFG intval: " + str(self.getConfigurationInterval()))
        sb.write(" StartTime: " + str(self.getSenderStartTime()))
        sb.write(" SndrId: " + hex(self.getSenderId()))
        sb.write(" Host: " + str(self.getHostAddress()))
        sb.write(" Appl: " + str(self.getApplicationName()))
        sb.write(">")
        return "".join(sb)
