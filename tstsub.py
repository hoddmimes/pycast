from __future__ import annotations
import random
import sys
import re
import time
from time import sleep
from typing import Any

from pymc.aux.aux import Aux
from pymc.connection import Connection
from pymc.connection_configuration import ConnectionConfiguration
from pymc.distributor import Distributor
from pymc.distributor_configuration import DistributorConfiguration, DistributorLogFlags
from pymc.publisher import Publisher
from pymc.subscriber import Subscriber
from pymc.distributor_events import DistributorEvent
from tstmsg import TestMessage

update_count: int = 0
start_time: int = 0
params: dict = None
sequence_number = 0


def str_to_bool(value: str) -> bool:
    value = value.lower()
    if value in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif value in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError("invalid truth value %r" % (value,))


def parse_subjects(arg: str) -> [str]:
    x = re.search("^(\d+)", arg)
    if x is not None:
        _count = int(x.group(1))
        _subjects = []
        for i in range(_count):
            _subjects.append("/test/{}".format(str(i).zfill(4)))
        return _subjects
    else:
        return arg.partition(',')


def parse_arguments() -> dict:
    params = {'check_seqno': False,
              'verbose': 100,
              'subjects': ['/...']}
    i: int = 0
    prmcnt: int = len(sys.argv)
    print(sys.argv)
    while i < prmcnt:
        if sys.argv[i] == "-check_seqno":
            params['check_seqno'] = bool(sys.argv[i + 1])
            i += 1
        if sys.argv[i] == "-subjects":
            v = sys.argv[i + 1]
            params['subjects'] = parse_subjects(sys.argv[i + 1])
            i += 1
        if sys.argv[i] == "-verbose":
            params['verbose'] = int(sys.argv[i + 1])
            i += 1
        if sys.argv[i] == "-check_seqno":
            params['check_seqno'] = str_to_bool(sys.argv[i + 1])
            i += 1
        i += 1
    return params


def main():
    global params
    params = parse_arguments()
    distributor_configuration: DistributorConfiguration = DistributorConfiguration(application_name='test')
    distributor_configuration.log_flags = (DistributorLogFlags.LOG_DEFAULT_FLAGS +
                                           # DistributorLogFlags.LOG_DATA_PROTOCOL_XTA +
                                           # + DistributorLogFlags.LOG_DATA_PROTOCOL_RCV +
                                           DistributorLogFlags.LOG_RMTDB_EVENTS
                                           )

    distributor: Distributor = Distributor(configuration=distributor_configuration)
    connection: Connection = distributor.create_connection(ConnectionConfiguration(mca='224.10.11.12', mca_port=5656))
    subscriber: Subscriber = distributor.create_subscriber(connection=connection, event_callback=event_callback,
                                                           update_callback=update_callback)

    _subjects = params['subjects']
    for s in _subjects:
        subscriber.add_subscription(subject=s, callback_parameter=s)

    try:
        while True:
            sleep(5)
    except KeyboardInterrupt:
        print("Interrupted, time to exit")


def event_callback(event: DistributorEvent):
    print("{} [SUBSCRIBER-EVENT-CALLBACK] {}".format(Aux.time_string(), event))


def update_callback(subject: str,
                    data: bytes,
                    callback_parameter: object,
                    app_id: int,
                    queue_length: int):
    global start_time
    global update_count
    global params
    global sequence_number

    if start_time == 0:
        start_time = time.perf_counter()

    update_count += 1
    _msg = TestMessage(data)

    _verbose = int(params['verbose'])
    _check_seqno = bool(params['check_seqno'])

    if sequence_number + 1 == _msg.seqno:
        sequence_number = _msg.seqno
    elif sequence_number == 0:
        sequence_number = _msg.seqno
    else:
        raise Exception("sequence number out of synch expected {} got {}".format((sequence_number + 1), _msg.seqno))

    if _verbose <= 5:
        print("{} [SUBSCRIBER-UPDATE] subject: {} data: {}".format(Aux.time_string(), subject, _msg))
    elif (update_count % _verbose) == 0:
        _rate = update_count / (time.perf_counter() - start_time)
        print(
            "{} [SUBSCRIBER-UPDATE] subject: {} updates {} rate {:.1f} queue_length: {} data: {} callback_parameter: {} app_id: {}"
            .format(Aux.time_string(), subject, update_count, round(_rate, 1), queue_length, _msg,
                    str(callback_parameter), hex(app_id)))


if __name__ == '__main__':
    main()
