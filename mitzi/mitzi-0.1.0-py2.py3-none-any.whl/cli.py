"""Console script for mitzi."""
import argparse
import sys
from mitzi import presets


def main():
    """Console script for mitzi."""
    parser = argparse.ArgumentParser()
    parser.add_argument('_', nargs='*')

    parser.add_argument('--width', default=512, type=int)
    parser.add_argument('--height', default=512, type=int)
    parser.add_argument('--warp', default='#ffffff', type=str)
    parser.add_argument('--weft', default='#000000', type=str)
    parser.add_argument('--threadwidth', default=1, type=int)
    parser.add_argument('--preset', default='check', type=str)


    args = parser.parse_args()
    img = presets[args.preset](
        args.warp, args.weft, args.threadwidth, (args.width, args.height)
    )

    img.save(sys.stdout.buffer, format="PNG")

    print("Arguments: " + str(args._))
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
