import re
import pathlib
from typing import List

from .user import User


class UsersList:

    def __init__(self, file):
        self.users = _parse_lines(_read_file_lines(file))

    def __iter__(self):
        return iter(self.users)

    def __len__(self):
        return len(self.users)


def _parse_line(line: str) -> User:
    stripped_line = re.sub(r"\s\s+", " ", line.strip())
    if len(stripped_line.split()) != 2:
        raise ValueError(f"file not formatted correctly. see line: {line}")
    email, password = stripped_line.split()
    return User(email, password)


def _parse_lines(lines: List[str]) -> List[User]:
    return [_parse_line(line) for line in lines]


def _is_empty_or_comment_string(string: str) -> bool:
    return (not string) or string.isspace() or string.strip().startswith('#') or string.strip().startswith('//')


def _read_file_lines(file: str) -> List[str]:
    return [line for line
            in pathlib.Path(file).read_text().splitlines()
            if not _is_empty_or_comment_string(line)]
