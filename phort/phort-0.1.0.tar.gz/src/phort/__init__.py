#!/usr/bin/env python3
"""
A command line tool to sort photos for the family.
"""
import argparse
import sys

from . import phort


def main(argv=None):
    if argv is None:
        argv = sys.argv
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-v", "--verbose", action="count", help="increase output verbosity"
    )
    parser.add_argument(
        "-m",
        "--move",
        action="store_true",
        help="moves files instead of copying - this is non-reversible, use with care",
    )
    args = parser.parse_args(argv[1:])
    try:
        phort.run(args)
    except KeyboardInterrupt:
        sys.exit(-1)


if __name__ == "__main__":
    sys.exit(main(sys.argv) or 0)
