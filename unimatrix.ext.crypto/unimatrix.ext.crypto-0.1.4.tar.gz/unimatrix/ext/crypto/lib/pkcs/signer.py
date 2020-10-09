"""Declares :class:`PKCSSigner`."""
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from ...const import OID_MAPPING
from ...signer import Signer
from ...signature import Signature
from .public import PEMPublicKey


class PKCSSigner(Signer):

    @property
    def public(self):
        """Returns a :class:`unimatrix.ext.crypto.PublicKey` implementation
        that can verify the signatures produced by this signer.
        """
        return PEMPublicKey(self.__key.public_key())

    @property
    def algorithm(self):
        """Returns a string holding an OID, identifying the algorithm
        that the signer uses.
        """
        return self.__algorithm

    def __init__(self, key, algorithm):
        self.__key = load_pem_private_key(open(key, 'rb').read(),
            None, default_backend())
        self.__algorithm = algorithm
        if self.__algorithm not in OID_MAPPING:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        self.__padding, self.__hashing = OID_MAPPING[algorithm]

    def sign(self, buf, **kwargs):
        """Use the private key of the signer to sign the given data."""
        return Signature(self.__key.sign(buf, self.__padding, self.__hashing),
            self.algorithm)
