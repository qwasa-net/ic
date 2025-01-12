import argparse

from .coder.simple import SimpleCoder
from .decoder.simple import SimpleAutoCropper, SimpleDecoder


def parse_args():
    parser = argparse.ArgumentParser(description="data→image|image→data")
    parser.add_argument(
        "-w",
        "--width",
        type=int,
        default=2400,
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
    parser.add_argument(
        "-s",
        "--split",
        type=int,
        default=5 * 1024 * 1024,
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
    datas = []
    for i in range(0, len(data), args.split):
        datas.append(data[i : i + args.split])
    for i, data in enumerate(datas):
        image = coder.encode(data, args.infile)
        outfile = args.outfile or f"{args.infile}-{i:03d}.png"
        image.save(outfile, "PNG")
        w, h = image.size
        print(f"encoded: {len(data)} bytes to `{outfile}` ({w}x{h})")


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
