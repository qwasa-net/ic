import abc


class Decoder(abc.ABC):

    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def decode(self) -> tuple[bytes, str]:
        pass
