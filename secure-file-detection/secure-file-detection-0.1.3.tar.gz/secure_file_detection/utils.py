from pathlib import Path
from typing import *

from secure_file_detection.typing_types import PathLike

__all__ = [
    "get_path", "get_func_name", "get_type_from_mimetype", "construct_error_message"
]


def get_path(value: PathLike, /) -> Path:
    return Path(value) if isinstance(value, str) else value


def get_func_name(mimetype: str, /) -> str:
    return mimetype.replace("/", "_").replace("-", "_")


def get_type_from_mimetype(mimetype: str, /) -> str:
    return mimetype.split("/")[1].replace("-", "_")


def construct_error_message(pretend: str, actual: Optional[str] = None) -> str:
    if actual is None:
        return f'The file pretends to be "{pretend}" but is not.'
    return f'The file pretends to be "{pretend}" but is actual "{actual}".'

