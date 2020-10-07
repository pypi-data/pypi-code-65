"""Default metadata for selected standard library types."""


import datetime
import ipaddress
import pathlib
import re
from functools import partial
from typing import Callable, Mapping, Optional, Pattern, TypeVar

import attr
import dateutil.parser
from typing_extensions import Final

from terramare.metadata import Metadata
from terramare.types import DeserializableType

from . import metadata


@attr.s(auto_attribs=True, frozen=True)
class StdlibDeserializationError(Exception):
    """Exception type raised on failure by standard library deserializers."""

    msg: str


@metadata.from_(metadata.VALUE)
def _make_datetime(s: str) -> datetime.datetime:
    try:
        return dateutil.parser.isoparse(s)
    except ValueError as e:
        raise StdlibDeserializationError("invalid ISO-8601 datetime") from e


@metadata.from_(metadata.VALUE)
def _make_regex(s: str) -> Pattern:
    try:
        return re.compile(s)
    except re.error as e:
        raise StdlibDeserializationError(f"invalid regex: {e}") from e


@metadata.from_(metadata.VALUE)
def _make_ipv4_address(s: str) -> ipaddress.IPv4Address:
    try:
        return ipaddress.IPv4Address(s)
    except ValueError as e:
        raise StdlibDeserializationError(f"invalid IPv4 address: {e}") from e


@metadata.from_(metadata.VALUE)
def _make_ipv6_address(s: str) -> ipaddress.IPv6Address:
    try:
        return ipaddress.IPv6Address(s)
    except ValueError as e:
        raise StdlibDeserializationError(f"invalid IPv6 address: {e}") from e


T = TypeVar("T")


def _make_str_fn(path_t: Callable[[str], T]) -> Callable[[str], T]:
    @metadata.from_(metadata.VALUE)
    def _make_path(s: str) -> T:
        return path_t(s)

    return _make_path


DEFAULT_METADATA: Final[Mapping[DeserializableType, Optional[Metadata]]] = {
    datetime.datetime: metadata.With_(lambda: _make_datetime),
    Pattern: metadata.With_(lambda: _make_regex),
    ipaddress.IPv4Address: metadata.With_(lambda: _make_ipv4_address),
    ipaddress.IPv6Address: metadata.With_(lambda: _make_ipv6_address),
    **{
        t: metadata.With_(partial(_make_str_fn, t))
        for t in {
            pathlib.Path,
            pathlib.PosixPath,
            pathlib.WindowsPath,
            pathlib.PurePath,
            pathlib.PurePosixPath,
            pathlib.PureWindowsPath,
        }
    },
}
