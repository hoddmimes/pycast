
class MessageBase:

    def __init__(self):
        pass

    def encode(self) -> bytearray:
        raise NotImplementedError("Should have implemented this")
    def decode(self, buffer: bytearray):
        raise NotImplementedError("Should have implemented this")

    def toString(self) -> dict:
        raise NotImplementedError("Should have implemented this")