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

"""Implementation of an immutable Mapping."""

from __future__ import annotations

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore

import typing

__all__ = [
    'ConstMapping',
    'ConstDict',
]

KT = typing.TypeVar('KT')
VT = typing.TypeVar('VT')


class ConstMapping(Protocol[KT, VT]):

    """A Protocol for an immutable Mapping.

    Provides no methods for mutating the mapping, although the fact is that is a
    mapping and can be mutated, even if mypy says that's an error.

    This is different than the Mapping in typing in that it's a Protocol, so
    any object that implements this Protocol  will work correctly.
    """

    def __contains__(self, key: KT) -> bool: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...

    def __iter__(self) -> typing.Iterator[KT]: ...

    def __len__(self) -> int: ...

    def __reversed__(self) -> typing.Iterable[KT]: ...

    # TODO: do we need a MutableMappingProtocol?
    def copy(self) -> typing.MutableMapping[KT, VT]: ...

    def get(self, key: KT, default: typing.Optional[VT]) -> typing.Optional[VT]: ...

    def items(self) -> typing.ItemsView[KT, VT]: ...
    def keys(self) -> typing.KeysView[KT]: ...
    def values(self) -> typing.ValuesView[VT]: ...


class ConstDict(Protocol[KT, VT]):

    """A Protocol for an immutable Mapping.

    Provides no methods for mutating the mapping, although the fact is that is a
    mapping and can be mutated, even if mypy says that's an error.

    This is different than the Mapping in typing in that it's a Protocol, so
    any object that implements this Protocol  will work correctly.
    """

    def __contains__(self, key: KT) -> bool: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...

    def __iter__(self) -> typing.Iterator[KT]: ...

    def __len__(self) -> int: ...

    def __reversed__(self) -> typing.Iterable[KT]: ...

    def copy(self) -> typing.Dict[KT, VT]: ...

    def get(self, key: KT, default: typing.Optional[VT]) -> typing.Optional[VT]: ...

    def items(self) -> typing.ItemsView[KT, VT]: ...
    def keys(self) -> typing.KeysView[KT]: ...
    def values(self) -> typing.ValuesView[VT]: ...