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

    def calculate_image_size(self, data: bytes) -> tuple[int, int]:
        total_len = (len(data) // 3) + 1 + self.HEADER_SIZE + self.BOOTSTRAP_SIZE
        if self.h is None:
            self.h = total_len // self.w
        return self.w, self.h + 1

    def xy(self, p: int) -> tuple[int, int]:
        return (p % self.w, p // self.w)

    def draw_bootstrap(self, image: Image) -> None:
        p = 0
        for i in range(self.BOOTSTRAP_SIZE):
            pixel = self.BOOTSTRAP[i % len(self.BOOTSTRAP)]
            image.putpixel(self.xy(p), pixel)
            p += 1
        return self.BOOTSTRAP_SIZE

    def draw_header(self, image, data, name, p) -> None:
        # [1px] version
        pixel = self.VERSION
        image.putpixel(self.xy(p), pixel)
        p += 1

        # [1px] width
        pixel = self.w
        image.putpixel(self.xy(p), pixel)
        p += 1

        # [1px] height
        pixel = self.h
        image.putpixel(self.xy(p), pixel)
        p += 1

        # [1px] data size (max 16777216)
        pixel = len(data)
        image.putpixel(self.xy(p), pixel)
        p += 1

        # [1px] checksum
        pixel = sum(data) % (2**24)
        image.putpixel(self.xy(p), pixel)
        p += 1

        # [64px] name
        name_bytes = name.encode("utf-8")
        for i in range(64):
            if i < len(name_bytes):
                pixel = name_bytes[i]
            else:
                pixel = 0
            image.putpixel(self.xy(p), pixel)
            p += 1

        return self.BOOTSTRAP_SIZE + self.HEADER_SIZE

    def draw_data(self, image, data, p) -> None:
        for i in range(0, len(data), 3):
            t3 = data[i : i + 3]
            r = t3[0] if len(t3) > 0 else 0
            g = t3[1] if len(t3) > 1 else 0
            b = t3[2] if len(t3) > 2 else 0
            pixel = (r, g, b)
            image.putpixel(self.xy(p), pixel)
            p += 1
        return p

    def encode(
        self,
        data: bytes,
        name: str,
    ) -> Image:
        """Encode data as bytes."""
        w, h = self.calculate_image_size(data)
        image = Image.new("RGB", (w, h))
        p = self.draw_bootstrap(image)
        p = self.draw_header(image, data, name, p)
        p = self.draw_data(image, data, p)
        return image
