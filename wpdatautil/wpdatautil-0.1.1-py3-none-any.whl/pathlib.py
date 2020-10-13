"""pathlib utilities."""
from pathlib import Path


def ensure_parent_dir(path: Path) -> None:
    """Ensure that the parent directory of the given path exists."""
    path.parent.mkdir(parents=True, exist_ok=True)
