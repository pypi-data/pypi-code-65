from typing import NamedTuple


Filesystem = NamedTuple('Filesystem', [
    ('id', int),
    ('name', str),
    ('fstype', str),
    ('ciphertextDirectory', str),
    ('plaintextDirectory', str)
])
