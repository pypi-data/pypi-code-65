"""Deserializer for a newtype alias."""

import attr

from .deserializer import Deserializer, DeserializerFactory
from .error_utils import ContextStack, Err, Ok, Result
from .types import T, Tag


@attr.s(auto_attribs=True, frozen=True)
class NewTypeDeserializerFactory(DeserializerFactory):
    """Create a newtype deserializer."""

    def mk_ds_internal(
        self, factory: DeserializerFactory, cs: ContextStack, type_: Tag[T]
    ) -> Result[Result[Deserializer[T]]]:
        """Create a deserializer for the specified newtype."""
        if not getattr(type_.t, "__qualname__", None) == "NewType.<locals>.new_type":
            return Err(cs, "type mismatch")
        return Ok(factory.mk_ds(cs, Tag(type_.t.__supertype__))())  # type: ignore
