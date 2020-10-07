"""Deserializer for an enum."""

import enum
from functools import partial
from typing import Any, List, Sequence, TypeVar

import attr
from typing_extensions import Literal

from . import error_utils, pretty_printer, type_utils
from .deserializer import Deserializer, DeserializerFactory
from .error_utils import ContextStack, Err, Ok, Result
from .types import Primitive, T, Tag

S = TypeVar("S", bound=enum.Enum)


@attr.s(auto_attribs=True, frozen=True)
class EnumValueDeserializer(Deserializer[S]):
    """Deserialize a single enum value."""

    _ds: Deserializer[S]
    _match_value: Any
    _return_value: S

    def ds(self, cs: ContextStack, value: Primitive) -> Result[S]:
        """Deserialize a single enum value."""
        v = self._ds.ds(cs, value)
        if v.is_err():
            return v
        if v.unwrap() == self._match_value:
            return Ok(self._return_value)
        return Err(cs, "value mismatch")

    def __str__(self) -> str:
        """Return a string representation of the match value."""
        return repr(self._match_value)


@attr.s(auto_attribs=True, frozen=True)
class EnumDeserializer(Deserializer[T]):
    """Deserialize a primitive into an enum value."""

    _variant_dss: Sequence[EnumValueDeserializer]

    def ds(self, cs: ContextStack, value: Primitive) -> Result[T]:
        """
        Deserialize a primitive into an enum value.

        Match the primitive against the enum's values, not its names.
        """
        variant_cs = ContextStack.new()
        v = error_utils.collect_any(
            partial(ds.ds, variant_cs.alternative(str(ds)), value)
            for ds in self._variant_dss
        )
        if v.is_ok():
            return v
        return Err(
            cs,
            f"value mismatch {pretty_printer.print_primitive(value)}: "
            f"expected one of {{{', '.join(map(str, self._variant_dss))}}}",
        )


@attr.s(auto_attribs=True, frozen=True)
class EnumDeserializerFactory(DeserializerFactory):
    """Create deserializer for an enum type."""

    def mk_ds_internal(
        self, factory: DeserializerFactory, cs: ContextStack, type_: Tag[T]
    ) -> Result[Result[Deserializer[T]]]:
        """Create deserializer for the specified enum type."""
        if not (isinstance(type_.t, type) and issubclass(type_.t, enum.Enum)):
            return Err(cs, "type mismatch")
        variants: List[T] = list(type_.t)
        # Since type_.t is an enum type, and T == type_.t, values of type T have
        # `name` and `value` attributes. However, mypy can't infer this.
        names: List[str] = [v.name for v in variants]  # type: ignore[attr-defined]
        values: List[Any] = [v.value for v in variants]  # type: ignore[attr-defined]
        return Ok(
            error_utils.collect_all(
                # pylint: disable=cell-var-from-loop
                lambda: factory.mk_ds(
                    cs.parameter_index(name, type(val)), Tag(type(val))
                )().map(lambda ds: EnumValueDeserializer(ds, val, var))
                for var, name, val in zip(variants, names, values)
            ).map(EnumDeserializer)
        )


@attr.s(auto_attribs=True, frozen=True)
class LiteralDeserializerFactory(DeserializerFactory):
    """Create deserializer for a literal type."""

    def mk_ds_internal(
        self, factory: DeserializerFactory, cs: ContextStack, type_: Tag[T]
    ) -> Result[Result[Deserializer[T]]]:
        """Create a deserializer for the specified literal type."""
        if not type_utils.get_base_of_generic_type(type_.t) == Literal:
            return Err(cs, "type mismatch")
        return Ok(
            error_utils.collect_all(
                # pylint: disable=cell-var-from-loop
                lambda: factory.mk_ds(
                    cs.type_index(_get_literal_t(v)), Tag(_get_literal_t(v))
                )().map(lambda ds: EnumValueDeserializer(ds, v, v))
                for v in type_utils.get_type_parameters(type_.t)
            ).map(EnumDeserializer)
        )


def _get_literal_t(type_: type) -> type:
    if type_utils.get_base_of_generic_type(type_) == Literal:
        return type_
    return type(type_)
