"""Deserializer implementing dynamic dispatch based on the value of a dictionary key."""

from functools import partial
from typing import Any, Generic, Hashable, Mapping, TypeVar, Union, cast

import attr

from . import error_utils
from .deserializer import Deserializer, DeserializerFactory
from .error_utils import ContextStack, Err, Result
from .errors import DeserializerFactoryError
from .types import DeserializableType, Primitive, T, Tag

K = TypeVar("K", bound=Hashable)
S = TypeVar("S", bound=Hashable)


@attr.s(auto_attribs=True, frozen=True)
class KeyedDeserializer(Generic[K, S, T], Deserializer[T]):
    """Deserialize a dictionary based on the value of one of its keys."""

    _dict_ds: Deserializer[Mapping[K, Any]]

    _key: K
    _key_ds: Deserializer[S]

    _remainder_dss: Mapping[S, Deserializer[T]]

    def ds(self, cs: ContextStack, value: Primitive) -> Result[T]:
        """Deserialize a dictionary based on the value of one of its keys."""
        elts_result = self._dict_ds.ds(cs, value)
        if elts_result.is_err():
            return cast(Result[T], elts_result)
        elts = elts_result.unwrap()

        if self._key not in elts:
            return Err(cs, f"missing key: '{self._key}'")

        key_result = self._key_ds.ds(cs.index(_key_str(self._key)), elts[self._key])
        if key_result.is_err():
            return cast(Result[T], key_result)
        key = key_result.unwrap()

        if key not in self._remainder_dss:
            return Err(
                cs.index(_key_str(self._key)),
                f"expected one of {{{', '.join(map(str, self._remainder_dss))}}}",
            )

        return self._remainder_dss[key].ds(
            cs.alternative(_key_str(key)),
            {k: v for k, v in elts.items() if k != self._key},
        )


@attr.s(auto_attribs=True, frozen=True)
class KeyedDeserializerFactory(Generic[K, S, T]):
    """Create a keyed deserializer."""

    def __call__(
        self,
        factory: DeserializerFactory,
        key: K,
        mapping: Mapping[S, DeserializableType],
    ) -> Deserializer[T]:
        """Create a KeyDeserializer from a specified key field and a value/type mapping."""
        return error_utils.unwrap(
            partial(DeserializerFactoryError, type_=Union[tuple(map(type, mapping))]),
            self.mk_ds_internal(factory, ContextStack.new(), key, mapping),
        )

    def mk_ds_internal(
        self,
        factory: DeserializerFactory,
        cs: ContextStack,
        key: K,
        mapping: Mapping[S, DeserializableType],
    ) -> Result[Deserializer[T]]:
        """
        Create a KeyDeserializer from a specified key field and mapping of key values to types.

        Recurse using the supplied factory.
        """
        return error_utils.collect_all(
            [
                factory.mk_ds(cs, Tag(Mapping[type(key), Any])),  # type: ignore[misc]
                factory.mk_ds(cs, Tag(Union[tuple(map(type, mapping))])),
            ]
            + [
                factory.mk_ds(cs.parameter_index(_key_str(k), t), Tag(t))
                for k, t in mapping.items()
            ]
        ).map(
            lambda dss: KeyedDeserializer(
                dss[0], key, dss[1], dict(zip(mapping, dss[2:]))
            )
        )


def _key_str(key: Any) -> Union[int, str]:
    if isinstance(key, int):
        return key
    return str(key)
