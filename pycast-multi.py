from __future__ import annotations

import threading
import sys
import random
from time import sleep

from pymc.aux.aux import Aux
from pymc.connection import Connection
from pymc.connection_configuration import ConnectionConfiguration
from pymc.distributor import Distributor
from pymc.distributor_configuration import DistributorConfiguration, DistributorLogFlags
from pymc.publisher import Publisher
from pymc.subscriber import Subscriber
from pymc.distributor_events import DistributorEvent

test_subjects = [
    '/test-subject',
    '/foo/001', '/foo/002', '/foo/003', '/foo/004', '/foo/005',
    '/foo/bar/001', '/foo/bar/002', '/foo/bar/003', '/foo/bar/004', '/foo/bar/005'
    '/frotz/xyz/a/b/c001', '/frotz/a/b/c/d/xyz/002', '/frotz/a/b/xyz/1234/67542/003', '/frotz/xyz/004', '/frotz/bar/005'
]



param_pub_min_delay = 20
param_pub_max_delay = 2000
param_sub_threads = 5
param_pub_threads = 2




def create_data( size: int) -> bytes:
    bytarr = bytearray(size)
    for i in range(size):
        if ((i % 5) == 0) and i > 0:
            bytarr[i] = 32
        else:
            bytarr[i] = 65 + random.randrange(0,20)
    return bytes(bytarr)



class SubscriberThread(threading.Thread):

    def __init__(self, index:int, subject_count: int ):
        super().__init__()
        self._index = index
        self._subject_count = subject_count
        self._subscriber: Subscriber = None

    def event_callback(self, event: DistributorEvent):
        print("[SUBSCRIBER-EVENT-CALLBACK] [{}] {}".format(self._index, event))

    def update_callback(self, subject: str,
                        data: bytes,
                        callback_parameter: object,
                        app_id: int,
                        queue_length: int):
        data_string: str = data.decode("utf-8")
        print("[SUBSCRIBER-UPDATE] [{}] subject: {} data: {} callback_parameter: {} app_id: {} queue_length: {}"
              .format(self._index, subject, data_string, str(callback_parameter), hex(app_id), queue_length))

    def run(self):
        print(distributor)
        self._subscriber = distributor.create_subscriber( connection=connection,
                                                          event_callback=self.event_callback,
                                                          update_callback=self.update_callback)
        for i in range(self._subject_count):
            idx: int = random.randrange(0,len(test_subjects))
            self._subscriber.add_subscription(subject=test_subjects[idx],
                                              callback_parameter='clbprm thread: {} subscridx: {}'.
                                              format(self._index,i))

        print("subscriber thread [{}] started".format(self._index))

class PublisherThread(threading.Thread):

    def __init__(self, index: int, subject_count: int):
        super().__init__()
        self._index = index
        self._subject_count = subject_count
        self._publisher: Publisher = None

    def event_callback(self, event: DistributorEvent):
        print("[PUBLISHER-EVENT-CALLBACK] [{}] {}".format(self._index, event))

    def run(self):
        print(distributor)
        self._publisher: Publisher = distributor.create_publisher( connection=connection,
                                                                   event_callback=self.event_callback)
        while (True):
            _sleep_time = random.randrange(20, 2000)
            _subject_index = random.randrange(0, len(test_subjects))
            _data = create_data(random.randrange(20, 50))
            self._publisher.publish(subject=test_subjects[_subject_index], data_bytes=_data)

            Aux.sleep_ms(_sleep_time)



def parse_arguments():
    argc: int  = len(sys.argv)
    i: int = 0
    while(i < argc):
        if sys.argv[i] == '-sthreads':
            global param_sub_threads
            param_sub_threads = int( sys.argv[i+1])
            i += 1
        if sys.argv[i] == '-pthreads':
            global param_pub_threads
            param_pub_threads = int( sys.argv[i+1])
            i += 1
        if sys.argv[i] == '-min_delay':
            global param_pub_min_delay
            param_pub_min_delay = int( sys.argv[i+1])
            i += 1
        if sys.argv[i] == '-max_delay':
            global param_pub_max_delay
            param_pub_max_delay = int( sys.argv[i+1])
            i += 1
        i += 1


def main():
    parse_arguments()
    distributor_configuration: DistributorConfiguration = DistributorConfiguration(application_name='test')
    distributor_configuration.log_flags += (DistributorLogFlags.LOG_DATA_PROTOCOL_XTA + DistributorLogFlags.LOG_DATA_PROTOCOL_RCV)

    global distributor
    global connection

    distributor = Distributor(configuration=distributor_configuration)
    connection = distributor.create_connection(ConnectionConfiguration(mca='224.10.11.12', mca_port=5656))

    for si in range(param_sub_threads):
        thr = SubscriberThread(index=(si+1), subject_count=int(len(test_subjects)/2))
        thr.start()
    for pi in range(param_pub_threads):
        thr = PublisherThread(index=(pi+101),
                              subject_count=int(len(test_subjects)/3))
        thr.start()


    while True:
        sleep(5)

if __name__ == '__main__':
    main()
