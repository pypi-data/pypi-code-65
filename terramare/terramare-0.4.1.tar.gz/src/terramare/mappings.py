"""Deserializers for typed dictionaries."""

from functools import partial
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Hashable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Set,
    TypeVar,
    cast,
)

import attr
from typing_extensions import TypedDict

from . import error_utils, iterator_utils, type_utils
from .deserializer import Deserializer, DeserializerFactory
from .error_utils import ContextStack, Err, Ok, Result
from .types import DeserializableType, Primitive, T, Tag

K = TypeVar("K", bound=Hashable)


@attr.s(auto_attribs=True, frozen=True)
class MappingDeserializer(Generic[K, T], Deserializer[T]):
    """Deserialize a dictionary using a mapping of keys to deserializers."""

    _untyped_ds: Deserializer[dict]

    _key_ds: Deserializer[K]
    _required_dss: Mapping[K, Deserializer]
    _optional_dss: Mapping[K, Deserializer]
    _var_ds: Optional[Deserializer]

    _construct_fn: Callable[[ContextStack, Mapping[K, Any]], Result[T]]

    def ds(self, cs: ContextStack, value: Primitive) -> Result[T]:
        """
        Deserialize a primitive using a mapping of keys to deserializers.

        Each dictionary element is matched with a deserializer based on its key.
        An error will be raised if the dictionary is missing keys corresponding
        to required element deserializers.
        An error will also be raised if the dictionary contains keys that do not
        correspond to either required or optional element deserializers, and
        no variadic element deserializer is supplied.
        """
        untyped_elts = self._untyped_ds.ds(cs, value)
        if untyped_elts.is_err():
            return cast(Result[T], untyped_elts)

        keys = error_utils.collect_all(
            partial(self._key_ds.ds, cs.index(i), k)
            for i, k in enumerate(untyped_elts.unwrap())
        )
        if keys.is_err():
            return cast(Result[T], keys)

        try:
            zipped = iterator_utils.zip_strict_dict(
                self._required_dss,
                self._optional_dss,
                self._var_ds,
                dict(zip(keys.unwrap(), untyped_elts.unwrap().values())),
            )
        except ValueError as e:
            return Err(cs, str(e))
        # pylint: disable=protected-access
        result = error_utils.collect_all(
            partial(ds.ds, cs.index(str(k)), v) for k, (ds, v) in zipped.items()
        )
        if result.is_ok():
            return self._construct_fn(cs, dict(zip(zipped.keys(), result.unwrap())))
        return cast(Result[T], result)


@attr.s(auto_attribs=True, frozen=True)
class DictDeserializerFactory(DeserializerFactory):
    """Create deserializer for a dictionary of values of the same type."""

    def mk_ds_internal(
        self, factory: DeserializerFactory, cs: ContextStack, type_: Tag[T]
    ) -> Result[Result[Deserializer[T]]]:
        """Create a deserializer for the specified dictionary type."""
        if type_utils.get_base_of_generic_type(type_.t) not in {
            Dict,
            Mapping,
            MutableMapping,
        }:
            return Err(cs, "type mismatch")

        key_t, value_t = type_utils.get_type_parameters(type_.t)
        if not _is_hashable(key_t):
            return Ok(Err(cs.type_index(key_t), "unhashable type"))

        return Ok(
            error_utils.collect_all(
                [
                    factory.mk_ds(cs, Tag(dict)),
                    factory.mk_ds(cs.type_index(key_t), Tag(key_t)),
                    factory.mk_ds(cs.type_index(value_t), Tag(value_t)),
                ]
            ).map(
                lambda dss: MappingDeserializer(
                    dss[0], dss[1], {}, {}, dss[2], lambda _, v: Ok(cast(T, dict(v)))
                )
            )
        )


@attr.s(auto_attribs=True, frozen=True)
class TypedDictDeserializerFactory(DeserializerFactory):
    """Create deserializer for a TypedDict."""

    def mk_ds_internal(
        self, factory: DeserializerFactory, cs: ContextStack, type_: Tag[T]
    ) -> Result[Result[Deserializer[T]]]:
        """Create a deserializer for the specified TypedDict type."""
        if type_utils.get_base_of_generic_type(type_.t) != TypedDict:
            return Err(cs, "type mismatch")

        annotations = type_.t.__annotations__
        return Ok(
            error_utils.collect_all(
                [factory.mk_ds(cs, Tag(dict)), factory.mk_ds(cs, Tag(str))]
                + [
                    factory.mk_ds(cs.parameter_index(k, t), Tag(t))
                    for k, t in annotations.items()
                ],
            ).map(
                lambda dss: MappingDeserializer(
                    dss[0],
                    dss[1],
                    dict(zip(annotations, dss[2:])),
                    {},
                    None,
                    lambda _, v: Ok(cast(T, v)),
                )
            )
        )


def _is_hashable(type_: DeserializableType) -> bool:
    return (
        "__hash__" in dir(type_)
        and "__eq__" in dir(type_)
        and type_utils.get_base_of_generic_type(type_) not in {Dict, List, Set}
    )
