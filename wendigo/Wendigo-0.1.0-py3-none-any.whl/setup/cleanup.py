from glob import glob
from pathlib import Path
from tempfile import gettempdir, TemporaryDirectory

__all__ = ["TMP_DIR"]

def get_tmp_dir() -> str:
    """
    Get a temporary directory.

    Returns
    -------
    path: Directory path.
    """
    path = Path(gettempdir()).joinpath("wendigo")

    if path.exists():
        # Delete sub directories.
        # Directories which were used by other applications such as Tesseract remain.
        for p in glob(str(path.joinpath("*"))):
            TemporaryDirectory._rmtree(p)
    else:
        path.mkdir(exist_ok=True)

    return str(path)

TMP_DIR = get_tmp_dir()