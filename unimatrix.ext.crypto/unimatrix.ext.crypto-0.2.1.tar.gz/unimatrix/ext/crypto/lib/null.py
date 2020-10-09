"""A :class:`~unimatrix.ext.crypto.BaseBackend` implementation that does
not encrypt.
"""
from ..ciphertext import CipherText
from .backend import BaseBackend


class NullKey:
    """A key implementation that does nothing."""

    async def async_decrypt(self, ct):
        """Asynchronously decrypt :class:`CipherText` `ct` using the underlying
        decryption backend.
        """
        return bytes(ct)

    async def async_encrypt(self, pt):
        """Asynchronously encrypt byte-sequence `pt` using the underlying
        encryption backend.
        """
        return CipherText(pt)

    def decrypt(self, ct):
        """Decrypt :class:`CipherText` `ct` using the underlying decryption
        backend.
        """
        return bytes(ct)

    def encrypt(self, pt):
        """Encrypt byte-sequence `pt` using the underlying encryption backend."""
        return CipherText(pt)


class Backend(BaseBackend):
    """A backend implementation that does nothing."""
    capabilities = [
        'encrypt',
        'encrypt:async',
        'decrypt',
        'decrypt:async'
    ]

    def __init__(self, params):
        self.__params = params

    def symmetric(self):
        """Return the :class:`~unimatrix.ext.crypto.SymmetricKey`
        implementation for this backend.
        """
        return NullKey()
