# Copyright 2020 John Lenton
# Licensed under GPLv3, see LICENSE file for details.

import sys

from unicodedata import normalize
from syltippy import syllabize

__all__ = ("geringoso",)
__version__ = "0.1.1"

_VOWELS = "aeiouAEIOUáéíóúÁÉÍÓÚ"
_CLOSED_VOWELS = "iuIU"  # non-accented

trans = str.maketrans("áéíóúÁÉÍÓÚ", "aeiouAEIOU")


def _pe(syl: str) -> str:
    if syl == "y":
        return "ipy"
    prev_gq = False
    for i, c in enumerate(syl):
        if c in "qgQG":
            prev_gq = True
            continue
        if prev_gq and c in "uU":
            prev_gq = False
            continue
        prev_gq = False
        if c in _VOWELS:
            i0 = i + 1
            if len(syl) > i0 and c in _CLOSED_VOWELS and syl[i0] in _VOWELS:
                i0 += 1
                i += 1
            p = "P" if syl[i].isupper() else "p"
            return syl[:i0] + p + syl[i:].translate(trans)
    # no vowels -> no extra pe
    return syl


def geringoso(word: str) -> str:
    syls, _ = syllabize(normalize("NFC", word))
    return "".join(_pe(syl) for syl in syls)


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        metavar="IN",
        help="Read input from this file",
        type=argparse.FileType("r"),
    )
    parser.add_argument(
        "-o",
        metavar="OUT",
        help="Write output to this file",
        type=argparse.FileType("w"),
        default=sys.stdout,
    )
    parser.add_argument("msg", nargs="*")
    args = parser.parse_args()
    if args.i is not None and args.msg:
        parser.error("cannot specify -i and also provide a message as argument")
    if args.i is None and not args.msg:
        if sys.stdin.isatty():
            print("\033[2mReading from standard input.\033[0m", file=sys.stderr)
        args.i = sys.stdin

    if args.i is None:
        print(" ".join(geringoso(word) for word in args.msg), file=args.o)
    else:
        for line in args.i:
            args.o.write(geringoso(line))


if __name__ == "__main__":

    main()
