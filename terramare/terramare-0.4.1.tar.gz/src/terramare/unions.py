"""Deserializer for a union of types."""

from functools import partial
from typing import Any, Mapping, Tuple, Union

import attr

from . import error_utils, pretty_printer, type_utils
from .deserializer import Deserializer, DeserializerFactory
from .error_utils import ContextStack, Err, Ok, Result
from .types import Primitive, T, Tag


@attr.s(auto_attribs=True, frozen=True)
class OneOfDeserializer(Deserializer[T]):
    """Deserialize with one of the supplied set of deserializers."""

    _dss: Mapping[str, Deserializer[T]]

    def ds(self, cs: ContextStack, value: Primitive) -> Result[T]:
        """Deserialize a primitive by trying several deserializers in turn."""
        return error_utils.collect_any(
            partial(ds.ds, cs.alternative(k), value) for k, ds in self._dss.items()
        ).map_err(partial(error_utils.add_err, cs.make_err("no alternative matched")))


@attr.s(auto_attribs=True, frozen=True)
class UnionDeserializerFactory(DeserializerFactory):
    """Create deserializer for a union of several types."""

    def mk_ds_internal(
        self, factory: DeserializerFactory, cs: ContextStack, type_: Tag[T]
    ) -> Result[Result[Deserializer[T]]]:
        """Create a deserializer for the specified union type."""
        if not type_utils.get_base_of_generic_type(type_.t) == Union:
            return Err(cs, "type mismatch")

        def mk_ds(i: int, t: Any) -> Result[Tuple[Any, Deserializer]]:
            return factory.mk_ds(cs.parameter_index(i, t), Tag(t))().map(
                lambda ds: (pretty_printer.print_type_name(t), ds)
            )

        return Ok(
            error_utils.collect_all(
                [
                    partial(mk_ds, i, t)
                    for i, t in enumerate(type_utils.get_type_parameters(type_.t))
                ]
            ).map(lambda dss: OneOfDeserializer(dict(dss)))
        )
