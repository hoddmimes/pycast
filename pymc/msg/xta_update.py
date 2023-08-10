
class XtaUpdate(object):

    def __init__(self, subject:str, data:bytearray, length:int):
        self.mSubject = subject
        self.mData = data
        self.mDataLength =  length

    # XtaUpdate encoded layout
    # 1 byte subject present or not
    # 4 bytes subject length
    # 'n' bytes subject data
    # 1 byte update present or not
    # 4 bytes update data length
    # 'n' bytes update payload

    def getSize(self) -> int:
        tSize:int = len(self.mSubjectName) + (1+4+1+4) + self.mDataLength
        return tSize

    def getDataLength(self) -> int:
        return self.mDataLength