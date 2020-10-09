"""Declares :class:`GoogleSymmetricKey`."""
import base64

from gcloud.aio.kms import decode
from gcloud.aio.kms import encode

from ...symmetric import BaseSymmetricKey
from .base import GoogleKMSInvoker


class GoogleSymmetricKey(BaseSymmetricKey, GoogleKMSInvoker):
    """A symmetric encryption/decryption key managed by Google Cloud KMS."""

    async def async_decrypt(self, blob):
        """Asynchronously decrypt byte-sequence `blob` using the underlying
        decryption backend.
        """
        async with self._get_async_client() as kms:
            pt = str.replace(await kms.decrypt(blob), '-', '+')\
                .replace('_', '/')
        return base64.b64decode(pt)

    def decrypt(self, blob):
        """Decrypt byte-sequence `blob` using the underlying decryption backend."""
        response = self._google_kms.decrypt(
            request={
                'name': self._get_resource_id(),
                'ciphertext': blob
            }
        )
        return response.plaintext

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
