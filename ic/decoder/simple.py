from PIL import Image

from ..coder.base import FormatV1
from .base import Decoder


class SimpleDecoder(FormatV1, Decoder):

    def __init__(self, image=None, *args, **kwargs):
        if isinstance(image, Image.Image):
            self.image = image
        elif isinstance(image, str):
            self.image = Image.open(image)
        else:
            raise ValueError("invalid image type")
        self.w, self.h = self.image.size

    def xy(self, p: int) -> tuple[int, int]:
        return (p % self.w, p // self.w)

    def getpx(self, p) -> int:
        x, y = self.xy(p)
        r, g, b = self.image.getpixel((x, y))
        return r + g * 256 + b * 65536

    def check_bootstrap(self):
        for i in range(self.BOOTSTRAP_SIZE):
            ipx = self.getpx(i)
            bpx = self.BOOTSTRAP[i % len(self.BOOTSTRAP)]
            if ipx != bpx:
                raise ValueError(f"Invalid bootstrap data {ipx:#06X} != {bpx:#06X}")
        return True

    def read_header(self):
        p = self.BOOTSTRAP_SIZE
        # [1px] version
        px = self.getpx(p)
        if px != self.VERSION:
            raise ValueError("Invalid version")
        p += 1

        # [1px] width
        px = self.getpx(p)
        assert px == self.w, f"Invalid width: {px} != {self.w}"
        p += 1

        # [1px] height
        px = self.getpx(p)
        assert px <= self.h, f"Invalid height: {px} != {self.h}"
        p += 1

        # [1px] data size (max 16777216)
        px = self.getpx(p)
        data_len = px
        p += 1

        # [1px] checksum
        px = self.getpx(p)
        checksum = px
        p += 1

        # [64px] name
        name = bytes()
        for i in range(64):
            px = self.getpx(p)
            if px == 0:
                break
            name += px.to_bytes(1, "big")
            p += 1

        return data_len, name.decode("utf-8"), checksum

    def read_data(self, data_len):
        p = self.BOOTSTRAP_SIZE + self.HEADER_SIZE
        data = []
        for i in range(data_len // 3 + 1):
            r, g, b = self.image.getpixel(self.xy(p))
            data.append(r.to_bytes(1, "big"))
            data.append(g.to_bytes(1, "big"))
            data.append(b.to_bytes(1, "big"))
            p += 1
        data = b"".join(data)[:data_len]
        return data

    def check_checksum(self, data, checksum):
        if sum(data) % (2**24) != checksum:
            raise ValueError(f"Invalid checksum {sum(data) % (2**24)} != {checksum}")
        return True

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
        print(f"found bootstrap at {(x0, y0)} ({p})")
        if x0 == -1:
            raise ValueError("no bootstrap found")
        v, w, h = self.read_header(p)
        h += 1
        print(f"header data: {(v, w, h)}")
        assert v == self.VERSION, f"Invalid version: {v} != {self.VERSION}"
        print(f"cropping {self.w}x{self.h} → {w}x{h}+({x0},{y0})")
        self.image = self.image.crop((x0, y0, x0 + w, y0 + h))

    def find_bootstrap(self):
        p = 0
        f = 0
        for x in range(self.w):
            for y in range(self.h):
                ipx = self.getpx(p)
                if ipx != self.BOOTSTRAP[f % len(self.BOOTSTRAP)]:
                    p += 1
                    f = 0
                    continue
                f += 1
                p += 1
                if f == self.BOOTSTRAP_SIZE:
                    p0 = p - self.BOOTSTRAP_SIZE
                    x0 = p0 % self.w
                    y0 = p0 // self.w
                    return x0, y0, p
        return -1, -1, -1

    def read_header(self, p):

        # [1px] version
        version = self.getpx(p)
        p += 1

        # [1px] width
        w = self.getpx(p)
        p += 1

        # [1px] height
        h = self.getpx(p)
        p += 1

        return version, w, h
