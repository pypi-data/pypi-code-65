"""Declares :class:`GoogleSigner`."""
import hashlib

from ...public import load_pem_public_key
from ...signer import Signer
from .base import GoogleKMSInvoker
from .signature import GoogleSignature


class GoogleSigner(Signer, GoogleKMSInvoker):

    @property
    def kms_key(self):
        """Return the KMS public key response."""
        if not getattr(self, '_kms_key', None):
            self._kms_key = self._google_kms.get_public_key(
                request={'name': self._get_resource_id()})
        return self._kms_key

    @property
    def public(self):
        """Return the public key loaded from :attr:`kms_key`."""
        return load_pem_public_key(str.encode(self.kms_key.pem))

    @property
    def algorithm(self):
        """Returns a string holding an OID, identifying the algorithm
        that the signer uses.
        """
        return self._crypto_mapping[self.kms_key.algorithm]

    def sign(self, buf, **kwargs):
        """Invoke the Google KMS API to sign byte-sequence `buf`."""
        # This will support only EC_SIGN_P256_SHA256, RSA_SIGN_PSS_2048_SHA256,
        # RSA_SIGN_PSS_3072_SHA256, RSA_SIGN_PSS_4096_SHA256,
        # RSA_SIGN_PKCS1_2048_SHA256, RSA_SIGN_PKCS1_3072_SHA256 and
        # RSA_SIGN_PKCS1_4096_SHA256 for now.
        h = hashlib.sha256(buf)
        request = {
            'name': self._get_resource_id(),
            'digest': {
                'sha256': h.digest()
            }
        }
        response = self._google_kms.asymmetric_sign(**request)

        # TODO: Error handling
        return GoogleSignature(response.signature, self.algorithm)
