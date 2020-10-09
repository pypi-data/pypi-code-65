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
    def add(self, f, content_type):
        """Check if a :class:`~unimatrix.ext.octet.models.Blob` instance exists
        for given file-like object `f`. If one does not exist, create it. Return
        an instance of the model specified by :attr:`model_class`.
        """
        blob, created = self.model.objects.get_or_create(
            checksum=self.calculate_checksum(f), content_type=content_type,
            length=self.get_filesize(f.name))
        if created:
            labels = {}
            self.storage.push(f.name, blob.checksum)
            self.storage.label(labels)
            blob.setlabels(labels)
            blob.save()
        return blob

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
