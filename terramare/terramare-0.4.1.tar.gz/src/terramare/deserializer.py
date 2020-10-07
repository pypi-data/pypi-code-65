"""Deserializer interface."""

import abc
from functools import partial
from typing import Callable, Generic, Mapping, TypeVar, cast

import attr
from typing_extensions import final

from . import error_utils
from .error_utils import ContextStack, Result
from .errors import DeserializationError, DeserializerFactoryError
from .types import DeserializableType, Primitive, Tag

T = TypeVar("T")


class Deserializer(Generic[T], abc.ABC):
    """Deserializer interface."""

    @final
    def __call__(self, value: Primitive) -> T:
        """Deserialize a primitive value."""
        return error_utils.unwrap(
            partial(DeserializationError, value=value),
            self.ds(ContextStack.new(), value),
        )

    @abc.abstractmethod
    def ds(self, cs: ContextStack, value: Primitive) -> Result[T]:
        """Deserialize a primitive value with the supplied context."""


class DeserializerFactory(abc.ABC):
    """Deserializer factory interface."""

    @final
    def __call__(self, type_: DeserializableType) -> Deserializer[T]:
        """Create a deserializer for the supplied type."""
        return error_utils.unwrap(
            partial(DeserializerFactoryError, type_=type_),
            cast(Result[Deserializer[T]], self.mk_ds(ContextStack.new(), Tag(type_))()),
        )

    @final
    def mk_ds(
        self, cs: ContextStack, type_: Tag[T]
    ) -> Callable[[], Result[Deserializer[T]]]:
        """Create a deserializer for the supplied type."""

        def inner() -> Result[Deserializer[T]]:
            return error_utils.join(self.mk_ds_internal(self, cs, type_))

        return inner

    @abc.abstractmethod
    def mk_ds_internal(
        self, factory: "DeserializerFactory", cs: ContextStack, type_: Tag[T]
    ) -> Result[Result[Deserializer[T]]]:
        """
        Create a deserializer for the supplied type.

        An Err return value corresponds to a mismatch between the target type
        and the factory type, with an Ok(Err) return value corresponding to
        a matching factory failing to create a deserializer.

        Recurse using the supplied factory.
        """


@attr.s(auto_attribs=True, frozen=True)
class OneOfDeserializerFactory(DeserializerFactory):
    """Deserializer factory that tries a sequence of factories in turn."""

    _factories: Mapping[str, DeserializerFactory]

    def mk_ds_internal(
        self, factory: "DeserializerFactory", cs: ContextStack, type_: Tag[T]
    ) -> Result[Result[Deserializer[T]]]:
        """Try the configured sequence of factories in turn."""
        return (
            error_utils.collect_any_it(
                partial(f.mk_ds_internal, self, cs.alternative(k), type_)
                for k, f in self._factories.items()
            )
            # For some reason mypy doesn't correctly deduce the type without
            # the lambda.
            # pylint: disable=unnecessary-lambda
            .map(lambda dss: next(dss)).map_err(
                partial(error_utils.add_err, cs.make_err("no alternative matched"))
            )
        )
