"""Declares :class:`PKCSDecrypter`."""
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.padding import MGF1
from cryptography.hazmat.primitives.asymmetric.padding import OAEP

from ...decrypter import Decrypter
from .private import PKCSPrivateKey


class PKCSDecrypter(Decrypter):
    """Provides an interface to decrypt ciphertext. It can also
    encrypt (since it possesses the private key).
    """

    @property
    def mgf(self):
        """Return the mask generation function."""
        return MGF1(SHA256())

    @property
    def hashing(self):
        """Return the hashing algorithm."""
        return SHA256()

    @property
    def padding(self):
        """Return the padding used for encryption/decryption
        operations.
        """
        return OAEP(self.mgf, self.hashing, None)

    @classmethod
    def ephemeral(cls, size=4096):
        """Generate a new private key that is bound to the lifecycle
        of :class:`PKCSDecrypter`.
        """
        return cls(PKCSPrivateKey.generate(size))

    @classmethod
    def frompem(cls, fp, *args, **kwargs):
        """Return a new :class:`PKCSDecrypter` with its private key
        loaded from a PEM-encoded filepath `fp`.
        """
        return cls(PKCSPrivateKey.frompem(fp, *args, **kwargs))

    def __init__(self, key=None):
        self.__key = key

    def encrypt(self, pt):
        """Returns the cipher text of byte-sequence `pt`."""
        return self.__key.encrypt(pt, self.padding)

    def decrypt(self, ct):
        """Returns the plain text of byte-sequence `ct`."""
        return self.__key.decrypt(ct, self.padding)
