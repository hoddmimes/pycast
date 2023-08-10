import socket
from collections import defaultdict

class RemoteConnection:
    def __init__(self, pSegment, controller, connection):
        self.mRemoteConnectionId = pSegment
        self.mRemoteHostInetAddress = None
        self.mMca = None
        self.mRemoteApplicationName = None
        self.mRemoteAppId = None
        self.mRemoteSenderId = None
        self.mRemoteStartTime = None
        self.mCfgIsActive = False
        self.mHbIsActive = False
        self.mCheckConfigurationTask = None
        self.mCheckHeartbeatTask = None
        self.mController = controller
        self.mConnection = connection

    def processHeartbeatMsg(self, pSegment):
        pass

    def processUpdateSegment(self, pSegment):
        pass

class RemoteConnectionController:
    def __init__(self, pConnection):
        self.mRemoteConnections = {}
        self.mConnection = pConnection

    def close(self):
        for tRmtConn in self.mRemoteConnections.values():
            tRmtConn.mCheckConfigurationTask.cancel()
            tRmtConn.mCheckHeartbeatTask.cancel()
        self.mRemoteConnections.clear()

    def triggerRemoteConfigurationNotifications(self, pCallback):
        for tRemoteConnection in self.mRemoteConnections.values():
            tEvent = DistributorNewRemoteConnectionEvent(
                InetAddressConverter.inetAddrToInt(tRemoteConnection.mRemoteHostInetAddress),
                InetAddressConverter.inetAddrToInt(tRemoteConnection.mMca.mInetAddress),
                tRemoteConnection.mMca.mPort,
                tRemoteConnection.mRemoteApplicationName,
                tRemoteConnection.mRemoteAppId,
                tRemoteConnection.mRemoteSenderId,
                tRemoteConnection.mRemoteStartTime
            )
            ClientDeliveryController.getInstance().queueEvent(
                self.mConnection.mConnectionId, tEvent, pCallback
            )

    def getRemoteConnection(self, pRemoteConnectionId):
        for tRmtConn in self.mRemoteConnections.values():
            if tRmtConn.mRemoteConnectionId == pRemoteConnectionId:
                return tRmtConn
        return None

    def processConfigurationMessage(self, pSegment):
        tRemoteConnection = None
        with self.mRemoteConnections:
            tRemoteConnection = self.mRemoteConnections.get(pSegment)
            if tRemoteConnection is None:
                tRemoteConnection = RemoteConnection(pSegment, self, self.mConnection)
                self.mRemoteConnections[pSegment] = tRemoteConnection
                if self.mConnection.isLogFlagSet(DistributorApplicationConfiguration.LOG_RMTDB_EVENTS):
                    self.mConnection.log(
                        "Remote Connection [CREATED] (" + hex(pSegment) + ")\n" + tRemoteConnection.toString()
                    )
                tEvent = DistributorNewRemoteConnectionEvent(
                    InetAddressConverter.inetAddrToInt(tRemoteConnection.mRemoteHostInetAddress),
                    InetAddressConverter.inetAddrToInt(tRemoteConnection.mMca.mInetAddress),
                    tRemoteConnection.mMca.mPort,
                    tRemoteConnection.mRemoteApplicationName,
                    tRemoteConnection.mRemoteAppId,
                    tRemoteConnection.mRemoteSenderId,
                    tRemoteConnection.mRemoteStartTime
                )
                ClientDeliveryController.getInstance().queueEvent(self.mConnection.mConnectionId, tEvent)
            tRemoteConnection.mCfgIsActive = True
        return tRemoteConnection

    def getConnection(self, pSegment):
        with self.mRemoteConnections:
            tConnection = self.mRemoteConnections.get(pSegment)
        if tConnection is not None:
            tConnection.mHbIsActive = True
        return tConnection

    def removeRemoteConnection(self, pConnection):
        with self.mRemoteConnections:
            self.mRemoteConnections.values().remove(pConnection)

    def processHeartbeatMessage(self, pSegment):
        with self.mRemoteConnections:
            tConnection = self.mRemoteConnections.get(pSegment)
        if tConnection is not None:
            tConnection.processHeartbeatMsg(pSegment)

    def processUpdateSegment(self, pSegment):
        tRemoteConnection = self.mRemoteConnections.get(pSegment)
        if tRemoteConnection is not None:
            tRemoteConnection.mHbIsActive = True
            tRemoteConnection.processUpdateSegment(pSegment)

class SegmentBatch:
    def __init__(self, pFirstRcvSegmentInBatch):
        self.mList = [pFirstRcvSegmentInBatch]

    def addSegment(self, pSegment):
        self.mList.append(pSegment)
