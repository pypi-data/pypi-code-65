"""Terramare-specific metadata for attrs classes."""

import enum
from typing import AbstractSet, Any, Callable, Generic, Mapping, cast

import attr
from typing_extensions import Final

from .deserializer import Deserializer, DeserializerFactory
from .error_utils import ContextStack, Err, Ok, Result
from .keyed_deserializer import K, KeyedDeserializerFactory, S
from .pretty_printer import print_type_name
from .types import DeserializableType, T, Tag

_METADATA_KEY: Final = "__terramare_terramare__"


class Metadata:
    """Base class for terramare metadata."""


@attr.s(auto_attribs=True, frozen=True)
class MetadataCollection:
    """Mapping of DeserializableTypes to terramare metadata."""

    _metadata: Mapping[DeserializableType, Metadata]

    def __getitem__(self, k: DeserializableType) -> Metadata:
        """Retrieve the metadata for a type."""
        try:
            if k in self._metadata:
                return self._metadata[k]
        except TypeError:
            # A TypeError is raised if k is not hashable.
            pass
        if hasattr(k, _METADATA_KEY):
            pair = getattr(k, _METADATA_KEY)
            if not isinstance(pair, tuple) or len(pair) != 2:
                raise TypeError("Metadata type mismatch")
            t, t_metadata = pair
            if not isinstance(t_metadata, Metadata):
                raise TypeError("Metadata type mismatch")
            if t == k:
                return t_metadata
        raise KeyError(k)


@attr.s(auto_attribs=True, frozen=True)
class MetadataDeserializerFactory(DeserializerFactory):
    """Create a deserializer from metadata."""

    _metadata: MetadataCollection
    _keyed_ds_factory: KeyedDeserializerFactory

    def mk_ds_internal(
        self, factory: DeserializerFactory, cs: ContextStack, type_: Tag[T]
    ) -> Result[Result[Deserializer[T]]]:
        """Create a deserializer for the specified type."""
        try:
            metadata = self._metadata[type_.t]
        except KeyError:
            return Err(cs, "no metadata supplied")
        if isinstance(metadata, From):
            return Err(cs, "no metadata supplied")
        if isinstance(metadata, With_):
            return Ok(
                cast(
                    Result[Deserializer[T]], factory.mk_ds(cs, Tag(metadata.with_()))()
                )
            )
        if isinstance(metadata, Keyed):
            return Ok(
                self._keyed_ds_factory.mk_ds_internal(
                    factory, cs, metadata.key, metadata.mapping()
                )
            )
        raise NotImplementedError(
            f"unexpected metadata type: {print_type_name(metadata)}"
        )  # pragma: no cover


@attr.s(auto_attribs=True, frozen=True)
class Keyed(Generic[K, S], Metadata):
    """
    Metadata to deserialize into a type determined by the value of a key in the input dictionary.

    See the `keyed` decorator for more details.
    """

    key: K
    mapping: Callable[[], Mapping[S, DeserializableType]]


def keyed(
    key: K, mapping: Callable[[], Mapping[S, DeserializableType]]
) -> Callable[[type], type]:
    """
    Metadata to deserialize into a type determined by the value of a key in the input dictionary.

    :param `key`: Use the value of this field to determine the target type.
    :param `mapping`: Callable returning the mapping of possible key values to target types.

    Example usage:

    >>> from typing import Any
    >>> import attr
    >>> import terramare
    >>>
    >>> @keyed("type", lambda: {0: IntVariant, 1: StrVariant})
    ... class Variant:
    ...     pass
    >>>
    >>> @attr.s(auto_attribs=True)
    ... class IntVariant(Variant):
    ...     integer: int
    >>>
    >>> @attr.s(auto_attribs=True)
    ... class StrVariant(Variant):
    ...     string: str
    >>>
    >>> terramare.deserialize_into(Variant, {"type": 0, "integer": 1})
    IntVariant(integer=1)
    >>>
    >>> terramare.deserialize_into(Variant, {"type": 1, "string": "string"})
    StrVariant(string='string')

    """
    return _set_metadata_fn(Keyed(key, mapping))


Decorator = Callable[[Any], Any]


@enum.unique
class _FromType(enum.Enum):
    DICT = "dict"
    LIST = "list"
    VALUE = "value"


FromType = AbstractSet[_FromType]

DICT: Final = frozenset({_FromType.DICT})
LIST: Final = frozenset({_FromType.LIST})
VALUE: Final = frozenset({_FromType.VALUE})


@attr.s(auto_attribs=True, frozen=True)
class From(Metadata):
    """
    Specify the primitive types from which a class can be deserialized.

    See the `from_` decorator for more details.
    """

    from_: FromType


def from_(from_: FromType) -> Decorator:
    """
    Specify the primitive types from which a class can be deserialized.

    :param `from_`: Set of deserialization methods.

    Example usage:

    >>> import terramare
    >>>
    >>> class Int:
    ...    def __init__(self, x: int):
    ...        self.x = x
    ...
    ...    def __repr__(self) -> str:
    ...        return f"Int({self.x})"
    >>>
    >>> # Deserializable from a dict only.
    >>> @from_(DICT)
    ... class FromDict(Int):
    ...     pass
    >>>
    >>> terramare.deserialize_into(FromDict, {"x": 1})
    Int(1)
    >>>
    >>> # Deserializable from a list only.
    >>> @from_(LIST)
    ... class FromList(Int):
    ...     pass
    >>>
    >>> terramare.deserialize_into(FromList, [2])
    Int(2)
    >>>
    >>> # Deserializable from a single value only.
    >>> @from_(VALUE)
    ... class FromValue(Int):
    ...     pass
    >>>
    >>> terramare.deserialize_into(FromValue, 3)
    Int(3)
    >>>
    >>> # Deserializable from a dict or a list.
    >>> @from_(DICT | LIST)
    ... class FromDictOrList(Int):
    ...     pass
    >>>
    >>> terramare.deserialize_into(FromDictOrList, {"x": 4})
    Int(4)
    >>> terramare.deserialize_into(FromDictOrList, [5])
    Int(5)
    """
    return _set_metadata_fn(From(from_))


@attr.s(auto_attribs=True, frozen=True)
class With_(Metadata):
    """
    Specify a function to use to construct instances of a type.

    See the `with_` decorator for more details.
    """

    with_: Callable[[], DeserializableType]


def with_(with_: Callable[[], DeserializableType]) -> Decorator:
    """
    Specify a function to use to construct instances of a type.

    :param with_: Callable returning the construction function to use.

    Example usage:

    >>> import terramare
    >>>
    >>> @with_(lambda: Example.new)
    ... class Example:
    ...     def __init__(self, x: int):
    ...         self.x = x
    ...
    ...     def __repr__(self) -> str:
    ...         return f"Example({self.x})"
    ...
    ...     @staticmethod
    ...     @from_(VALUE)
    ...     def new(y: int) -> "Example":
    ...         return Example(y + 1)
    >>>
    >>> terramare.deserialize_into(Example, 1)
    Example(2)
    """
    return _set_metadata_fn(With_(with_))


def _set_metadata_fn(metadata: Metadata) -> Decorator:
    def inner(t: type) -> type:
        setattr(t, _METADATA_KEY, (t, metadata))
        return t

    return inner
