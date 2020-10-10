# pylint: skip-file
import os
import unittest

#from ..encrypter import PKCSEncrypter
from ..decrypter import PKCSDecrypter


class EncryptAndDecryptTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.decrypter = PKCSDecrypter.frompem(
            os.path.join(os.path.dirname(__file__), 'key.rsa'))

    def test_encrypt_exits_succesfully(self):
        self.decrypter.encrypt(b'Hello world!')

    def test_decrypt_from_encrypt(self):
        pt = b'Hello world!'
        ct = self.decrypter.encrypt(pt)
        self.assertEqual(self.decrypter.decrypt(ct), pt)

    def test_ephemeral_decrypter(self):
        decrypter = PKCSDecrypter.ephemeral(1024)

        pt = b'Hello world!'
        ct = decrypter.encrypt(pt)
        self.assertEqual(decrypter.decrypt(ct), pt)
