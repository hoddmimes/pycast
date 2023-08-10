import threading
from distributor_interfaces import DistributorBase
from distributor_interfaces import ConnectionBase




class Subscriber:
    def __init__(self, distributor: DistributorBase, connection: ConnectionBase):
        self.distributor:DistributorBase = distributor
        self.connection:ConnectionBase = connection
