"""Declares :class:`CipherText`."""


class CipherText:
    """The base class for all encryption results."""
    __module__ = 'unimatrix.ext.crypto'

    @property
    def annotations(self):
        """Return the annotation associated to the :class:`CipherText`."""
        return dict(self.__annotations)

    def __init__(self, ct, annotations=None):
        """Initializes a :class:`CipherText` instance."""
        if not isinstance(ct, bytes):
            raise TypeError("Expected bytes, got %s" % type(ct).__name__)
        self.__ct = ct
        self.__annotations = annotations or {}

    def update_annotations(self, annotations):
        """Updates the annotations on the :class:`CipherText`."""
        self.__annotations.update(annotations)

    def __repr__(self):
        return f"<CipherText: {repr(self.__annotations)}>"

    def __bytes__(self):
        return self.__ct
