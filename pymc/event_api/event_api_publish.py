from pymc.event_loop import ConnectionEvent


class EventApiPublish(ConnectionEvent):

    def __init__(self, subject: str, data: bytes | bytearray):
        super().__init__( ConnectionEvent.API_EVENT)
        self._subject = subject
        self._data = data

    @property
    def subject(self) -> str:
        return self._subject

    @property
    def data(self):
        return self._data



    def __str__(self):
        return "subject: {} data_length: {}".format(self._subject, len(self._data))