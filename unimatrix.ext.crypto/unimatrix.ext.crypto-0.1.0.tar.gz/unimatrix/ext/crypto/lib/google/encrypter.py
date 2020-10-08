"""Declares :class:`GoogleEncrypter`."""
from gcloud.aio.kms import encode

from ...encrypter import Encrypter
from .base import GoogleKMSInvoker


class GoogleEncrypter(Encrypter, GoogleKMSInvoker):
    """Provides an interface to encrypt using Google Cloud KMS."""

    async def async_encrypt(self, blob):
        """Asynchronously encrypt byte-sequence `blob` using the underlying
        encryption backend.
        """
        async with self._get_async_client() as kms:
            return await kms.encrypt(encode(blob))

    def encrypt(self, blob):
        """Encrypt byte-sequence `blob` using the underlying encryption backend."""
        response = self._google_kms.encrypt(
            request={
                'name': self._get_resource_id(),
                'plaintext': blob
            }
        )
        return response.ciphertext
