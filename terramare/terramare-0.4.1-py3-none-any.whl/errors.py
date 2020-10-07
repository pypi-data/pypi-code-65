"""Common error types."""

import abc
from abc import abstractproperty

import attr

from .pretty_printer import print_primitive, print_type_name
from .tree import Tree
from .types import DeserializableType, Primitive, TerramareError


@attr.s(auto_attribs=True, frozen=True)
class _TreeException(TerramareError, abc.ABC):

    tree: Tree[str, str]

    def __str__(self) -> str:
        return f"{self.msg}\n{self.tree}"

    @abstractproperty
    def msg(self) -> str:
        """Format the exception message."""


@attr.s(auto_attribs=True, frozen=True)
class DeserializationError(_TreeException):
    """Raised when deserialization fails."""

    value: Primitive

    @property
    def msg(self) -> str:
        """Format the exception message."""
        return f"Failed to deserialize value '{print_primitive(self.value)}'"


@attr.s(auto_attribs=True, frozen=True)
class DeserializerFactoryError(_TreeException):
    """Raised when deserializer creation fails."""

    type_: DeserializableType

    @property
    def msg(self) -> str:
        """Format the exception message."""
        return f"Failed to create deserializer for type '{print_type_name(self.type_)}'"
