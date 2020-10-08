# pylint: skip-file
import hashlib
import os
import unittest

from ....const import RSA_PKCS1_SHA256
from ..signer import PKCSSigner


class SignAndVerifyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.signer = PKCSSigner(
            key=os.path.join(os.path.dirname(__file__), 'key.rsa'),
            algorithm=RSA_PKCS1_SHA256
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
