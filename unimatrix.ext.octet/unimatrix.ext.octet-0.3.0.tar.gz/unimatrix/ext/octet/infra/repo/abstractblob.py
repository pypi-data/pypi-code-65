"""Declares :class:`AbstractBlobRepository`."""
import abc
import hashlib
import os

import ioc
from django.apps import apps
from django.db import transaction


class AbstractBlobRepository:
    """Provides an interface to persist blobs used as input for jobs (environment,
    arguments, secrets and files).
    """
    storage = ioc.class_property('octet.BlobStorage')
    model_class = abc.abstractproperty()

    @property
    def model(self):
        """Returns the model class used by this repository."""
        return apps.get_model(self.model_class)

    @transaction.atomic
    @ioc.inject('factory', 'BlobFactory')
    def add(self, f, content_type, factory, encrypt=False):
        """Check if a :class:`~unimatrix.ext.octet.models.Blob` instance exists
        for given file-like object `f`. If one does not exist, create it. Return
        an instance of the model specified by :attr:`model_class`.
        """
        f.seek(0)
        checksum = self.calculate_checksum(f)
        created = False
        if not self.exists(checksum):
            blob = factory.new(f, content_type, encrypt=encrypt)
            created = True
        else:
            blob = self.model.objects.get(checksum=checksum)
        if created:
            labels = {}
            self.storage.push(f.name, blob.checksum)
            self.storage.label(labels)
            blob.setlabels(labels)
            blob.save()
            blob.fd = f
            blob.fd.seek(0)
        return blob

    def exists(self, checksum):
        """Return a boolean indicating if a file with the given checksum
        exists.
        """
        return self.model.objects.filter(checksum=checksum).exists()

    @ioc.inject('decrypter', 'BlobEncryptionBackend')
    def read(self, checksum, decrypter, decrypt=True):
        """Reads the full content of the :class:`Blob` identified by
        `checksum`.
        """
        blob = self.model.objects.get(checksum=checksum)
        with self.storage.open(checksum, 'rb') as f:
            buf = f.read()
            if blob.is_encrypted() and decrypt:
                ct = blob.get_ciphertext(buf)
                buf = decrypter.decrypt(ct, blob.get_key_id())

        return buf

    async def async_slice(self, checksum, length, offset=0):
        """Return a byte-sequence holding the slice specified by `length`
        and `offset`.
        """
        blob = self.model.objects.get(checksum=checksum)
        if blob.is_encrypted():
            raise TypeError("Encrypted blobs can not be sliced.")
        return await self.storage.async_slice(checksum, length, offset)

    @staticmethod
    def calculate_checksum(f):
        """Calculate a SHA-256 hash for file-like object `f`."""
        h = hashlib.sha256()
        p = f.tell()
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            h.update(chunk)
        f.seek(p)
        return h.hexdigest()

    @staticmethod
    def get_filesize(fp):
        """Return an unsigned integer indicating the size of file `fp`."""
        return os.path.getsize(fp)
