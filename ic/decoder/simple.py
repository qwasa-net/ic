from pathlib import Path

from PIL import Image

from ..coder.base import FormatV1
from .base import Decoder


class SimpleDecoder(FormatV1, Decoder):

    def __init__(
        self,
        image: Image.Image | str | Path,
        *args,
        **kwargs,
    ):
        if isinstance(image, Image.Image):
            self.image = image
        elif isinstance(image, (str, Path)):
            self.image = Image.open(image)
        else:
            raise ValueError("invalid image type")
        self.w, self.h = self.image.size
        self.pos = 0

    def xy(self, p: int | None = None) -> tuple[int, int]:
        p = self.pos if p is None else p
        return (p % self.w, p // self.w)

    def getpx(self, p: int | None = None) -> int:
        x, y = self.xy(p)
        r, g, b = self.image.getpixel((x, y))
        return r + g * (2**8) + b * (2**16)

    def check_bootstrap(self):
        self.pos = 0
        for i in range(self.BOOTSTRAP_SIZE):
            ipx = self.getpx()
            bpx = self.BOOTSTRAP[i % len(self.BOOTSTRAP)]
            if ipx != bpx:
                raise ValueError(f"Invalid bootstrap data {ipx:#06X} != {bpx:#06X}")
            self.pos += 1
        return True

    def read_header(self):
        self.pos = self.BOOTSTRAP_SIZE
        # [1px] version
        px = self.getpx()
        if px != self.VERSION:
            raise ValueError("Invalid version")
        self.pos += 1
        # [1px] width
        px = self.getpx()
        assert px == self.w, f"Invalid width: {px} != {self.w}"
        self.pos += 1
        # [1px] height
        px = self.getpx()
        assert px <= self.h, f"Invalid height: {px} != {self.h}"
        self.pos += 1
        # [1px] data size (max 16777216)
        px = self.getpx()
        data_len = px
        self.pos += 1
        # [1px] checksum
        px = self.getpx()
        checksum = px
        self.pos += 1
        # [64px] name
        name = bytes()
        for i in range(self.NAME_LENGTH):
            px = self.getpx()
            if px == 0:
                break
            name += px.to_bytes(1, "big")
            self.pos += 1
        return data_len, name.decode("utf-8"), checksum

    def read_data(self, data_len):
        self.pos = self.BOOTSTRAP_SIZE + self.HEADER_SIZE
        data = []
        for i in range(data_len // 3 + 1):
            rgb = self.image.getpixel(self.xy())
            for c in rgb:
                data.append(c.to_bytes(1, "big"))
            self.pos += 1
        data = b"".join(data[:data_len])
        return data

    def check_checksum(self, data, checksum):
        data_sum = self.checksum(data)
        if data_sum == checksum:
            return True
        raise ValueError(f"Invalid checksum {data_sum} != {checksum} {len(data)=}")

    def decode(self) -> tuple[bytes, str]:
        self.check_bootstrap()
        length, name, checksum = self.read_header()
        print(f"header: {length} bytes, name: `{name}`, checksum: `{checksum}`")
        data = self.read_data(length)
        self.check_checksum(data, checksum)
        return data, name


class SimpleAutoCropper(SimpleDecoder):

    def autocrop(self):
        x0, y0, p = self.find_bootstrap()
        if x0 == -1:
            raise ValueError("no bootstrap found")
        v, w, h = self.read_header(p)
        h += 1
        print(f"found bootstrap at +{x0}+{y0} (@{p}), header data: v{v} {w}×{h}")
        assert v == self.VERSION, f"Invalid version: {v} != {self.VERSION}"
        print(f"cropping {self.w}x{self.h} → {w}x{h}+({x0},{y0})")
        return self.image.crop((x0, y0, x0 + w, y0 + h))

    def find_bootstrap(self):
        pos = 0
        found_count = 0
        for x in range(self.w):
            for y in range(self.h):
                ipx = self.getpx(pos)
                if ipx != self.BOOTSTRAP[found_count % len(self.BOOTSTRAP)]:
                    pos += 1
                    found_count = 0
                    continue
                found_count += 1
                pos += 1
                if found_count == self.BOOTSTRAP_SIZE:
                    p0 = pos - self.BOOTSTRAP_SIZE
                    x0 = p0 % self.w
                    y0 = p0 // self.w
                    return x0, y0, pos
        return -1, -1, -1

    def read_header(self, pos: int):
        # [1px] version
        version = self.getpx(pos)
        pos += 1
        # [1px] width
        w = self.getpx(pos)
        pos += 1
        # [1px] height
        h = self.getpx(pos)
        pos += 1
        return version, w, h
