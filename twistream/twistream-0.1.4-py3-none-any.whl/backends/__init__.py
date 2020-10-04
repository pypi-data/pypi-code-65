from typing import Any, Dict

from .sqlite import SqliteStorageBackend
from .mongodb import MongoDBStorageBackend

BACKENDS: Dict[str, Any] = {
    "sqlite": {"object": SqliteStorageBackend, "params": ["db_path"]},
    "mongodb": {"object": MongoDBStorageBackend, "params": ["db_string", "collection_name"]},
}
