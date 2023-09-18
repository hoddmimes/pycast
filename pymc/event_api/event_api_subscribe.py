from pymc.event_loop import ConnectionEvent


class EventApiSubscribe(ConnectionEvent):

    def __init__(self, subscriber_id: int, subject: str, callback_parameter: object ):
        super().__init__( ConnectionEvent.API_EVENT)
        self._subscriber_id = subscriber_id
        self._subject = subject
        self._callback_parameter = callback_parameter

    @property
    def subscriber_id(self) -> int:
        return self._subscriber_id

    @property
    def subject(self) -> str:
        return self._subject

    @property
    def callback_parameter(self) -> object:
        return self._callback_parameter



    def __str__(self):
        return "subscriber_id: {} subject: {} callback_parameter: {}".format(hex(self._subscriber_id), self._subject, self._callback_parameter)