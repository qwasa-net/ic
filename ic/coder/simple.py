import math

from PIL import Image

from .base import Coder, FormatV1


class SimpleCoder(FormatV1, Coder):

    def __init__(
        self,
        w: int = 1280,
        h: int | None = None,
        *args,
        **kwargs,
    ):
        self.w = max(w, self.BOOTSTRAP_SIZE + self.HEADER_SIZE)
        self.h = h
        self.pos = 0
        self.image = None

    def calculate_image_size(self, data: bytes) -> tuple[int, int]:
        data_len = (len(data) // 3 + 1) + self.HEADER_SIZE + self.BOOTSTRAP_SIZE
        if not self.w:
            wq = math.sqrt(data_len) + 1
            self.w = 2 ** math.ceil(math.log2(wq))
        self.h = data_len // self.w + 1
        return self.w, self.h

    def create_image(self) -> Image:
        self.image = Image.new("RGB", (self.w, self.h))
        return self.image

    def xy(self) -> tuple[int, int]:
        return (self.pos % self.w, self.pos // self.w)

    def draw_bootstrap(self) -> None:
        self.pos = 0
        for i in range(self.BOOTSTRAP_SIZE):
            pixel = self.BOOTSTRAP[i % len(self.BOOTSTRAP)]
            self.image.putpixel(self.xy(), pixel)
            self.pos += 1

    def draw_header(self, data, name) -> None:
        self.pos = self.BOOTSTRAP_SIZE
        # [1px] version
        pixel = self.VERSION
        self.image.putpixel(self.xy(), pixel)
        self.pos += 1
        # [1px] width
        pixel = self.w
        self.image.putpixel(self.xy(), pixel)
        self.pos += 1
        # [1px] height
        pixel = self.h
        self.image.putpixel(self.xy(), pixel)
        self.pos += 1
        # [1px] data size (max 16777216)
        pixel = len(data)
        self.image.putpixel(self.xy(), pixel)
        self.pos += 1
        # [1px] checksum
        pixel = self.checksum(data)
        self.image.putpixel(self.xy(), pixel)
        self.pos += 1
        # [64px] name
        name_bytes = name.encode("utf-8")
        for i in range(self.NAME_LENGTH):
            if i < len(name_bytes):
                pixel = name_bytes[i]
            else:
                pixel = 0
            self.image.putpixel(self.xy(), pixel)
            self.pos += 1

    def draw_data(self, data) -> None:
        self.pos = self.BOOTSTRAP_SIZE + self.HEADER_SIZE
        for i in range(0, len(data), 3):
            rgb = data[i : i + 3]
            if len(rgb) < 3:
                rgb += bytes(3 - len(rgb))
            pixel = (rgb[0], rgb[1], rgb[2])
            self.image.putpixel(self.xy(), pixel)
            self.pos += 1

    def encode(
        self,
        data: bytes,
        name: str,
    ) -> Image:
        self.calculate_image_size(data)
        self.create_image()
        self.draw_bootstrap()
        self.draw_header(data, name)
        self.draw_data(data)
        return self.image
