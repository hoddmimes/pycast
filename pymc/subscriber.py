import threading

from aux import Aux
from aux import PCLogger
from distributor_interfaces import DistributorBase
from distributor_interfaces import ConnectionBase

from __future__ import annotations


class Subscriber:
    def __init__(self, distributor: DistributorBase, connection: ConnectionBase):
        self.distributor:DistributorBase = distributor
        self.connection = connection
