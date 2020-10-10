# pylint: skip-file
import unittest

import unimatrix.lib.test

from unimatrix.ext.crypto.tests import BaseSymmetricKeyTestCase
from unimatrix.ext.crypto.lib import null


@unimatrix.lib.test.integration
class SymmetricEncryptionTestCase(BaseSymmetricKeyTestCase, unittest.TestCase):
    backend_class = null.Backend

    def get_backend_kwargs(self):
        return {'params': {}}
