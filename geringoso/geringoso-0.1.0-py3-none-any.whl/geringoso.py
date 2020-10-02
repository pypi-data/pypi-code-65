# Copyright 2020 John Lenton
# Licensed under GPLv3, see LICENSE file for details.

import sys

from unicodedata import normalize
from syltippy import syllabize

__all__ = ('geringoso',)
__version__ = '0.1.0'

_VOWELS = 'aeiouAEIOUáéíóúÁÉÍÓÚ'
_CLOSED_VOWELS = 'iuIU'           # non-accented

trans = str.maketrans("áéíóúÁÉÍÓÚ", "aeiouAEIOU")

def _pe(syl: str) -> str:
    if syl == 'y':
        return 'ipy'
    prev_gq = False
    for i, c in enumerate(syl):
        if c in 'qgQG':
            prev_gq = True
            continue
        if prev_gq and c in 'uU':
            prev_gq = False
            continue
        prev_gq = False
        if c in _VOWELS:
            i0 = i+1
            if c in _CLOSED_VOWELS and syl[i+1:i+2] in _VOWELS:
                i0 += 1
                i += 1
            return syl[:i0] + 'p' + syl[i:].translate(trans)
    # no vowels -> no extra pe
    return syl

def geringoso(word: str) -> str:
    syls, _ = syllabize(normalize('NFC', word))
    return ''.join(_pe(syl) for syl in syls)

def main():
    print(" ".join(geringoso(word) for word in sys.argv[1:]))

if __name__ == '__main__':
    main()
