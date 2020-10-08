"""Declares :class:`GoogleCloudStorageBackend`."""
import os

from google.cloud import storage

from .base import BaseStorageBackend
from .base import RemoteStorageBackendMixin


class StorageBackend(RemoteStorageBackendMixin, BaseStorageBackend):
    """A storage backend that uses Google Cloud Storage (GCS)."""
    kind = 'google'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = storage.Client()
        self.bucket = self.client.get_bucket(os.environ['GOOGLE_GCS_BUCKET'])
        self.project = os.environ['GOOGLE_CLOUD_PROJECT']

    def close(self, handler):
        """Flush and close the IO object.

        This method has no effect if the file is already closed.
        """
        dst = self.storage_path(handler.path)
        if handler.is_dirty():
            blob = self.bucket.blob(dst)
            blob.upload_from_filename(handler.fd.name)

    def download(self, path, dst):
        """Downloads file from `path` to `dst` on the local filesystem."""
        blob = self.bucket.blob(self.storage_path(path))
        blob.download_to_filename(dst)
        return dst

    def exists(self, path):
        """Test whether a path exists.  Returns False for broken symbolic links
        if the storage backend supports them.
        """
        return storage.Blob(bucket=self.bucket, name=self.storage_path(path))\
            .exists(self.client)

    def read(self, handler, size=-1):
        """Read at most n characters from handler.

        Read from underlying buffer until we have n characters or we hit EOF.
        If n is negative or omitted, read until EOF.
        """
        if size != -1:
            raise NotImplementedError("Partial reads are not implemented.")

        # TODO: This is not going to play well with seeking and friends (pylint: disable=W0511).
        self.download(handler.path, handler.fd.name)
        return handler.fd.read(size)

    def push(self, src, path):
        """Copies local absolute path `src` to remote `path`."""
        blob = self.bucket.blob(self.storage_path(path))
        blob.upload_from_filename(src)

    def unlink(self, path):
        """Remove a path."""
        self.bucket.delete_blobs(
            blobs=list(self.bucket.list_blobs(prefix=self.storage_path(path))))

    def update_labels(self, labels):
        """Update dictionary `labels` with the label for a specific
        storage backend.
        """
        labels.update({
            'cloud.google.com/project': self.project,
            'storage.googleapis.com/bucket': self.bucket
        })
