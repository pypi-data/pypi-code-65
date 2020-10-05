# dbnomics-fetcher-toolbox
# Toolbox of functions and data types helping writing DBnomics fetchers.
# By: Christophe Benz <christophe.benz@cepremap.org>
#
# Copyright (C) 2019 Cepremap
# https://git.nomics.world/dbnomics/dbnomics-fetcher-toolbox
#
# dbnomics-fetcher-toolbox is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# dbnomics-fetcher-toolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Utility functions."""

from typing import Any, Callable, Dict, Iterable, Mapping, Optional, TypeVar

T = TypeVar("T")


def find(
    predicate: Callable[[T], bool], items: Iterable[T], default=None
) -> Optional[T]:
    """Find the first item in ``items`` satisfying ``predicate(item)``.

    Return the found item, or return ``default`` if no item was found.

    >>> find(lambda item: item > 2, [1, 2, 3, 4])
    3
    >>> find(lambda item: item > 10, [1, 2, 3, 4])
    >>> find(lambda item: item > 10, [1, 2, 3, 4], default=42)
    42
    """
    for item in items:
        if predicate(item):
            return item
    return default


K = TypeVar("K")
V = TypeVar("V")


def without_empty_values(mapping: Mapping[K, V]) -> Dict[K, V]:
    """Return a ``dict`` built from ``mapping`` without its empty values.

    This function does not apply recursively.

    Testing emptiness of values is done by ``is_empty``.

    >>> without_empty_values(  # doctest: +NORMALIZE_WHITESPACE
    ...     {'name': 'Robert', 'children': None, 'age': 42,
    ...     'nb_gold_medals': 0, 'hobbies': [],
    ...     'houses': [{'city': 'Dallas'}],
    ...     'notes': {'maths': 'A', 'tech': None}})
    {'name': 'Robert', 'age': 42, 'nb_gold_medals': 0, 'houses': [{'city': 'Dallas'}],
     'notes': {'maths': 'A', 'tech': None}}
    """
    return {k: v for k, v in mapping.items() if not is_empty(v)}


def is_empty(value: Any) -> bool:
    """Return ``True`` if ``value`` is empty.

    Empty values are ``[]``, ``{}``, ``None``, ``""``, but not ``False``, ``0``.

    >>> is_empty(0)
    False
    >>> is_empty(1)
    False
    >>> is_empty([])
    True
    >>> is_empty([1])
    False
    >>> is_empty({})
    True
    >>> is_empty({'a': 1})
    False
    >>> is_empty('')
    True
    >>> is_empty('hi')
    False
    >>> is_empty(set())
    True
    >>> is_empty({1})
    False
    >>> is_empty(None)
    True
    """
    if value is None:
        return True
    if isinstance(value, (list, dict, set, str)):
        return not bool(value)
    return False
