# pylint: skip-file
import unittest

import unimatrix.lib.test

from unimatrix.ext.crypto.tests import BaseSymmetricKeyTestCase
from unimatrix.ext.crypto.lib import google
from . import environ


@unimatrix.lib.test.system
@unittest.skipIf(not environ.KMS_ENCRYPTION_OK, "Google KMS not configured.")
class SymmetricEncryptionTestCase(BaseSymmetricKeyTestCase, unittest.TestCase):
    backend_class = google.Backend

    def get_backend_kwargs(self):
        return {
            'params': {
                google.PARAM_PROJECT: environ.KMS_PROJECT,
                google.PARAM_LOCATION: environ.KMS_REGION,
                google.PARAM_KEYRING: environ.KMS_KEYRING,
                google.PARAM_KEY: environ.KMS_ENCRYPTION_KEY
            }
        }
