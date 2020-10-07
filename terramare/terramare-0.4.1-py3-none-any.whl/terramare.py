"""Automatically deserialize complex objects from simple Python types."""

import dataclasses
from typing import (
    AbstractSet,
    Callable,
    Dict,
    FrozenSet,
    Iterable,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    MutableSequence,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
)

from typing_extensions import Final, TypedDict

from terramare.stdlib_metadata import DEFAULT_METADATA, StdlibDeserializationError

from . import (
    classes,
    deserializer,
    enums,
    keyed_deserializer,
    mappings,
    metadata,
    newtypes,
    primitives,
    sequences,
    type_utils,
    unions,
)
from .types import DeserializableType, Primitive, T, TypedDictMetas

__all__ = [
    "DEFAULT_FALSE_STRINGS",
    "DEFAULT_TRUE_STRINGS",
    "Primitive",
    "create_deserializer_factory",
    "deserialize_into",
]

DEFAULT_TRUE_STRINGS: Final = frozenset({"yes", "on", "true", "1"})
DEFAULT_FALSE_STRINGS: Final = frozenset({"no", "off", "false", "0"})


def deserialize_into(
    type_: DeserializableType,
    value: Primitive,
    *,
    coerce_strings: bool = False,
    true_strings: AbstractSet[str] = DEFAULT_TRUE_STRINGS,
    false_strings: AbstractSet[str] = DEFAULT_FALSE_STRINGS,
    handle_exception_types: AbstractSet[Type[Exception]] = frozenset(),
    _experimental_metadata: Optional[
        Mapping[DeserializableType, Optional[metadata.Metadata]]
    ] = None,
) -> T:
    """
    Deserialize a primitive as a value of the specified type.

    :param `type_`: Deserialize into this type.
    :param `value`: Primitive value to attempt to deserialize.
    :param `coerce_strings`: If set, attempt to convert :python:`str` values to
        :python:`bool`, :python:`int`, or :python:`float` where the latter are required.
        For example:

        >>> deserialize_into(int, "1")
        Traceback (most recent call last):
            ...
        terramare.errors.DeserializationError: ...
        >>> deserialize_into(int, "1", coerce_strings=True)
        1

        Note that setting this option will cause :python:`terramare` to reject
        non-string primitives where a :python:`bool`, :python:`int`, or :python:`float`
        is required.
        For example:

        >>> deserialize_into(int, 1)
        1
        >>> deserialize_into(int, 1, coerce_strings=True)
        Traceback (most recent call last):
            ...
        terramare.errors.DeserializationError: ...

        This option defaults to :python:`False`.

    :param `true_strings`: Set of strings to convert to :python:`True` when convering a
        :python:`str` value to a :python:`bool`. Case is ignored.

        This value defaults to :python:`{"yes", "on", "true", "1"}`.

    :param `false_strings`: Set of strings to convert to :python:`False` when convering
        a :python:`str` value to a :python:`bool`. Case is ignored.

        This value defaults to :python:`{"no", "off", "false", "0"}`.

    :param `handle_exception_types`: Set of additional exception types that
        :python:`terramare` should catch and handle rather than propogating.

        Generally this will still result in an exception being raised. However, it will
        be a :python:`terramare` exception containing additional context.

        This option is useful when the deserialization target provides some form of
        additional validation. For example:

        >>> from typing import Union
        >>> import attr
        >>>
        >>> @metadata.from_(metadata.VALUE)
        ... @attr.s
        ... class Paint:
        ...    color: str = attr.ib(validator=attr.validators.in_(["red", "blue"]))

        When no exception types are provided, context is lost when deserializing into a
        single type:

        >>> deserialize_into(Paint, "green")
        Traceback (most recent call last):
        ...
        ValueError: 'color' must be in ['red', 'blue'] (got 'green')

        When the exception type is provided, that context is preserved:

        >>> deserialize_into(Paint, "green", handle_exception_types={ValueError})
        Traceback (most recent call last):
        ...
        terramare.errors.DeserializationError: ...
        .: no alternative matched
        └─ • value: 'color' must be in ['red', 'blue'] (got 'green')

        The exception is when the deserialization target is a union type, where
        :python:`terramare` will continue to try further union variants - as it would
        when encountering a deserialization failure.

        When no exception types are provided, :python:`terramare` cannot try further
        union variants if one fails due to a validation error:

        >>> deserialize_into(Union[Paint, str], "green")
        Traceback (most recent call last):
        ...
        ValueError: 'color' must be in ['red', 'blue'] (got 'green')

        When the exception type is provided, :python:`terramare` continues and
        successfully deserializes into a later variant.

        >>> deserialize_into(Union[Paint, str], "green", handle_exception_types={ValueError})
        'green'

    :param _experimental_metadata: See :ref:`experimental-features-metadata`.

    :raises terramare.DeserializerFactoryError: if a deserializer for :python:`type_`
        cannot be created.
    :raises terramare.DeserializationError: if the deserializer fails to deserialize a
        value of :python:`type_` from :python:`value`.
    """  # noqa: E501

    return create_deserializer_factory(
        coerce_strings=coerce_strings,
        true_strings=true_strings,
        false_strings=false_strings,
        handle_exception_types=handle_exception_types,
        _experimental_metadata=_experimental_metadata,
    )(type_)(value)


def create_deserializer_factory(
    *,
    coerce_strings: bool = False,
    true_strings: AbstractSet[str] = DEFAULT_TRUE_STRINGS,
    false_strings: AbstractSet[str] = DEFAULT_FALSE_STRINGS,
    handle_exception_types: AbstractSet[Type[Exception]] = frozenset(),
    _experimental_metadata: Optional[
        Mapping[DeserializableType, Optional[metadata.Metadata]]
    ] = None,
) -> deserializer.DeserializerFactory:
    """Create a DeserializerFactory using sensible defaults which may be overridden."""
    metadata_collection = metadata.MetadataCollection(
        {
            k: v
            for k, v in {**DEFAULT_METADATA, **(_experimental_metadata or {})}.items()
            if v is not None
        }
    )

    def _class_deserializer_enable_if(t: DeserializableType) -> metadata.FromType:
        # Explicitly disable class deserializer creation for typing types.
        # They are technically callable, so the class deserializer factory will
        # create a deserializer, but this will always raise if called.
        if type_utils.get_base_of_generic_type(t) in {
            AbstractSet,
            Callable,
            Dict,
            FrozenSet,
            Iterable,
            Iterator,
            List,
            Mapping,
            MutableMapping,
            MutableSequence,
            Sequence,
            Set,
            Tuple,
            TypedDict,
            *TypedDictMetas,
        }:
            return frozenset()
        try:
            t_metadata = metadata_collection[t]
        except KeyError:
            pass
        else:
            # Metadata of other types will be consumed by the
            # MetadataDeserializerFactory before reaching this function, making
            # this branch hard to miss.
            if isinstance(  # pragma: no branch
                # pylint: disable=protected-access
                t_metadata,
                metadata.From,
            ):
                return t_metadata.from_
        if _is_attrs_class(t) or _is_dataclass(t):
            return metadata.DICT
        if _is_namedtuple(t):
            return metadata.DICT | metadata.LIST
        return frozenset()

    return deserializer.OneOfDeserializerFactory(
        {
            "metadata": metadata.MetadataDeserializerFactory(
                metadata_collection, keyed_deserializer.KeyedDeserializerFactory()
            ),
            "newtype": newtypes.NewTypeDeserializerFactory(),
            "primitive": primitives.PrimitiveDeserializerFactory(
                {
                    **{k.lower(): True for k in true_strings},
                    **{k.lower(): False for k in false_strings},
                }
                if coerce_strings
                else None
            ),
            "literal": enums.LiteralDeserializerFactory(),
            "enum": enums.EnumDeserializerFactory(),
            "union": unions.UnionDeserializerFactory(),
            "tuple": sequences.TupleDeserializerFactory(),
            "sequence": sequences.HomogeneousSequenceDeserializerFactory(),
            "typeddict": mappings.TypedDictDeserializerFactory(),
            "dict": mappings.DictDeserializerFactory(),
            "class": classes.ClassDeserializerFactory(
                enable_if=_class_deserializer_enable_if,
                handle_exception_ts=handle_exception_types
                | {StdlibDeserializationError},
            ),
        }
    )


def _is_attrs_class(t: DeserializableType) -> bool:
    return hasattr(t, "__attrs_attrs__")


def _is_dataclass(t: DeserializableType) -> bool:
    return isinstance(t, type) and dataclasses.is_dataclass(t)


def _is_namedtuple(t: DeserializableType) -> bool:
    return (
        isinstance(t, type)
        and issubclass(t, tuple)
        and hasattr(t, "_asdict")
        and hasattr(t, "__annotations__")
    )
