"""Declares :class:`PKCSPrivateKey`."""
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from ...private import PrivateKey
from .public import PEMPublicKey


class PKCSPrivateKey(PrivateKey):
    """Provides an interface for signing and decryption operations
    using the Public Key Cryptography Standard (PKCS).
    """

    @property
    def public(self):
        """Return the :mod:`unimatrix.ext.crypto.lib.pkcs.PKCSPublicKey`
        corresponding to the private key.
        """
        return PEMPublicKey(self.__key.public_key())

    @classmethod
    def frompem(cls, fp, password=None):
        """Return a new :class:`PKCSPrivateKey` with its private key
        loaded from a PEM-encoded filepath `fp`.
        """
        with open(fp, 'rb') as fd:
            key = serialization.load_pem_private_key(fd.read(),
                password=password, backend=default_backend())
        return cls(key)

    @classmethod
    def generate(cls, size=4096):
        """Generate a new private key."""
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=size,
            backend=default_backend()
        )
        return cls(key)

    def __init__(self, key):
        self.__key = key

    def encrypt(self, pt, padding):
        """Returns the cipher text of byte-sequence `pt`."""
        return self.public.encrypt(pt, padding)

    def decrypt(self, ct, padding):
        """Returns the plain text of byte-sequence `ct`."""
        return self.__key.decrypt(bytes(ct), padding)
