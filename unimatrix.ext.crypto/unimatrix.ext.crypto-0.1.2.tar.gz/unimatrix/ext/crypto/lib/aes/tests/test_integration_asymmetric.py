# pylint: skip-file
import unittest

import unimatrix.lib.test
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from unimatrix.ext.crypto.tests import BaseSymmetricKeyTestCase
from unimatrix.ext.crypto.lib import aes


@unimatrix.lib.test.integration
class SymmetricEncryptionTestCase(BaseSymmetricKeyTestCase, unittest.TestCase):
    backend_class = aes.Backend

    def get_backend_kwargs(self):
        return {'key': AESGCM.generate_key(256)}
