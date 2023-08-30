from __future__ import annotations
from pymc.aux.aux import Aux
from pymc.msg.segment import Segment
from pymc.connection import Connection
from pymc.distributor_configuration import DistributorLogFlags
from pymc.distributor_events import DistributorNewRemoteConnectionEvent
from pymc.client_controller import ClientDeliveryController
from pymc.remote_connection import RemoteConnection

class RemoteConnectionController(object):
    def __init__(self, connection: Connection):
        self.mRemoteConnections: dict = {}
        self.mConnection = connection

    def close(self):
        for tRmtConn in self.mRemoteConnections.values():
            tRmtConn.mCheckConfigurationTask.cancel()
            tRmtConn.mCheckHeartbeatTask.cancel()
        self.mRemoteConnections.clear()

    def triggerRemoteConfigurationNotifications(self, pCallback):
        for tRemoteConnection in self.mRemoteConnections.values():
            tEvent = DistributorNewRemoteConnectionEvent(
                tRemoteConnection.mRemoteHostInetAddress,
                tRemoteConnection.mMca.mInetAddress,
                tRemoteConnection.mMca.mPort,
                tRemoteConnection.mRemoteApplicationName,
                tRemoteConnection.mRemoteAppId,
                tRemoteConnection.mRemoteSenderId,
                tRemoteConnection.mRemoteStartTime
            )
            ClientDeliveryController.getInstance().queueEvent( self.mConnection.mConnectionId, tEvent, pCallback )

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
                if self.mConnection.isLogFlagSet(DistributorLogFlags.LOG_RMTDB_EVENTS):
                    self.mConnection.log(
                        "Remote Connection [CREATED] (" + hex(pSegment) + ")\n" + tRemoteConnection.toString()
                    )
                tEvent = DistributorNewRemoteConnectionEvent(
                    tRemoteConnection.mRemoteHostInetAddress,
                    tRemoteConnection.mMca.mInetAddress,
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
