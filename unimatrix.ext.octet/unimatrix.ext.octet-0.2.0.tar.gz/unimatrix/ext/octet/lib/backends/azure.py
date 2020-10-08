"""Declares :class:`StorageBackend` for use with Azure Blob Storage."""
import re
import os

from azure.storage.blob import BlobServiceClient # pylint: disable=E0611

from .base import BaseStorageBackend
from .base import RemoteStorageBackendMixin


class StorageBackend(RemoteStorageBackendMixin, BaseStorageBackend): # pylint: disable=R0801
    """A storage backend that uses Azure Blob Storage."""
    kind = 'azure'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = BlobServiceClient.from_connection_string(
            os.environ['AZURE_STORAGE_CONNECTION_STRING'])
        self.container_name = os.environ['AZURE_STORAGE_CONTAINER_NAME']
        self.account_name = re.search('AccountName=([^;]+);',
            os.environ['AZURE_STORAGE_CONNECTION_STRING']).group(1)
        if ('AccountName=%s' % self.account_name)\
        not in os.environ['AZURE_STORAGE_CONNECTION_STRING']: # pragma: no cover
            raise ValueError("Unable to parse account name from connection string")

    def get_blob_client(self, path):
        """Returns an Azure blob client for the given path."""
        return self.client.get_blob_client(self.container_name,
            self.storage_path(path))

    def close(self, handler):
        """Flush and close the IO object.

        This method has no effect if the file is already closed.
        """
        if handler.is_dirty():
            handler.fd.seek(0)
            blob = self.get_blob_client(handler.path)
            with open(handler.fd.name, 'rb') as f:
                blob.upload_blob(f, overwrite=True)

    def download(self, path, dst):
        """Downloads file from `path` to `dst` on the local filesystem."""
        blob = self.get_blob_client(path)
        stream = blob.download_blob()
        with open(dst, 'wb') as f:
            stream.readinto(f)
        return dst

    def exists(self, path):
        """Test whether a path exists.  Returns False for broken symbolic links
        if the storage backend supports them.
        """
        return self.get_blob_client(path).exists()

    def update_labels(self, labels):
        """Update dictionary `labels` with the label for a specific
        storage backend.
        """
        labels.update({
            'azure.microsoft.com/blob-storage-account': self.account_name,
            'azure.microsoft.com/blob-storage-container': self.container_name
        })

    def read(self, handler, size=-1):
        """Read at most n characters from handler.

        Read from underlying buffer until we have n characters or we hit EOF.
        If n is negative or omitted, read until EOF.
        """
        if size != -1:
            raise NotImplementedError("Partial reads are not implemented.")

        # It supports offset/length so we can implement seeking.
        blob = self.get_blob_client(handler.path)
        stream = blob.download_blob(encoding="UTF-8" if not handler.is_binary() else None)
        return stream.readall()

    def push(self, src, path):
        """Copies local absolute path `src` to remote `path`."""
        blob = self.get_blob_client(path)
        with open(src, 'rb') as f:
            blob.upload_blob(f, overwrite=True)

    def unlink(self, path):
        """Remove a path."""
        raise NotImplementedError
