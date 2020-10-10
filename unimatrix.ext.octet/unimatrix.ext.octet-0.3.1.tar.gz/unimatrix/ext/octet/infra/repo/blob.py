"""Declares :class:`BlobRepository`."""
from .abstractblob import AbstractBlobRepository


class BlobRepository(AbstractBlobRepository):
    """Provides an interface to persist blobs used as input for jobs (environment,
    arguments, secrets and files).
    """
    model_class = 'octet.Blob'
