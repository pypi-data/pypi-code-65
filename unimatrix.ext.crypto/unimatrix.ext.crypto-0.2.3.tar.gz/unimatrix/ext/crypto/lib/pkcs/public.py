"""Declares :class:`PEMPublicKey`."""
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_public_key

from ...public import PublicKey


class PEMPublicKey(PublicKey):
    """A PKCS#1 public key. This basically wraps the :mod:`cryptography`
    public key implementations.
    """

    @classmethod
    def frompem(cls, buf):
        return cls(load_pem_public_key(buf, default_backend()))

    def __init__(self, key):
        self.key = key

    def encrypt(self, pt, padding):
        """Returns the cipher text of byte-sequence `pt`."""
        return self.key.encrypt(pt, padding)

    def verify(self, sig, buf, padding, algorithm):
        """Verifies that `sig` is a valid signature with this public
        key on `buf`.
        """
        return self.key.verify(sig, buf, padding, algorithm)
