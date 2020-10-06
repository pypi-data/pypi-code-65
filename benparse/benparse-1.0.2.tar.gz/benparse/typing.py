"""Type aliases used by :mod:`benparse`

The `BencodeParamObject*` types are used used as function arguments to
:func:`~benparse.dump` and :func:`~benparse.dumps`

The `BencodeReturnObject*` types are returned by :func:`~benparse.load`
and :func:`~benparse.loads` when the ``encoding`` param is `None`
(default)

The `BencodeReturnObjectDecoded*` types are returned by
:func:`~benparse.load` and :func:`~benparse.loads` when the ``encoding``
param is given

Issues
------

Type errors when using load or loads
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When using the object returned by :func:`~benparse.load` or
:func:`~benparse.loads`, you may get type errors about missing
attributes or it being an incompatible type

This is caused because these functions return a Union that can be many
different types

There are two ways that you can resolve this:
    * Assert that the type of the object matches what it's supposed to
      be::

        import benparse

        # torrent files are always dicts
        with open('debian.torrent', 'rb') as file:
            torrent_dict = benparse.load(file)

        # raise an error if it's not a dict
        #
        # if this isn't included, mypy would return a bunch of \
missing-attribute
        # errors
        assert isinstance(torrent_dict, dict)

        for key in torrent_dict.keys():
            print(key)

    * Manually set the expected type if you don't care about handling
      unexpected input::

        from typing import Any, Dict

        import benparse

        # torrent files are always dicts
        with open('debian.torrent', 'rb') as file:
            # manually set the expected type, and ignore errors about \
it being
            # incompatible with the return value
            torrent_dict: Dict[bytes, Any] = benparse.load(file)  \
# type:ignore

        # if torrent_dict isn't actually a dict, this will raise an \
exception
        for key in torrent_dict.keys():
            print(key)

See these issues for more information:
`python/typing#566 <https://github.com/python/typing/issues/566>`_,
`python/mypy#1693 <https://github.com/python/mypy/issues/1693>`_
"""

import typing as _t

# the ignored types are ignored because mypy doesn't support recursive
# types
#
# see https://github.com/python/mypy/issues/731
#
# until this functionally is added, mypy is currently interpreting the
# forward references as type ``Any``

BencodeParamObjectNested = _t.Union[  # type: ignore
    bytes, str, int,
    _t.Sequence['BencodeParamObjectNested'],  # type: ignore
    # mapping keys are invariant, so a Union and the individual types
    # must be specified separately
    _t.Mapping[
        _t.Union[bytes, str], 'BencodeParamObjectNested'  # type: ignore
    ],
    _t.Mapping[bytes, 'BencodeParamObjectNested'],  # type: ignore
    _t.Mapping[str, 'BencodeParamObjectNested']  # type: ignore
]
"""Nested type accepted by :func:`~benparse.dump` and
:func:`~benparse.dumps`

This is the type that is accepted within lists/dicts
"""

BencodeParamObject = _t.Optional[BencodeParamObjectNested]  # type: ignore
"""Complete type accepted by :func:`~benparse.dump` and
:func:`~benparse.dumps`

Similar to :data:`BencodeParamObjectNested`, except it also accepts
`None` by itself (not within lists/dicts)
"""


BencodeReturnObjectNested = _t.Union[  # type: ignore
    bytes, int,
    _t.Tuple['BencodeReturnObjectNested', ...],  # type: ignore
    _t.Dict[bytes, 'BencodeReturnObjectNested']  # type: ignore
]
"""Nested type returned by :func:`~benparse.load` and
:func:`~benparse.loads` when ``encoding`` is `None` (default)

This is the type that is used within lists/dicts
"""

BencodeReturnObject = _t.Optional[BencodeReturnObjectNested]  # type: ignore
"""Complete type returned by :func:`~benparse.load` and
:func:`~benparse.loads` when ``encoding`` is `None` (default)

Similar to :data:`BencodeReturnObjectNested`, except it can also return
`None` by itself (not within lists/dicts)
"""


BencodeReturnObjectDecodedNested = _t.Union[  # type: ignore
    str, int,
    _t.Tuple['BencodeReturnObjectDecodedNested', ...],  # type: ignore
    _t.Dict[str, 'BencodeReturnObjectDecodedNested']  # type: ignore
]
"""Nested type returned by :func:`~benparse.load` and
:func:`~benparse.loads` when ``encoding`` is given

This is the type that is used within lists/dicts
"""

BencodeReturnObjectDecoded = _t.Optional[  # type: ignore
    BencodeReturnObjectDecodedNested
]
"""Complete type returned by :func:`~benparse.load` and
:func:`~benparse.loads` when ``encoding`` is given

Similar to :data:`BencodeReturnObjectDecodedNested`, except it can also
return `None` by itself (not within lists/dicts)
"""
