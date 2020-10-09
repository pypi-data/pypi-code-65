"""Declares :class:`BaseBackend`."""


class BaseBackend:
    """The base class for all cryptographic backend implementations."""
    capabilities = []

    def has_capability(self, cap):
        """Return a boolean indicating if the backend has the given
        capability `cap`.
        """
        return cap in self.capabilities

    def has_capabilities(self, capabilities):
        """Return a boolean indicating if the backend has the given
        capabilities `capabilities`.
        """
        return set(capabilities) <= set(self.capabilities)

    def symmetric(self):
        """Return the :class:`~unimatrix.ext.crypto.SymmetricKey`
        implementation for this backend.
        """
        raise NotImplementedError("Subclasses must override this method.")
