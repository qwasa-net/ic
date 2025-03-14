import argparse
import os

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
        "-b",
        "--base-filename",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-bp",
        "--base-filepath",
        action="store_true",
        default=False,
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
    parser.add_argument(
        "-x",
        "--xor",
        type=str,
        default=None,
    )
    parser.add_argument(
        "-xm",
        "--xor-magic",
        action="store_true",
        default=False,
    )
    parser.add_argument("infile")
    parser.add_argument("outfile", nargs="?")

    args, _ = parser.parse_known_args()

    if args.xor_magic:
        args.xor = b"".join([bytes([i]) for i in range(256)])
    if isinstance(args.xor, str):
        args.xor = args.xor.encode("utf-8")

    return args


def main():

    args = parse_args()
    print(args)

    if args.decode:
        decode(args)
    else:
        encode(args)


def encode(args, img_type="PNG"):
    datas = read_data_chunks(args)
    for i, data in enumerate(datas):
        coder = SimpleCoder(w=args.width)
        image = coder.encode(data, args.infile)
        outfile = args.outfile or f"{args.infile}-{i:03d}.{img_type.lower()}"
        image.save(outfile, format=img_type)
        w, h = image.size
        print(f"encoded: {len(data)} bytes to `{outfile}` ({w}x{h})")


def decode(args):
    if args.autocrop:
        cropper = SimpleAutoCropper(args.infile)
        image = cropper.autocrop()
    else:
        image = args.infile
    decoder = SimpleDecoder(image)
    data, name = decoder.decode()
    data = xor_bunny_boyz(data, args.xor)
    outfile = args.outfile or name
    infile_dir = os.path.dirname(args.infile)
    if args.base_filepath:  # /path/to/file.ext -> path_to_file.ext
        outfile_paths = os.path.normpath(outfile).split(os.sep)
        outfile_filename = "_".join(outfile_paths[-5:]).strip("_")
        outfile = os.path.join(infile_dir, outfile_filename)
    elif args.base_filename:  # /path/to/file.ext -> file.ext
        outfile_filename = os.path.basename(outfile)
        outfile = os.path.join(infile_dir, outfile_filename)
    open(outfile, "wb").write(data)
    print(f"decoded: {len(data)} bytes of `{name}` to `{outfile}`")


def read_data_chunks(args):
    datas = []
    with open(args.infile, "rb") as infile:
        while chunk := infile.read(args.split):
            data = xor_bunny_boyz(chunk, args.xor)
            datas.append(data)
    return datas


def xor_bunny_boyz(data, xor):
    if not xor:
        return data
    xdata = bytearray(data)
    for i in range(len(data)):
        xdata[i] ^= xor[i % len(xor)]
    return bytes(xdata)


if __name__ == "__main__":
    main()
