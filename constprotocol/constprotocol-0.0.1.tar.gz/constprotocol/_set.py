# Copyright 2020 Dylan Baker

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Implementation of an immutable Set."""

from __future__ import annotations

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore

import typing

__all__ = [
    'ConstSet',
]

T = typing.TypeVar('T')


class ConstSet(Protocol[T]):

    """A Protocol for an immutable Set.

    """

    def __iter__(self) -> typing.Iterator[T]: ...

    def __contains__(self, item: T) -> bool: ...

    def __len__(self) -> int: ...
    
    def __and__(self, value: typing.AbstractSet[T]) -> typing.AbstractSet[T]: ...

    def __or__(self, value: typing.AbstractSet[T]) -> typing.AbstractSet[T]: ...

    def __xor__(self, value: typing.AbstractSet[T]) -> typing.AbstractSet[T]: ...

    def __lt__(self, value: typing.AbstractSet[T]) -> bool: ...
    def __le__(self, value: typing.AbstractSet[T]) -> bool: ...
    def __eq__(self, value: object) -> bool: ...
    def __ne__(self, value: object) -> bool: ...
    def __ge__(self, value: typing.AbstractSet[T]) -> bool: ...
    def __gt__(self, value: typing.AbstractSet[T]) -> bool: ...

    def copy(self) -> typing.AbstractSet[T]: ...

    @typing.overload
    def difference(self, other: typing.AbstractSet[T]) -> typing.AbstractSet[T]: ...
    @typing.overload
    def difference(self, other: ConstSet[T]) -> typing.AbstractSet[T]: ...

    @typing.overload
    def intersection(self, other: typing.AbstractSet[T]) -> typing.AbstractSet[T]: ...
    @typing.overload
    def intersection(self, other: ConstSet[T]) -> typing.AbstractSet[T]: ...

    @typing.overload
    def isdisjoint(self, other: typing.AbstractSet[T]) -> bool: ...
    @typing.overload
    def isdisjoint(self, other: ConstSet[T]) -> bool: ...

    @typing.overload
    def issubset(self, other: typing.AbstractSet[T]) -> bool: ...
    @typing.overload
    def issubset(self, other: ConstSet[T]) -> bool: ...

    @typing.overload
    def issuperset(self, other: typing.AbstractSet[T]) -> bool: ...
    @typing.overload
    def issuperset(self, other: ConstSet[T]) -> bool: ...

    @typing.overload
    def symmetric_difference(self, other: typing.AbstractSet[T]) -> typing.AbstractSet[T]: ...
    @typing.overload
    def symmetric_difference(self, other: ConstSet[T]) -> typing.AbstractSet[T]: ...

    @typing.overload
    def union(self, other: typing.AbstractSet[T]) -> typing.AbstractSet[T]: ...
    @typing.overload
    def union(self, other: ConstSet[T]) -> typing.AbstractSet[T]: ...