"""Deserializer factory for a generic class."""

import inspect
import sys
import typing
from functools import partial
from inspect import Parameter
from typing import AbstractSet, Any, Callable, Dict, List, Sequence, Type, TypeVar, cast

import attr

from . import error_utils, iterator_utils, mappings, sequences, unions
from .deserializer import Deserializer, DeserializerFactory
from .error_utils import ContextStack, Err, Ok, Result
from .metadata import DICT, LIST, VALUE, FromType, _FromType
from .types import DeserializableType, Primitive, T, Tag

S = TypeVar("S")


@attr.s(auto_attribs=True, frozen=True)
class ClassDeserializerFactory(DeserializerFactory):
    """Create deserializer for a class."""

    _enable_if: Callable[[DeserializableType], FromType] = lambda _: DICT | LIST | VALUE
    _handle_exception_ts: AbstractSet[Type[Exception]] = attr.ib(factory=frozenset)

    def mk_ds_internal(
        self, factory: DeserializerFactory, cs: ContextStack, type_: Tag[T]
    ) -> Result[Result[Deserializer[T]]]:
        """Create a deserializer for the specified class type."""

        def _mk_ds(name: str, fn: Any) -> Callable[[], Result[Deserializer[T]]]:
            return lambda: fn(
                self._handle_exception_ts, factory, cs.alternative(name), type_, params
            ).map(lambda ds: (name, ds))

        ds_fns = [
            _mk_ds(t.value, fn)
            for t, fn in {
                _FromType.DICT: _mk_dict_ds,
                _FromType.LIST: _mk_list_ds,
                _FromType.VALUE: _mk_value_ds,
            }.items()
            if t in self._enable_if(type_.t)
        ]

        if not hasattr(type_.t, "__call__"):
            return Err(cs, "type mismatch")
        if not ds_fns:
            return Err(cs, "not enabled for type")
        try:
            params = _get_parameters(type_.t)
        except _ParameterError as e:
            return Ok(Err(cs, e.msg))

        return Ok(
            error_utils.collect_any_it(ds_fns).map(
                lambda dss: unions.OneOfDeserializer(dict(dss))
            )
        )


def _mk_dict_ds(
    handle_exception_ts: AbstractSet[Type[Exception]],
    factory: DeserializerFactory,
    cs: ContextStack,
    type_: Tag[T],
    params: Sequence["_Parameter"],
) -> Result[Deserializer[T]]:
    non_kw_required = [p.name for p in params if p.is_required() and not p.is_kw()]
    # Non-keyword parameters can't be created easily pre-Python 3.8.
    if non_kw_required:  # pragma: no cover
        return Err(
            cs, "required non-keyword parameter(s) " + ", ".join(non_kw_required)
        )

    params = [p for p in params if p.is_kw()]
    result = _get_dss(factory, cs, type_, [dict, str], params)
    if result.is_err():
        return cast(Result[Deserializer[T]], result)
    dss = result.unwrap()

    var, non_var = iterator_utils.divide_list(_Parameter.is_var, params)
    param_dss = dict(zip((p.name for p in params), dss[2:]))
    return Ok(
        mappings.MappingDeserializer(
            dss[0],
            dss[1],
            {p.name: param_dss[p.name] for p in non_var if p.is_required()},
            {p.name: param_dss[p.name] for p in non_var if not p.is_required()},
            next(iter([param_dss[p.name] for p in var]), None),
            _mk_construct_fn(handle_exception_ts, lambda v: type_.t(**v)),
        )
    )


def _mk_list_ds(
    handle_exception_ts: AbstractSet[Type[Exception]],
    factory: DeserializerFactory,
    cs: ContextStack,
    type_: Tag[T],
    params: Sequence["_Parameter"],
) -> Result[Deserializer[T]]:
    non_pos_required = [p.name for p in params if p.is_required() and not p.is_pos()]
    if non_pos_required:
        return Err(
            cs, "required non-positional parameter(s) " + ", ".join(non_pos_required)
        )

    params = [p for p in params if p.is_pos()]
    result = _get_dss(factory, cs, type_, [list], params)
    if result.is_err():
        return cast(Result[Deserializer[T]], result)
    dss = result.unwrap()

    var, non_var = iterator_utils.divide_list(_Parameter.is_var, params)
    param_dss = dict(zip((p.name for p in params), dss[1:]))
    return Ok(
        sequences.SequenceDeserializer(
            dss[0],
            [param_dss[p.name] for p in non_var if p.is_required()],
            [param_dss[p.name] for p in non_var if not p.is_required()],
            next(iter([param_dss[p.name] for p in var]), None),
            _mk_construct_fn(handle_exception_ts, lambda v: type_.t(*v)),
        )
    )


@attr.s(auto_attribs=True, frozen=True)
class _ClassValueDeserializer(Deserializer[T]):
    """Deserialize a class from a single value."""

    _handle_exception_ts: AbstractSet[Type[Exception]]
    _construct_fn: Callable[[ContextStack, Any], Result[T]]
    _value_ds: Deserializer

    def ds(self, cs: ContextStack, value: Primitive) -> Result[T]:
        result = self._value_ds.ds(cs, value)
        if result.is_err():
            return cast(Result[T], result)
        return self._construct_fn(cs, result.unwrap())


def _mk_value_ds(
    handle_exception_ts: AbstractSet[Type[Exception]],
    factory: DeserializerFactory,
    cs: ContextStack,
    type_: Tag[T],
    params: Sequence["_Parameter"],
) -> Result[Deserializer[T]]:
    required, optional = iterator_utils.divide_list(_Parameter.is_required, params)
    if len(required) > 1 or len(required) + len(optional) < 1:
        return Err(
            cs,
            "unsupported number of parameters "
            + f"(required: {len(required)}, optional: {len(optional)})",
        )

    value_param = params[0]
    if not value_param.is_pos():
        return Err(cs, "non-positional first parameter")
    return _get_dss(factory, cs, type_, [], [value_param]).map(
        lambda dss: _ClassValueDeserializer(
            handle_exception_ts, _mk_construct_fn(handle_exception_ts, type_.t), dss[0]
        )
    )


def _get_dss(
    factory: DeserializerFactory,
    cs: ContextStack,
    type_: Tag[T],
    extra: Sequence[DeserializableType],
    params: Sequence["_Parameter"],
) -> Result[List[Deserializer]]:
    try:
        return error_utils.collect_all(
            [factory.mk_ds(cs, Tag(t)) for t in extra]
            + [
                factory.mk_ds(cs.parameter_index(p, t), Tag(t))
                for p, t in _get_type_hints(
                    type_.t, [p.parameter for p in params]
                ).items()
            ]
        )
    except _ParameterError as e:  # pragma: no cover
        # This branch is pretty hard to hit.
        return Err(cs, e.msg)


def _mk_construct_fn(
    handle_exception_ts: AbstractSet[Type[Exception]], fn: Callable[[Any], T]
) -> Callable[[ContextStack, Any], Result[T]]:
    def inner(cs: ContextStack, args: Any) -> Result[T]:
        try:
            return Ok(fn(args))
        # pylint: disable=catching-non-exception
        except tuple(handle_exception_ts) as e:
            return Err(cs, str(e))

    return inner


@attr.s(auto_attribs=True, frozen=True)
class _Parameter:
    parameter: Parameter

    @property
    def name(self) -> str:
        return self.parameter.name

    def is_var(self) -> bool:
        return self.parameter.kind in {
            Parameter.VAR_POSITIONAL,
            Parameter.VAR_KEYWORD,
        }

    def is_pos(self) -> bool:
        return self.parameter.kind in {
            Parameter.POSITIONAL_ONLY,
            Parameter.POSITIONAL_OR_KEYWORD,
            Parameter.VAR_POSITIONAL,
        }

    def is_kw(self) -> bool:
        return self.parameter.kind in {
            Parameter.KEYWORD_ONLY,
            Parameter.POSITIONAL_OR_KEYWORD,
            Parameter.VAR_KEYWORD,
        }

    def is_required(self) -> bool:
        return self.parameter.default == inspect.Parameter.empty and not self.is_var()


@attr.s(auto_attribs=True, frozen=True)
class _ParameterError(Exception):
    msg: str


def _get_parameters(type_: DeserializableType) -> List[_Parameter]:
    try:
        return [_Parameter(p) for p in inspect.signature(type_).parameters.values()]
    except ValueError as e:
        raise _ParameterError(str(e)) from e


def _get_type_hints(
    type_: DeserializableType, params: Sequence[inspect.Parameter]
) -> Dict[str, Any]:
    if hasattr(type_, "__globals__"):
        globals_ = getattr(type_, "__globals__")
    elif hasattr(type_, "__module__"):
        globals_ = vars(sys.modules[getattr(type_, "__module__")])
    else:  # pragma: no cover TODO
        globals_ = {}

    # For some reason `get_type_hints` can't handle the type returned by
    # `functools.partial` - but it _can_ handle its `__call__` method.
    if isinstance(type_, partial):
        type_ = type_.__call__

    try:
        type_hints = typing.get_type_hints(type_, globals_)
    except TypeError as e:  # pragma: no cover
        raise _ParameterError(str(e)) from None

    def get_type_hint(p: inspect.Parameter) -> Any:
        if p.name in type_hints:
            return type_hints[p.name]
        if p.annotation == inspect.Parameter.empty:
            return Any
        if not isinstance(p.annotation, str):
            return p.annotation
        # TODO __closure__?
        return eval(  # pragma: no cover, pylint: disable=eval-used
            p.annotation, globals_
        )

    return {p.name: get_type_hint(p) for p in params}
