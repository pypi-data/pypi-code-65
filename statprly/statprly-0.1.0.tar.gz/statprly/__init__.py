"""
Top-level module for `Statprly` pattern recognition package.

This package interact with server and recognize a patterns.
"""
from statprly.mono_digits_recognizer.recognizer import MonoDigitRecognizer
from statprly.mono_digits_recognizer.standards_provider import StandardsProvider

__version__ = "0.1.0"
__version_info__ = tuple(int(i) for i in __version__.split(".") if i.isdigit())
