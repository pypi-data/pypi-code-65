import warnings
from tempfile import TemporaryDirectory as _TemporaryDirectory
from wendigo import TMP_DIR
from wendigo.warnings import TemporaryDirectoryDeletionWarning

__all__ = ["Area"]

class Representator:
    """
    Representator.
    """
    def __repr__(self) -> str:
        """
        Get a representation.

        Returns
        -------
        repr: Representation.
        """
        return f"{self.__class__.__name__}({', '.join([f'{k}={v}' for k, v in self.__dict__.items()])})"

class Point(Representator):
    """
    Point.
    """
    def __init__(self, x: int, y: int):
        """
        Initialize.

        Parameters
        ----------
        x: Position X.
        y: Position Y.
        """
        self.x = round(x)
        self.y = round(y)

class Area(Representator):
    """
    Area.
    """
    @property
    def center(self) -> Point:
        """
        Get center position.

        Returns
        -------
        position: Position.
        """
        return Point(self.x + self.width / 2, self.y + self.height / 2)

    def __init__(self, x: int, y: int, width: int, height: int):
        """
        Initialize.

        Parameters
        ----------
        x: Position X.
        y: Position Y.
        width: Width.
        height: Height.
        """
        self.x = round(x)
        self.y = round(y)
        self.width = round(width)
        self.height = round(height)

class TemporaryDirectory(_TemporaryDirectory):
    """
    Temporary directory.
    """
    def __init__(self, suffix: str=None, prefix: str=None):
        """
        Initialize.

        Parameters
        ----------
        suffix: Suffix.
        prefix: Prefix.
        """
        super().__init__(suffix=suffix, prefix=prefix, dir=TMP_DIR)

    @classmethod
    def _cleanup(cls, name: str, warn_message: str):
        """
        Clean up.

        Parameters
        ----------
        name: Name.
        warn_message: Warning message.
        """
        try:
            super._cleanup(name, warn_message)
        except:
            # The directory is used by other applications such as Tesseract, so giving up to delete it now
            msg = f"Failed to delete temporary directory, but this one will be deleted at the next startup time of wendigo ({name})"
            warnings.warn(msg, TemporaryDirectoryDeletionWarning)