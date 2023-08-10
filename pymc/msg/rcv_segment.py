from pymc.msg.segment import Segment


class RcvSegment(Segment):
    def __init__(self, buffer):
        super().__init__(buffer)
        self.mFromAddress:int = None
        self.mFromPort:int = None

    def isStartSegment(self):
        if (self.getHeaderSegmentFlags() & Segment.FLAG_M_SEGMENT_START) != 0:
            return True
        else:
            return False

    def isEndSegment(self):
        if (self.getHeaderSegmentFlags() & Segment.FLAG_M_SEGMENT_END) != 0:
            return True
        else:
            return False

    def setFromAddress(self, from_addr:int):
        self.mFromAddress = from_addr

    def getFromAddress(self) -> int:
        return self.mFromAddress

    def setFromPort(self, from_port:int):
        self.mFromPort = from_port

    def setFrom(self, from_addr:int, from_port: int):
        self.mFromPort = from_port
        self.mFromAddress = from_addr

    def getFromPort(self) -> int:
        return self.mFromPort


    def hashCode(self):
        return super().hashCode()

    def equals(self, pObj):
        return super().equals(pObj)
