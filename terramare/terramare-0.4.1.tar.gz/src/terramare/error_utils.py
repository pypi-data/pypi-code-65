"""Utilities for dealing with terramare's error types."""

import abc
import itertools
import json
from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

import attr
import result
from result import Ok

from .iterator_utils import round_robin, round_robin_group
from .pretty_printer import print_type_name
from .tree import Tree

__all__ = [
    "ContextStack",
    "Err",
    "Ok",  # re-export
    "Result",
    "add_err",
    "collect_all",
    "collect_any",
    "collect_any_it",
    "join",
    "unwrap",
]

T = TypeVar("T")


class _Error(abc.ABC):
    @abc.abstractmethod
    def __add__(self, other: object) -> "_Error":
        """Combine two errors."""

    @abc.abstractmethod
    def map_(self, fn: Callable[["_LeafError"], None]) -> None:
        """Map a function over all leaf errors."""


@attr.s(auto_attribs=True, frozen=True)
class _LeafError(_Error):
    path: Tuple[str, ...]
    msg: str

    def __add__(self, other: object) -> "_Error":
        raise NotImplementedError  # pragma: no cover

    def map_(self, fn: Callable[["_LeafError"], None]) -> None:
        fn(self)


@attr.s(auto_attribs=True, frozen=True)
class _CompositeError(_Error):
    errors: List[Union[_LeafError, "_CompositeError"]]

    def __add__(self, other: object) -> "_Error":
        if isinstance(other, _LeafError):
            return _CompositeError(self.errors + [other])
        elif isinstance(other, _CompositeError):  # pragma: no cover
            return _CompositeError(self.errors + other.errors)
        raise NotImplementedError  # pragma: no cover

    def map_(self, fn: Callable[[_LeafError], None]) -> None:
        for error in self.errors:
            error.map_(fn)


@attr.s(auto_attribs=True)
class ContextStack:
    """Stack data structure for providing error context."""

    _stack: Tuple[str, ...]

    @staticmethod
    def new() -> "ContextStack":
        """Create a ContextStack."""
        return ContextStack(())

    def index(self, index: Union[int, str]) -> "ContextStack":
        """Push an index onto the context stack."""
        return self._push(json.dumps(index))

    def type_index(self, type_: Any) -> "ContextStack":
        """Push a type index onto the context stack."""
        return self._push(print_type_name(type_))

    def parameter_index(self, index: Union[int, str], type_: Any) -> "ContextStack":
        """Push a type parameter index onto the context stack."""
        return self._push(f"{json.dumps(index)}: {print_type_name(type_)}")

    def alternative(self, alternative: Union[int, str]) -> "ContextStack":
        """Push an alternative onto the context stack."""
        return self._push(f"• {alternative}")

    def _push(self, context: str) -> "ContextStack":
        return ContextStack(self._stack + (context,))

    def make_err(self, msg: str) -> _LeafError:
        """Create an error using the current context."""
        return _LeafError(self._stack, msg)


Result = result.Result[T, Iterator[_Error]]


def Err(cs: ContextStack, msg: str) -> Result[T]:
    """Create an error with context."""
    return result.Err(iter([cs.make_err(msg)]))


def add_err(err: _Error, errs: Iterator[_Error]) -> Iterator[_Error]:
    """Add an error to the first set of errors produced by an iterator."""
    try:
        yield next(errs) + err
    except StopIteration:  # pragma: no cover
        yield err
    yield from errs


Fn = Callable[[], Result[Any]]
Collectable = Union[Iterator[Fn], Iterable[Fn]]


def collect_all(fns: Collectable) -> Result[List[Any]]:
    """
    Lazily evaluate a series of functions and return the results.

    If any function returns an error, return an error.
    """
    vs = []
    fns = iter(fns)
    for fn in fns:
        v = fn()
        if v.is_err():
            # Return early if any ds fails.
            # Create an iterator over the rest of the errors.
            extra_errs = (fn().map(lambda _: iter(())).value for fn in fns)
            # Yield errors breadth-first.
            return result.Err(
                round_robin(itertools.chain((v.unwrap_err(),), extra_errs))
            )
        vs.append(v.unwrap())
    return Ok(vs)


def collect_any_it(fns: Collectable) -> Result[Iterator[Any]]:
    """
    Lazily evaluate a series of functions and return the results.

    If any function returns ok, return ok.
    """
    errs = []
    fns = iter(fns)
    for fn in fns:
        v = fn()
        if v.is_ok():
            # Return early if any ds succeeds.
            # Create an iterator over the rest of the successes.
            extra_vs = map(
                result.Result.unwrap, filter(result.Result.is_ok, (fn() for fn in fns))
            )
            # Yield errors breadth-first.
            return Ok(itertools.chain((v.unwrap(),), extra_vs))
        errs.append(v.unwrap_err())
    return result.Err(map(_CompositeError.__call__, round_robin_group(errs)))


def collect_any(fns: Collectable) -> Result[Any]:
    """
    Lazily evaluate a series of functions and return the results.

    If any function returns ok, return ok.
    """
    result = collect_any_it(fns)
    if result.is_ok():
        return Ok(next(result.unwrap()))
    return result


def unwrap(exc: Callable[[Tree[str, str]], Exception], value: Result[T]) -> T:
    """Unwrap a result, raising an exception if it is not Ok."""
    if value.is_ok():
        return value.unwrap()
    raise exc(_treeify(value.unwrap_err()))


def join(value: Result[Result[T]]) -> Result[T]:
    """Flatten a Result[Result] into a Result."""
    if value.is_ok():
        return value.unwrap()
    return result.Err(value.unwrap_err())


def _treeify(
    errs: Iterator[_Error], max_errors: Optional[int] = None
) -> Tree[str, str]:
    tree: Tree[str, str] = Tree()

    def add(err: _LeafError) -> None:
        tree[err.path] = err.msg

    for err, _ in zip(
        errs, range(max_errors) if max_errors is not None else itertools.repeat(0)
    ):
        err.map_(add)
    return tree
