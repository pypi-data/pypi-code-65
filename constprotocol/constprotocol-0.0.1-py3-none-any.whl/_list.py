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

"""Implementation of an immutable List."""

from __future__ import annotations

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore

import typing

__all__ = [
    'ConstList',
]

T = typing.TypeVar('T')


class ConstList(Protocol[T]):

    """A Protocol for an immutable List.

    Provides no methods for mutating the list, although the fact is that is a
    list and can be mutated, even if mypy says that's an error.

    mypy will not correctly recognize that a slice returns a ConstList, it is
    up to you to ensure that you cast in that case.
    """

    def __iter__(self) -> typing.Iterator[T]: ...

    @typing.overload
    def __getitem__(self, index: int) -> T: ...
    @typing.overload
    def __getitem__(self, index: slice) -> typing.List[T]: ...

    def __contains__(self, item: T) -> bool: ...

    def __reversed__(self) -> typing.Iterator[T]: ...

    def __len__(self) -> int: ...

    def __add__(self, other: typing.List[T]) -> typing.List[T]: ...

    def count(self, item: T) -> int: ...

    def index(self, item: T) -> int: ...

    def copy(self) -> typing.List[T]: ...