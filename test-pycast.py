from time import sleep

from pymc.connection import Connection
from pymc.connection_configuration import ConnectionConfiguration
from pymc.distributor import Distributor
from pymc.distributor_configuration import DistributorConfiguration, DistributorLogFlags
from pymc.publisher import Publisher
from pymc.subscriber import Subscriber


class DistributeEvent:
    pass


def publisher_event_callback(event: DistributeEvent):
    print("[PUBLISHER-EVENT-CALLBACK] {}".format(event))


def subscriber_event_callback(event: DistributeEvent):
    print("[SUBSCRIBER-EVENT-CALLBACK] {}".format(event))


def subscriber_update_callback(subject: str,
                               data: bytes,
                               callback_parameter: object,
                               app_id: int,
                               queue_length: int):
    data_string: str = data.decode("utf-8")
    print("[SUBSCRIBER-UPDATE] subject: {} data: {} callback_parameter: {} app_id: {} queue_length: {}"
          .format(subject, data_string, str(callback_parameter), hex(app_id), queue_length))


def main():

    distributor_configuration: DistributorConfiguration = DistributorConfiguration(application_name='test')
    distributor_configuration.log_flags += (
                DistributorLogFlags.LOG_DATA_PROTOCOL_XTA + DistributorLogFlags.LOG_DATA_PROTOCOL_RCV)

    distributor: Distributor = Distributor(configuration=distributor_configuration)
    connection: Connection = distributor.create_connection(ConnectionConfiguration(mca='224.10.11.12', mca_port=5656))

    publisher: Publisher = distributor.create_publisher(connection=connection, event_callback=publisher_event_callback)
    subscriber: Subscriber = distributor.create_subscriber(connection=connection,
                                                           event_callback=subscriber_event_callback,
                                                           update_callback=subscriber_update_callback)

    subscriber.add_subscription(subject='/ALPHA01', callback_parameter='frotz_parameter')
    publisher.publish(subject='/ALPHA01', data_bytes=bytes('ABCDEFGHIJ0123456789', 'utf-8'))

    while True:
        sleep(5)


if __name__ == '__main__':
    main()
