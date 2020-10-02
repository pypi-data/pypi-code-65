from typing import Any, Dict

from .sqlite import SqliteStorageBackend

BACKENDS: Dict[str, Any] = {"sqlite": {"object": SqliteStorageBackend, "params": ["db_path"]}}
