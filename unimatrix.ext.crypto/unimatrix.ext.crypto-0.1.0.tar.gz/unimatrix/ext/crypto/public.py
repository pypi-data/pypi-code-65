"""Declares :class:`PublicKey`."""
import abc


class PublicKey(metaclass=abc.ABCMeta):
    """Declares the interface for public key."""

    @abc.abstractmethod
    def verify(self, sig, buf, padding, algorithm):
        """Verifies that `sig` is a valid signature with this public
        key on `buf`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def encrypt(self, pt, *args, **kwargs):
        """Encrypt byte-sequence `pt` using the specified parameters."""
        raise NotImplementedError


def load_pem_public_key(buf):
    """Load byte-sequence `buf` holding a PEM-serialized PKCS#1 DER encoded
    public key as a :class:`PublicKey` instance.
    """
    from .lib.pkcs import PEMPublicKey
    return PEMPublicKey.frompem(buf)
