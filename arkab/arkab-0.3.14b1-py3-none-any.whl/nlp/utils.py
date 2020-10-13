from typing import Tuple
import unicodedata
import string
import math

__all__ = ['unicode_to_ascii']


# Turn a Unicode string to plain ASCII, thanks to https://stackoverflow.com/a/518232/2809427
def unicode_to_ascii(s):
    all_letters = string.ascii_letters + " .,;'"
    return ''.join(
            c for c in unicodedata.normalize('NFD', s)
            if unicodedata.category(c) != 'Mn'
            and c in all_letters
    )
