#!/usr/bin/env python3

import re
import sys


__version__ = "0.0.1"
__description__ = "Multilingual sentence segmentation tool"

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?", type=argparse.FileType("r"), default=sys.stdin)
    args = parser.parse_args()

    for line in args.file:
        segments = re.split(r"([\.\?\!])", line)
        for i in range(0, len(segments), 2):
            segment = "".join(segments[i:i+2]).strip()
            print(segment)


if __name__ == "__main__":
    main()
