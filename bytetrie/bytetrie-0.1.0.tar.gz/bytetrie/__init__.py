"""
Bytetrie
========
A fast, dependency-free implementation of a compressed trie with radix 256.

Bytetrie allows fast prefix search in a large corpus of keys. Each key can
be associated with arbitrary data. The fast lookup times come at the cost of
expensive insertion. A Bytetrie is best used if it can be pre-loaded with data.

Keys and Data
-------------
Keys are byte strings. Therefore, each node in the trie can have up to 256
children. Keys do work well with utf-8 and other encodings as long as the
encoding is consistent and deterministic. I.e. a certain grapheme clusters is
always encoded to the same byte sequence. Every key can be associated with
arbitrary data. Multi-valued bytetries allow to associate a sequence of
arbitrary data with every key. Order is not guaranteed.

Usage
-----
.. code :: python
    t = ByteTrie()
    t.add(b"Hello", "P1")
    t.add(b"Hi", "P2")
    t.add(b"Hela", "P3")
    t.find(b"He") # ["P1", "P3"]
"""

from .bytetrie import ByteTrie
