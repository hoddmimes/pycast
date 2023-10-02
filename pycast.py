import random
import threading
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



def publisher_event_callback(event: DistributorEvent):
    print("[PUBLISHER-EVENT-CALLBACK] {}".format(event))


def subscriber_event_callback(event: DistributorEvent):
    print("[SUBSCRIBER-EVENT-CALLBACK] {}".format(event))


def subscriber_update_callback(subject: str,
                        data: bytes,
                        callback_parameter: object,
                        app_id: int,
                        queue_length: int):
    data_string: str = data.decode("utf-8")
    print("[SUBSCRIBER-UPDATE] subject: {} data: {} callback_parameter: {} app_id: {} queue_length: {}"
          .format(subject, data_string, str(callback_parameter), hex(app_id), queue_length))


def create_data( size: int) -> bytes:
    bytarr = bytearray(size)
    for i in range(size):
        if ((i % 5) == 0) and i > 0:
            bytarr[i] = 32
        else:
            bytarr[i] = 65 + random.randrange(0,20)
    return bytes(bytarr)


def main():
    distributor_configuration: DistributorConfiguration = DistributorConfiguration(application_name='test')
    distributor_configuration.log_flags = DistributorLogFlags.LOG_DEFAULT_FLAGS # (DistributorLogFlags.LOG_DATA_PROTOCOL_XTA + DistributorLogFlags.LOG_DATA_PROTOCOL_RCV)

    ''' Create a Distributor instance'''
    distributor: Distributor = Distributor(configuration=distributor_configuration)
    ''' Create a connect instance i.e transport channel '''
    connection: Connection = distributor.create_connection(ConnectionConfiguration(mca='224.10.11.12', mca_port=5656))

    ''' Create a publisher instance on the just created connection '''
    publisher: Publisher = distributor.create_publisher(connection=connection, event_callback=publisher_event_callback)

    ''' Create a publisher on the just created connection '''
    subscriber: Subscriber = distributor.create_subscriber(connection=connection,
                                                           event_callback=subscriber_event_callback,
                                                           update_callback=subscriber_update_callback)

    ''' Setup subscription for some topics'''
    global test_subjects
    for subj in test_subjects:
        subscriber.add_subscription(subject=subj, callback_parameter='frotz_parameter')

    # Start publisher logic


    ''' Start to publish data '''
    while (True):
        _sleep_time = random.randrange(20, 2000)
        _subject_index = random.randrange(0, len(test_subjects))
        _data = create_data(random.randrange(20, 50))
        publisher.publish(subject=test_subjects[_subject_index], data_bytes=_data)

        Aux.sleep_ms(_sleep_time)


if __name__ == '__main__':
    main()
