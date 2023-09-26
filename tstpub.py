import random
import sys
import time

from tstmsg import TestMessage
from pymc.aux.aux import Aux
from pymc.connection import Connection
from pymc.connection_configuration import ConnectionConfiguration
from pymc.distributor import Distributor
from pymc.distributor_configuration import DistributorConfiguration, DistributorLogFlags
from pymc.publisher import Publisher
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
            params['rate'] = float(sys.argv[i+1])
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
    print("{} [PUBLISHER-EVENT-CALLBACK] {}".format(Aux.time_string(), event))

def generate_subjects( count: int) -> [str]:
    subjects = []
    for i in range(count):
        subjects.append("/test/{}".format(str(i).zfill(4)))
    return subjects

def calculate_dismiss( rate ) -> tuple:

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

    distributor_configuration.log_flags += (DistributorLogFlags.LOG_DEFAULT_FLAGS +
                                            # DistributorLogFlags.LOG_RETRANSMISSION_CACHE +
                                            # DistributorLogFlags.LOG_DATA_PROTOCOL_XTA +
                                            # DistributorLogFlags.LOG_TRAFFIC_FLOW_EVENTS +
                                            DistributorLogFlags.LOG_RMTDB_EVENTS)

    distributor: Distributor = Distributor(configuration=distributor_configuration)

    connection_configuration: ConnectionConfiguration = ConnectionConfiguration(mca='224.10.11.12', mca_port=5656)
    connection_configuration.send_holdback_delay_ms = 20 # if the rate exceeds send_holdback_threshold  per send_holdback_calc_interval_ms
    connection_configuration.fake_xta_error_rate = 30 # randomly simulate 30 error per 1000 messages

    connection: Connection = distributor.create_connection(connection_configuration)

    publisher: Publisher = distributor.create_publisher(connection=connection, event_callback=publisher_event_callback)

    subjects = generate_subjects( params['subjects'])
    dismiss_data = calculate_dismiss( params['rate'])
    xta_loop = dismiss_data[0]
    xta_dismiss = dismiss_data[1]


    # Start publisher logic
    stop_count: int = params['count']
    min_size = params['min_size']
    max_size = params['max_size']
    verbose = params['verbose']

    start_time = time.perf_counter()
    sequence_number = 0

    while sequence_number < stop_count:
        for i in range(xta_loop):
            sequence_number += 1
            _msg = TestMessage(sequence_number, random.randrange(min_size, max_size))
            _subject_index = random.randrange(0, len(subjects))
            publisher.publish(subject=subjects[_subject_index], data_bytes=_msg.encode())
            if ((sequence_number % verbose) == 0):
                print("published {} updates".format(sequence_number))
        Aux.sleep_ms(xta_dismiss)

    exec_time = time.perf_counter()
    xta_rate = sequence_number / exec_time
    print("{} Sent {} updates, rate {:.1f}".format(Aux.time_string(), sequence_number, round(xta_rate,1)))

    
if __name__ == '__main__':
    main()
