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

"""Tests for ConstList.

These work by using mypy ignore statements for code that should break, and
relying on mypy to catch "useless ignore" statements
"""

from __future__ import annotations
import typing

from constprotocol import ConstList


class MyList(list):
    pass


def test_const_list_paramater() -> None:
    """Test passing various kinds into a function that returns a ConstList."""

    def func(l: ConstList[str]) -> None:
        pass

    # Plain list does work
    func(['a', 'b'])

    # A ConstList does work
    c: ConstList[str] = ['1', '2']
    func(c)

    # Sequence doesn't work, because it doesn't implement add or copy
    a: typing.Sequence[str] = ['str']
    func(a)  # type: ignore

    # Set doesn't work
    b = {'a', 'b'}
    func(b)  # type: ignore

    # Dict keys don't work
    func({'a': 'b'}.keys())  # type: ignore


def test_const_list_return() -> None:
    """Test returning a ConstList and using that value."""
    def func() -> ConstList[str]:
        return ['a', 'b', 'c']

    a = func()

    # Does not have an append method
    a.append('d')  # type: ignore

    # Does not have an iadd method
    a += ['b']  # type: ignore

    # Works, since a is not mutated 
    b: ConstList[str] = a + ['a']

    # Does not have an append method
    b.append('d')  # type: ignore

    # Works, since a is not mutated 
    c = func() + ['d']
    c.append('e')
    assert c == ['a', 'b', 'c', 'd', 'e']

    # With a custom class
    d: ConstList[str] = MyList(['a', 'b'])
    e = d + ['c']