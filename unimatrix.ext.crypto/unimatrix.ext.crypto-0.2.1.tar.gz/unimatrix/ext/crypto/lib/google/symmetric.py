"""Declares :class:`GoogleSymmetricKey`."""
import base64

from gcloud.aio.kms import decode
from gcloud.aio.kms import encode

from ...ciphertext import CipherText
from ...symmetric import BaseSymmetricKey
from .base import GoogleKMSInvoker


class GoogleSymmetricKey(BaseSymmetricKey, GoogleKMSInvoker):
    """A symmetric encryption/decryption key managed by Google Cloud KMS."""

    async def async_decrypt(self, ct):
        """Asynchronously decrypt :class:`CipherText` `ct` using the underlying
        decryption backend.
        """
        blob = bytes.decode(base64.b64encode(bytes(ct)))
        async with self._get_async_client() as kms:
            pt = str.replace(await kms.decrypt(blob), '-', '+')\
                .replace('_', '/')
        return base64.b64decode(pt)

    async def async_encrypt(self, blob):
        """Asynchronously encrypt byte-sequence `blob` using the underlying
        encryption backend.
        """
        async with self._get_async_client() as kms:
            ct = CipherText(base64.b64decode(await kms.encrypt(encode(blob))))
        ct.update_annotations({
            'crypto.unimatrixone.io/backend': "unimatrix.ext.crypto.lib.google",
            'cloudkms.googleapis.com/resource-id': self._get_resource_id()
        })
        return ct

    def decrypt(self, blob):
        """Decrypt byte-sequence `blob` using the underlying decryption backend."""
        response = self._google_kms.decrypt(
            request={
                'name': self._get_resource_id(),
                'ciphertext': bytes(blob)
            }
        )
        return response.plaintext

    def encrypt(self, blob):
        """Encrypt byte-sequence `blob` using the underlying encryption backend."""
        response = self._google_kms.encrypt(
            request={
                'name': self._get_resource_id(),
                'plaintext': blob
            }
        )
        ct =  CipherText(response.ciphertext)
        ct.update_annotations({
            'crypto.unimatrixone.io/backend': "unimatrix.ext.crypto.lib.google",
            'cloudkms.googleapis.com/resource-id': self._get_resource_id()
        })
        return ct
