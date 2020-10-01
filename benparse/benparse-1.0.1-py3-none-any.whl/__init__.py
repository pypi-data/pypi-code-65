"""Bencode parser

benparse is a bencode parser for Python 3. It is capable of reading
and creating `bencoded files <https://en.wikipedia.org/wiki/Bencode>`_
such as torrents
"""

__all__ = [
    'dump', 'dumps',
    'load', 'loads', 'Delimiter', 'StrictError'
]

from .dump import dump, dumps
from .load import load, loads, Delimiter, StrictError
