"""Declares :class:`PrivateKey`."""
import abc


class PrivateKey(metaclass=abc.ABCMeta):
    """Provides an interface for signing and decryption
    operations.
    """

    @abc.abstractmethod
    def encrypt(self, buf, padding):
        """Returns the cipher text of byte-sequence `buf`."""
        raise NotImplementedError

    @abc.abstractmethod
    def decrypt(self, buf, padding):
        """Returns the plain text of byte-sequence `buf`."""
        raise NotImplementedError
