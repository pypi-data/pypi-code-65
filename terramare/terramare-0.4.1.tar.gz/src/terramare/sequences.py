"""Deserializer for a generalized homogenous sequence."""

from functools import partial
from typing import (
    AbstractSet,
    Any,
    Callable,
    Dict,
    FrozenSet,
    Iterable,
    Iterator,
    List,
    MutableSequence,
    Optional,
    Sequence,
    Set,
    Tuple,
    cast,
)

import attr

from . import error_utils, iterator_utils, type_utils
from .deserializer import Deserializer, DeserializerFactory
from .error_utils import ContextStack, Err, Ok, Result
from .types import Primitive, T, Tag


@attr.s(auto_attribs=True, frozen=True)
class SequenceDeserializer(Deserializer[T]):
    """Deserialize a list using a sequence of deserializers."""

    _untyped_ds: Deserializer[list]

    _required_dss: Sequence[Deserializer]
    _optional_dss: Sequence[Deserializer]
    _var_ds: Optional[Deserializer]

    _construct_fn: Callable[[ContextStack, Sequence[Any]], Result[T]]

    def ds(self, cs: ContextStack, value: Primitive) -> Result[T]:
        """
        Deserialize a primitive using a sequence of deserializers.

        Each list element is matched with a deserializer based on its index.
        From the start of the list:
        - Elements are first matched with the required element deserializers,
          raising an error if there are too few elements;
        - Additional elements are then matched with the optional element
          deserializers;
        - Any remaining elements are matched with the variadic element
          deserializer, if supplied. Otherwise an error is raised.
        """
        elts = self._untyped_ds.ds(cs, value)
        if elts.is_err():
            return cast(Result[T], elts)
        try:
            zipped = iterator_utils.zip_strict(
                self._required_dss, self._optional_dss, self._var_ds, elts.unwrap()
            )
        except ValueError as e:
            return Err(cs, str(e))
        # pylint: disable=protected-access
        result = error_utils.collect_all(
            partial(ds.ds, cs.index(i), v) for i, (ds, v) in enumerate(zipped)
        )
        if result.is_err():
            return cast(Result[T], result)
        return self._construct_fn(cs, result.unwrap())


@attr.s(auto_attribs=True, frozen=True)
class HomogeneousSequenceDeserializerFactory(DeserializerFactory):
    """Create deserializer for a generalized homogenous sequence type."""

    def mk_ds_internal(
        self, factory: DeserializerFactory, cs: ContextStack, type_: Tag[T]
    ) -> Result[Result[Deserializer[T]]]:
        """Create a deserializer for the specified homogeneous sequence type."""
        sequence_fns = cast(
            Dict[T, Callable[[Sequence[Any]], T]],
            {
                AbstractSet: set,
                FrozenSet: frozenset,
                Iterable: list,
                Iterator: iter,
                List: list,
                MutableSequence: list,
                Sequence: list,
                Set: set,
            },
        )
        base_t = cast(T, type_utils.get_base_of_generic_type(type_.t))
        if base_t not in sequence_fns:
            return Err(cs, "type mismatch")

        [value_t] = type_utils.get_type_parameters(type_.t)
        return Ok(
            error_utils.collect_all(
                [
                    factory.mk_ds(cs, Tag(list)),
                    factory.mk_ds(cs.type_index(value_t), Tag(value_t)),
                ]
            ).map(
                lambda dss: SequenceDeserializer(
                    dss[0], [], [], dss[1], lambda _, v: Ok(sequence_fns[base_t](v))
                )
            )
        )


@attr.s(auto_attribs=True, frozen=True)
class TupleDeserializerFactory(DeserializerFactory):
    """Create deserializer for a tuple type."""

    def mk_ds_internal(
        self, factory: DeserializerFactory, cs: ContextStack, type_: Tag[T]
    ) -> Result[Result[Deserializer[T]]]:
        """Create a deserializer for the specified tuple type."""
        if not type_utils.get_base_of_generic_type(type_.t) == Tuple:
            return Err(cs, "type mismatch")
        types = type_utils.get_type_parameters(type_.t)
        if types and types[-1] == Ellipsis:
            # variadic tuple
            return Ok(
                error_utils.collect_all(
                    [factory.mk_ds(cs, Tag(list))]
                    + [factory.mk_ds(cs.type_index(t), Tag(t)) for t in types[:-1]]
                ).map(
                    lambda dss: SequenceDeserializer(
                        dss[0],
                        dss[1:-1],
                        [],
                        dss[-1],
                        lambda _, v: Ok(cast(T, tuple(v))),
                    )
                )
            )
        else:
            # fixed-length tuple
            return Ok(
                error_utils.collect_all(
                    [factory.mk_ds(cs, Tag(list))]
                    + [
                        factory.mk_ds(cs.parameter_index(i, t), Tag(t))
                        for i, t in enumerate(types)
                    ]
                ).map(
                    lambda dss: SequenceDeserializer(
                        dss[0], dss[1:], [], None, lambda _, v: Ok(cast(T, tuple(v)))
                    )
                )
            )
