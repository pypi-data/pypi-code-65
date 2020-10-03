"""
A package with a set of types that can be used independently as extension of basic python types
"""

from .implementation.mutable import *

__all__ = [
    'MBoolean',
    'MInteger',
    'MFloat',
    'MString',
]