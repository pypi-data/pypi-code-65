# pylint: skip-file
import hashlib
import os
import unittest

from ..signer import GoogleSigner
from . import environ


@unittest.skipIf(not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'),
    "GOOGLE_APPLICATION_CREDENTIALS not set.")
@unittest.skipIf(not environ.KMS_SIGNING_OK, "Google KMS not configured.")
class SignAndVerifyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.signer = GoogleSigner(
            project=environ.KMS_PROJECT,
            region=environ.KMS_REGION,
            keyring=environ.KMS_KEYRING,
            key=environ.KMS_SIGNING_KEY,
            version=environ.KMS_SIGNING_KEY_VERSION
        )

    def setUp(self):
        self.buf = os.urandom(256)

    def test_sign_random_data(self):
        """Test if ``sign()`` exits succesfully."""
        sig = self.signer.sign(self.buf)

    def test_sign_random_data_and_verify(self):
        """Test if ``sign()`` exits succesfully and the data may be succesfully
        verified using the public key of the signer.
        """
        sig = self.signer.sign(self.buf)
        self.assertTrue(sig.verify(self.signer.public, self.buf))

    def test_sign_random_data_and_verify_prehashed(self):
        """Test if ``sign()`` exits succesfully and the prehashed data may be
        succesfully verified using the public key of the signer.
        """
        sig = self.signer.sign(self.buf)
        self.assertTrue(sig.verify(self.signer.public,
            hashlib.sha256(self.buf).digest(), prehashed=True))

    def test_sign_random_data_and_verify_with_random_data(self):
        """Test if ``sign()`` exits succesfully and the data is not succesfully
        verified with new random data.
        """
        sig = self.signer.sign(self.buf)
        self.assertFalse(sig.verify(self.signer.public, os.urandom(256)))

    def test_sign_random_data_and_verify_with_random_data_prehashed(self):
        """Test if ``sign()`` exits succesfully and the prehashed data is
        not succesfully verified with new random data.
        """
        sig = self.signer.sign(self.buf)
        self.assertFalse(sig.verify(self.signer.public,
            hashlib.sha256(os.urandom(256)).digest(), prehashed=True))
