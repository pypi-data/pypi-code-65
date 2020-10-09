"""Declares :class:`GoogleCloudStorageBackend`."""
import os

import aiohttp
import gcloud.aio.storage
from aiofile import AIOFile
from aiofile import Reader
from google.cloud import storage


from .base import BaseStorageBackend
from .base import RemoteStorageBackendMixin


class StorageBackend(RemoteStorageBackendMixin, BaseStorageBackend):
    """A storage backend that uses Google Cloud Storage (GCS)."""
    kind = 'google'

    @property
    def async_client(self):
        """Return the asynchronous GCS client."""
        if not getattr(self, '_async_client', None):
            self._async_client = gcloud.aio.storage.Storage()
        return self._async_client

    @property
    def async_bucket(self):
        """Return the asynchronous GCS bucket."""
        if not getattr(self, '_async_bucket', None):
            self._async_bucket = gcloud.aio.storage.Bucket(
                self.async_client, self.bucket_name)
        return self._async_bucket

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = storage.Client()
        self.bucket_name = os.environ['GOOGLE_GCS_BUCKET']
        self.bucket = self.client.get_bucket(self.bucket_name)
        self.project = os.environ['GOOGLE_CLOUD_PROJECT']

    async def async_close(self, handler):
        """Flush and close the IO object.

        This method has no effect if the file is already closed.
        """
        if handler.is_dirty():
            await self.async_push(handler.fd.name, handler.path)

        await super().async_close(handler)

    async def async_download(self, path, dst):
        """Downloads file from `path` to `dst` on the local filesystem."""
        await self.async_client.download_to_filename(
            self.bucket_name, self.storage_path(path), dst)
        return dst

    async def async_push(self, src, path):
        """Copies local absolute path `src` to remote `path`."""
        return await self.async_client.upload_from_filename(
            self.bucket_name, self.storage_path(path), src)

    async def async_exists(self, path):
        """Test whether a path exists.  Returns False for broken symbolic links
        if the storage backend supports them.
        """
        return await self.async_bucket.blob_exists(self.storage_path(path))

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
