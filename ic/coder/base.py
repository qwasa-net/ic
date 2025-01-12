import abc

from PIL import Image


class Coder(abc.ABC):

    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def encode(self, data: bytes, name: str) -> Image:
        pass


class FormatV1:

    VERSION = 1
    BOOTSTRAP = (
        0x010203,
        0xFEFDFC,
        0x810079,
        0x01CDEF,
    )
    BOOTSTRAP_SIZE = 41
    HEADER_SIZE = 69
