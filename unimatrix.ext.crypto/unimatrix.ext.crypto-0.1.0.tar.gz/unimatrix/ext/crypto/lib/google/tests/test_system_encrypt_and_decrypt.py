# pylint: skip-file
import asyncio
import unittest

import unimatrix.lib.test

from ..decrypter import GoogleDecrypter
from ..encrypter import GoogleEncrypter
from . import environ


@unimatrix.lib.test.system
class EncryptAndDecryptTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.encrypter = GoogleEncrypter(
            project=environ.KMS_PROJECT,
            region=environ.KMS_REGION,
            keyring=environ.KMS_KEYRING,
            key=environ.KMS_ENCRYPTION_KEY
        )
        cls.decrypter = GoogleDecrypter(
            project=environ.KMS_PROJECT,
            region=environ.KMS_REGION,
            keyring=environ.KMS_KEYRING,
            key=environ.KMS_ENCRYPTION_KEY
        )

    def test_encrypt(self):
        blob = b'Hello world!'
        self.encrypter.encrypt(blob)

    def test_decrypt(self):
        pt = b'Hello world!'
        ct = self.encrypter.encrypt(pt)
        self.assertEqual(pt, self.decrypter.decrypt(ct))

    def test_async_encrypt(self):
        blob = b'Hello world!'
        asyncio.run(self.encrypter.async_encrypt(blob))

    def test_async_decrypt(self):
        pt = b'Hello world!'
        ct = asyncio.run(self.encrypter.async_encrypt(pt))
        self.assertEqual(pt, asyncio.run(self.decrypter.async_decrypt(ct)))
