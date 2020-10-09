"""Declares :class:`BackendProvider`."""


class BackendProvider:
    """Maintains a registry of encryption backends."""

    def __init__(self):
        self.__backends = {}

    def add(self, name, backend):
        """Adds a new cryptographic backend to the registry."""
        self.__backends[name] = backend

    def __getitem__(self, name):
        return self.__backends[name]
