"""Common utility functions for dealing with iterators."""

import itertools
from typing import (
    Callable,
    Dict,
    Iterator,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypeVar,
    Union,
    cast,
)

T = TypeVar("T")
S = TypeVar("S")


def zip_strict(
    required_ts: Sequence[T],
    optional_ts: Sequence[T],
    var_ts: Optional[T],
    ss: Sequence[S],
) -> Iterator[Tuple[T, S]]:
    """
    Zip required, optional and variadic elements with a supplied sequence.

    Raises if:
      - the sequence contains fewer than the required number of elements;
      - the sequence contains more than the required + optional number of
        elements and no variadic element is supplied.
    """
    if len(ss) < len(required_ts):
        raise ValueError(
            "too few elements ({}) - expected at least {}".format(
                len(ss), len(required_ts)
            )
        )
    if var_ts is not None:
        return zip(
            itertools.chain(
                iter(required_ts), iter(optional_ts), itertools.repeat(var_ts)
            ),
            ss,
        )
    ts = [*required_ts, *optional_ts]
    if len(ss) > len(ts):
        raise ValueError(
            "too many elements ({}) - expected at most {}".format(len(ss), len(ts))
        )
    return zip(ts, ss)


K = TypeVar("K")


def zip_strict_dict(
    required_ts: Mapping[K, T],
    optional_ts: Mapping[K, T],
    var_ts: Optional[T],
    ss: Mapping[K, S],
) -> Dict[K, Tuple[T, S]]:
    """
    Zip required, optional, and variadic key/value pairs with a supplied mapping.

    Raises if:
      - the mapping is missing required keys;
      - the mapping contains keys not present in the set of required or optional
        keys and no variadic element is supplied.
    """

    def show_if(msg: str, keys: Set[K]) -> Optional[str]:
        return msg.format(", ".join(map(str, keys))) if keys else None

    missing_keys = show_if("missing keys '{}'", set(required_ts) - set(ss))
    ts = {**required_ts, **optional_ts}
    unexpected_keys = None
    if var_ts is None:
        unexpected_keys = show_if("unexpected keys '{}'", set(ss) - set(ts))
    if missing_keys or unexpected_keys:
        raise ValueError(
            "key mismatch - {}".format(
                ", ".join((msg for msg in (missing_keys, unexpected_keys) if msg))
            )
        )
    # Either var_ts is set, or it is None and all keys in ss are present in ts.
    return {k: (ts.get(k, cast(T, var_ts)), ss[k]) for k in ss}


def divide_list(fn: Callable[[T], bool], ts: Sequence[T]) -> Tuple[List[T], List[T]]:
    """Divide a list into elements that meet a predicate and those that don't."""
    predicate_met: List[T] = []
    predicate_not_met: List[T] = []
    for t in ts:
        if fn(t):
            predicate_met.append(t)
        else:
            predicate_not_met.append(t)
    return (predicate_met, predicate_not_met)


def round_robin(iterators: Iterator[Iterator[T]]) -> Iterator[T]:
    """
    Round-robin yield from a list of iterators.

    Yield a value from each iterator in turn until all iterators are exhausted.
    For example:

    >>> list(round_robin(iter([iter([1,2,3]), iter(['a', 'b']), iter(['x'])])))
    [1, 'a', 'x', 2, 'b', 3]
    """
    its: Union[Iterator[Iterator[T]], List[Iterator[T]]] = iterators
    while its:
        new_its = []
        for it in its:
            try:
                yield next(it)
            except StopIteration:
                continue
            new_its.append(it)
        its = new_its


def round_robin_group(iterators: Sequence[Iterator[T]]) -> Iterator[List[T]]:
    """
    Yield lists containing one value from each of a list of iterators.

    For example:

    >>> list(round_robin_group([iter([1, 2, 3]), iter(['a', 'b']), iter(['x'])]))
    [[1, 'a', 'x'], [2, 'b'], [3]]
    """
    while iterators:
        group = []
        new_its = []
        for it in iterators:
            try:
                group.append(next(it))
            except StopIteration:
                continue
            new_its.append(it)
        if group:
            yield group
        iterators = new_its
