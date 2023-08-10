from segment import Segment

class XtaSegment(Segment):

    def __init__(self, bufferSize:int):
        super().__init__( bufferSize )
        self.mAllocatedBufferSize = bufferSize


    def getSize(self) -> int:
        return self.getLength()

    def getBufferAllocationSize(self) -> int:
        return self.mAllocatedBufferSize