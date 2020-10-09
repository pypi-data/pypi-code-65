"""Declares :class:`GoogleDecrypter`."""
import base64

from gcloud.aio.kms import decode

from ...decrypter import Decrypter
from .base import GoogleKMSInvoker


class GoogleDecrypter(Decrypter, GoogleKMSInvoker):
    """Provides an interface to decrypt using Google Cloud KMS."""

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
