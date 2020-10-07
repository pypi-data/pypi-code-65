"""Common types and re-exports."""

from typing import Any, Generic, Mapping, Sequence, TypeVar, Union

import attr
from typing_extensions import Literal

TypedDictMetas = set()

# pylint: disable=unused-import
try:  # pragma: no cover
    from typing import _TypedDictMeta  # type: ignore[attr-defined]

    TypedDictMetas.add(_TypedDictMeta)

except ImportError:  # pragma: no cover
    pass

# pylint: disable=unused-import
try:  # pragma: no cover
    from typing_extensions import _TypedDictMeta  # type: ignore[attr-defined]

    TypedDictMetas.add(_TypedDictMeta)
except ImportError:  # pragma: no cover
    pass

try:
    from typing_extensions import _Literal  # type: ignore[attr-defined]

    LiteralMeta = _Literal
except ImportError:  # pragma: no cover
    LiteralMeta = Literal

T = TypeVar("T")


NotNonePrimitive = Union[str, int, float, Mapping, Sequence, bool]
Primitive = Union[NotNonePrimitive, None]

DeserializableType = Any


class TerramareError(Exception):
    """Base class for exceptions raised by terramare."""


@attr.s(auto_attribs=True, frozen=True)
class Tag(Generic[T]):
    """Tag type to satisfy the type checker."""

    t: DeserializableType
