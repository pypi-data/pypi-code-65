"""Automatically deserialize complex objects from simple Python types."""

import pkg_resources

from .errors import DeserializationError, DeserializerFactoryError
from .terramare import deserialize_into

# Attempt to expose the package version as __version__ (see PEP 396).
try:
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:  # pragma: no cover
    pass


__all__ = ["DeserializationError", "DeserializerFactoryError", "deserialize_into"]
