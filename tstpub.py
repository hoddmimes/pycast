import random
import sys
import threading
import itertools
import time
from time import sleep

from pymc.aux.aux import Aux
from pymc.connection import Connection
from pymc.connection_configuration import ConnectionConfiguration
from pymc.distributor import Distributor
from pymc.distributor_configuration import DistributorConfiguration, DistributorLogFlags
from pymc.publisher import Publisher
from pymc.subscriber import Subscriber
from pymc.distributor_events import DistributorEvent


def parse_arguments() -> dict:
    params = {'min_size' : 8,
              'max_size' : 256,
              'verbose' : 100,
              'rate' : 10,
              'count' : 0xffffffffff,
              'subjects' : 1}
    i: int = 0
    prmcnt: int = len(sys.argv)
    while i < prmcnt:
        if sys.argv[i] == "-min_size":
            params['min_size'] = int(sys.argv[i+1])
            i += 1
        if sys.argv[i] == "-max_size":
            params['max_size'] = int(sys.argv[i+1])
            i += 1
        if sys.argv[i] == "-rate":
            params['rate'] = int(sys.argv[i+1])
            i += 1
        if sys.argv[i] == "-subjects":
            params['subjects'] = int(sys.argv[i+1])
            i += 1
        if sys.argv[i] == "-verbose":
            params['verbose'] = int(sys.argv[i+1])
            i += 1
        if sys.argv[i] == "-count":
            params['count'] = int(sys.argv[i+1])
            i += 1
        i += 1
    return params

def publisher_event_callback(event: DistributorEvent):
    print("[PUBLISHER-EVENT-CALLBACK] {}".format(event))



def create_data( size: int) -> bytes:
    bytarr = bytearray(size)
    itertools.repeat(65, len(bytarr))
    return bytes(bytarr)

def generate_subjects( count: int) -> [str]:
    subjects = []
    for i in range(count):
        subjects.append("/test/{}".format(str(i).zfill(4)))
    return subjects

def calculate_dismiss( rate: int) -> tuple[]:

    if rate <= 100:
        d = int(1000 / rate)
        f = 1
        return (f,d)
    if rate <= 600:
        d = int(4000 / rate)
        f = 4
        return (f,d)
    if rate <= 2000:
        d = int(10000 / rate)
        f = 10
        return (f,d)
    if rate <= 6000:
        d = int(30000 / rate)
        f = 30
        return (f,d)
    else:
        d = int(50000 / rate)
        f = 50
        return (f,d)






def main():
    params = parse_arguments()

    distributor_configuration: DistributorConfiguration = DistributorConfiguration(application_name='test')
    distributor_configuration.log_flags += (DistributorLogFlags.LOG_DEFAULT_FLAGS)

    distributor: Distributor = Distributor(configuration=distributor_configuration)
    connection: Connection = distributor.create_connection(ConnectionConfiguration(mca='224.10.11.12', mca_port=5656))

    publisher: Publisher = distributor.create_publisher(connection=connection, event_callback=publisher_event_callback)

    subjects = generate_subjects( params['subjects'])
    dismiss_data = calculate_dismiss( params['rate'])
    xta_loop = dismiss_data[0]
    xta_dismiss = dismiss_data[1]


    # Start publisher logic
    loop_count: int = 0
    stop_count: int = params['count']
    min_size = params['min_size']
    max_size = params['max_size']
    verbose = params['verbose']

    start_time = time.perf_counter()

    while loop_count < stop_count and loop_count < stop_count:
        for i in range(xta_loop):
            _subject_index = random.randrange(0, len(subjects))
            _data = create_data(random.randrange(min_size, max_size))
            publisher.publish(subject=subjects[_subject_index], data_bytes=_data)
            loop_count += 1
            if ((loop_count % verbose) == 0):
                print("published {} updates".format(loop_count))
        Aux.sleep_ms(xta_dismiss)

    exec_time = time.perf_counter()
    xta_rate = loop_count / exec_time
    print("Sent {} updates, rate {:.1f}".format(loop_count, round(xta_rate,1)))

    
if __name__ == '__main__':
    main()
