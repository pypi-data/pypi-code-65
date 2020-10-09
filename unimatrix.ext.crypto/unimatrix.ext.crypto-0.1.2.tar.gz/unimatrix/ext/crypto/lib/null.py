"""Provides mock implementations."""


class Encrypter:
    """A :class:`~unimatrix.ext.crypto.encrypter.Encrypter` implementation
    that does nothing.
    """

    @property
    def metadata(self):
        """Return the dictionary with metadata describing this :class:`Encrypter`."""
        return {}

    def encrypt(self, blob):
        """Encrypt byte-sequence `blob`."""
        return blob
