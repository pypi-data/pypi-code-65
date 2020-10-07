"""Deserializers for primitive types."""

from functools import partial
from typing import (
    AbstractSet,
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    NoReturn,
    Optional,
    Type,
    TypeVar,
    cast,
)

import attr

from . import pretty_printer
from .deserializer import Deserializer, DeserializerFactory
from .error_utils import ContextStack, Err, Ok, Result
from .types import DeserializableType, Primitive, T, Tag


@attr.s(auto_attribs=True, frozen=True)
class PrimitiveDeserializer(Deserializer[T]):
    """Deserializer for a primitive type."""

    _deserializer: Callable[[Primitive], T]

    def ds(self, cs: ContextStack, value: Primitive) -> Result[T]:
        """Deserialize a primitive value."""
        try:
            return Ok(self._deserializer(value))  # type: ignore[misc, call-arg]
        except _PrimitiveError as e:
            return Err(cs, str(e))


@attr.s(auto_attribs=True, frozen=True)
class PrimitiveDeserializerFactory(DeserializerFactory):
    """Create deserializer for a primitive type."""

    _bool_strings: Optional[Mapping[str, bool]] = None

    def mk_ds_internal(
        self, _: DeserializerFactory, cs: ContextStack, type_: Tag[T]
    ) -> Result[Result[Deserializer[T]]]:
        """Create a deserializer for the specified primitive type."""
        if self._bool_strings is not None:
            deserialize_int = _deserialize_int_from_string
            deserialize_float = _deserialize_float_from_string
            deserialize_bool: Callable[[Primitive], bool] = partial(
                _deserialize_bool_from_string,
                {s for s, v in self._bool_strings.items() if v},
                {s for s, v in self._bool_strings.items() if not v},
            )
        else:
            deserialize_int = _deserialize_int
            deserialize_float = _deserialize_float
            deserialize_bool = _deserialize_bool
        ds = cast(
            Dict[DeserializableType, Callable[[Primitive], T]],
            {
                Any: lambda x: x,
                str: _deserialize_str,
                int: deserialize_int,
                float: deserialize_float,
                dict: _deserialize_dict,
                list: _deserialize_list,
                bool: deserialize_bool,
                type(None): _deserialize_none,
            },
        )
        try:
            return Ok(Ok(PrimitiveDeserializer(ds[type_.t])))
        except (KeyError, TypeError):
            # A TypeError is raised if the type is unhashable.
            return Err(cs, "type mismatch")


@attr.s(auto_attribs=True, frozen=True)
class _PrimitiveError(Exception):
    msg: str


def _deserialize_str(value: Primitive) -> str:
    """Deserialise a primitive as a string."""
    return _to_primitive(value, str)


def _deserialize_int(value: Primitive) -> int:
    """
    Deserialise a primitive as an int.

    Union[bool, int] will be collapsed into int, so special-case bools.
    TODO - deserialize with best match
    """
    if isinstance(value, bool):
        return value
    return _to_primitive(value, int)


def _deserialize_int_from_string(value: Primitive) -> int:
    value = _assert_string(value, int).lower()
    try:
        return int(value)
    except ValueError as e:
        raise _PrimitiveError(f"could not coerce value '{value}' to type 'int'") from e


def _deserialize_float(value: Primitive) -> float:
    """
    Deserialize a primitive as a float.

    Both ints and floats are acceptable input values.
    """
    try:
        return _to_primitive(value, int)
    except _PrimitiveError:
        return _to_primitive(value, float)


def _deserialize_float_from_string(value: Primitive) -> float:
    value = _assert_string(value, float).lower()
    try:
        return float(value)
    except ValueError as e:
        raise _PrimitiveError(
            f"could not coerce value '{value}' to type 'float'"
        ) from e


def _deserialize_dict(value: Primitive) -> Dict[str, Any]:
    """Deserialize a primitive as an untyped dict."""
    return _to_primitive(value, dict)


def _deserialize_list(value: Primitive) -> List[Any]:
    """Deserialize a primitive as an untyped list."""
    return _to_primitive(value, list)


def _deserialize_bool(value: Primitive) -> bool:
    """Deserialize a primitive as a bool."""
    return _to_primitive(value, bool)


def _deserialize_bool_from_string(
    true_values: AbstractSet[str], false_values: AbstractSet[str], value: Primitive
) -> bool:
    """Deserialize a string as a bool."""
    value = _assert_string(value, bool).lower()
    if value in true_values:
        return True
    elif value in false_values:
        return False
    else:
        raise _PrimitiveError(
            "could not coerce value '{}' to type 'bool' (expected one of {})".format(
                value, set(true_values | false_values)
            )
        )


def _deserialize_none(value: Primitive) -> None:
    """Deserialize a primitive as None."""
    if value is None:
        return value
    _raise_type_mismatch(value, type(None))


S = TypeVar("S")


def _to_primitive(value: Primitive, primitive_t: Type[S]) -> S:
    if isinstance(value, primitive_t):
        return primitive_t.__call__(value)
    _raise_type_mismatch(value, primitive_t)


def _assert_string(value: Primitive, type_: type) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (bool, int, float)):
        raise _PrimitiveError(
            "type mismatch - expected 'str' (as coerce_strings is set)"
        )
    _raise_type_mismatch(value, type_)


def _raise_type_mismatch(value: Primitive, type_: type) -> NoReturn:
    raise _PrimitiveError(
        f"type mismatch - expected '{pretty_printer.print_type_name(type_)}'"
    )
