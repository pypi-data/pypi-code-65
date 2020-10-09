"""Provides encryption and decryption using the Advanced Encryption
Standard (AES).
"""
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from ..backend import BaseBackend
from .symmetric import AdvancedEncryptionStandardSymmetricKey


class Backend(BaseBackend):
    """Provides an interface to construct, generate or persist AES
    keys.
    """
    capabilities = [
        'encrypt',
        'decrypt',
        'generate:symmetric'
    ]

    @classmethod
    def generate(cls, length=256):
        """Generate a new key and instantiate a backend with it."""
        return cls(AESGCM.generate_key(length))

    def __init__(self, key):
        """Initialize a new :class:`AESBackend` instance.

        Args:
            key (:class:`bytes`): a byte-sequence holding a 128, 192 or
                256 bits AES key.
        """
        self.__key = AdvancedEncryptionStandardSymmetricKey(key)

    def symmetric(self):
        """Return the :class:`~unimatrix.ext.crypto.SymmetricKey`
        implementation for this backend.
        """
        return self.__key
