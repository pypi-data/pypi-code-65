# pylint: skip-file
import hashlib
import io
import tempfile

import ioc
import unimatrix.lib.test
from django.test import TestCase

from unimatrix.ext.octet.models import Blob
from ..blob import BlobRepository
from ....lib.backends.local import LocalDiskBackend


@unimatrix.lib.test.integration
class BlobRepositoryTestCase(TestCase):

    def setUp(self):
        self.blobs = BlobRepository()
        self.backend = LocalDiskBackend(base_path=tempfile.mkdtemp())

        ioc.provide('octet.BlobStorage', self.backend, force=True)

    def test_calculate_checksum(self):
        h = hashlib.sha256()
        h.update(b'Hello world!')
        c1 = h.hexdigest()
        c2 = self.blobs.calculate_checksum(io.BytesIO(b"Hello world!"))
        self.assertEqual(c1, c2)

    def test_add(self):
        with tempfile.NamedTemporaryFile('w+b') as f:
            f.write(b"Hello world!")
            f.flush()

            self.blobs.add(f, "text/plain")
