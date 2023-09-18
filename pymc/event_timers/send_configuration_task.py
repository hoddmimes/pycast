from pymc.event_timers.connection_timer_event import ConnectionTimerEvent


def sendConfiguration(connection: 'Connection'):
    connection.push_out_configuration()
    connection.push_out_configuration()


class SendConfigurationTask(ConnectionTimerEvent):
    def __init__(self, connection_id: int):
        super().__init__(connection_id)

    def execute(self, connection: 'Connection'):
        if connection.is_time_to_die:
            self.cancel()
            return
        if len(connection.publishers) == 0:
            return
        sendConfiguration(connection)

