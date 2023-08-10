
class RcvUpdate(object):

    def __init__(self, connection_id:int, subject:str, update_data:bytearray, app_id:int):
        self.mUpdateData:bytearray = update_data
        self.mSubject:str = subject
        self.mAppId:int = app_id
        self.mConnectionId:int = connection_id

    def getSize(self) -> int:
        # 8 == bool string + 2 string len + string data + bool data + 4 data length + data
        return len(self.mSubject) + 8 + len(self.mUpdateData)


