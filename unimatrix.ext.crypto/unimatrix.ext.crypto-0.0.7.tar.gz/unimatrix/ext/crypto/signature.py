"""Declares :class:`Signature`."""
import abc

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed

from .const import OID_MAPPING


class Signature(metaclass=abc.ABCMeta):
    """Provides the interface for digital signatures."""

    def __init__(self, buf, algorithm):
        self.__data = buf
        self.__algorithm = algorithm
        if self.__algorithm not in OID_MAPPING:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        self.__padding, self.__hashing = OID_MAPPING[algorithm]

    def to_bytes(self):
        """Return a binary representation of the signature."""
        return self.__data

    def verify(self, key, data, prehashed=False):
        """Verifies the :class:`Signature` using the given public key
        `key`.
        """
        try:
            key.verify(bytes(self), data, self.__padding,
                self.__hashing if not prehashed else Prehashed(self.__hashing))
            return True
        except InvalidSignature:
            return False

    def __bytes__(self):
        return self.to_bytes()
