"""Declares :class:`Signer`."""
import abc


class Signer(metaclass=abc.ABCMeta):
    """Declares the mandatory interface for all :class:`Signer`
    implementations.
    """

    @abc.abstractmethod
    def sign(self, buf, algorithm=None):
        """Signs byte-sequence `buf` and returns a byte-sequence holding the
        signature.

        Args:
            buf (bytes): the data to be signed.
            algorithm: an instruction for the signer on the algorithm to use.
        """
        raise NotImplementedError

    @abc.abstractproperty
    def public(self):
        """Returns a :class:`unimatrix.ext.crypto.PublicKey` implementation
        that can verify the signatures produced by this signer.
        """
        raise NotImplementedError

    @abc.abstractproperty
    def algorithm(self):
        """Returns a string holding an OID, identifying the algorithm
        that the signer uses.
        """
        raise NotImplementedError
