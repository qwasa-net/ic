import argparse

from .coder.simple import SimpleCoder
from .decoder.simple import SimpleAutoCropper, SimpleDecoder


def parse_args():
    parser = argparse.ArgumentParser(description="data→image|image→data")
    parser.add_argument(
        "-w",
        "--width",
        type=int,
        default=1024,
    )
    parser.add_argument(
        "-d",
        "--decode",
        action="store_true",
    )
    parser.add_argument(
        "-a",
        "--autocrop",
        action="store_true",
        default=False,
    )
    parser.add_argument("infile")
    parser.add_argument("outfile", nargs="?")
    return parser.parse_args()


def main():

    args = parse_args()
    print(args)

    if args.decode:
        decode(args)
    else:
        encode(args)


def encode(args):
    coder = SimpleCoder(args.width)
    data = open(args.infile, "rb").read()
    image = coder.encode(data, args.infile)
    if args.outfile is None:
        args.outfile = args.infile + ".png"
    image.save(args.outfile, "PNG")
    w, h = image.size
    print(f"encoded: {len(data)} bytes to `{args.outfile}` ({w}x{h})")


def decode(args):
    if args.autocrop:
        cropper = SimpleAutoCropper(args.infile)
        cropper.autocrop()
        decoder = SimpleDecoder(cropper.image)
    else:
        decoder = SimpleDecoder(args.infile)
    data, name = decoder.decode()
    if args.outfile is not None:
        name = args.outfile
    open(name, "wb").write(data)
    print(f"decoded: {len(data)} bytes to `{name}`")


if __name__ == "__main__":
    main()
