import threading

from aux import Aux
from logging import Logger
from msg.pycast_messages import XtaUpdate
from aux import LogManager, DistributorException
from connection import ConnectionController
from distributor_interfaces import DistributorBase
from distributor_interfaces import ConnectionBase

from __future__ import annotations


class Publisher:

    def __init__(self, distributor: DistributorBase, connectionId:int ):
        self.mDistributor:DistributorBase = distributor
        self.mConnectionId:int = connectionId
        self.mLogger = LogManager.getLogger('Publisher')


    def publish(self, subject:str, data:bytearray, data_len:int = None):
        tConnection = ConnectionController.getAndLockDistributor(self.mConnectionId)

        if not tConnection:
            raise DistributorException("Distributor connection is closed or no longer valid")

        tXtaUpdate = XtaUpdate( subject, data, data_len or len(data))
        tConnection.publishUpdate( tXtaUpdate )
        ConnectionController.unlockDistributor(tConnection);