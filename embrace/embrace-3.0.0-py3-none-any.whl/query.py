#  Copyright 2020 Oliver Cope
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from collections import namedtuple
from functools import partial
from itertools import chain
from itertools import cycle
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Union
from typing import Tuple
import sys

from .parsing import BindParams, compile_bind_parameters
from . import exceptions
from embrace.util import toposort


known_styles: Dict[type, str] = {}

_joinedload = namedtuple("_joinedload", "target attr source arity")


def get_param_style(conn: Any) -> str:

    conncls = conn.__class__
    try:
        return known_styles[conncls]
    except KeyError:
        modname = conncls.__module__
        while modname:
            try:
                style = sys.modules[modname].paramstyle  # type: ignore
                known_styles[conncls] = style
                return style
            except AttributeError:
                if "." in modname:
                    modname = modname.rsplit(".", 1)[0]
                else:
                    break
    raise TypeError(f"Can't find paramstyle for connection {conn!r}")


class Query:

    name: str
    metadata: Mapping
    sql: str
    source: str

    def __init__(self, name, statements, source, metadata=None, **kwmetadata):
        self.name = name
        self.metadata = dict(metadata or {}, **kwmetadata)
        self.result_map = None
        self.statements = statements
        self.source = source
        self._conn = None
        self.get_row_mapper = None

    def prepare(self, paramstyle, kw: Mapping) -> List[Tuple[str, BindParams]]:
        return [
            compile_bind_parameters(paramstyle, s, kw) for s in self.statements
        ]

    def bind(self, conn) -> "Query":
        """
        Return a copy of the query bound to a database connection
        """
        cls = self.__class__
        bound = cls.__new__(cls)
        bound.__dict__ = self.__dict__.copy()
        bound._conn = conn
        return bound

    def returning(
        self,
        row_spec: Sequence[Callable],
        joins: Optional[Union[_joinedload, Sequence[_joinedload]]] = None,
        positional=False,
        key_columns: Optional[List[Tuple[str]]] = None,
        split_on=["id"],
    ) -> "Query":
        """
        Return a copy of the query with a changed result type
        """
        cls = self.__class__
        q = cls.__new__(cls)
        q.__dict__ = self.__dict__.copy()
        if isinstance(joins, _joinedload):
            joins = [joins]
        q.get_row_mapper = partial(
            row_mapper, row_spec, joins, positional, split_on, key_columns,
        )
        return q

    def one(self, conn=None, *, debug=False, **kwargs):
        return self(conn, debug=debug, _result="one", **kwargs)

    def first(self, conn=None, *, debug=False, **kwargs):
        return self(conn, debug=debug, _result="first", **kwargs)

    def one_or_none(self, conn=None, *, debug=False, **kwargs):
        return self(conn, debug=debug, _result="one_or_none", **kwargs)

    def many(self, conn=None, *, debug=False, **kwargs):
        return self(conn, debug=debug, _result="many", **kwargs)

    def scalar(self, conn=None, *, debug=False, **kwargs):
        return self(conn, debug=debug, _result="scalar", **kwargs)

    def affected(self, conn=None, *, debug=False, **kwargs):
        return self(conn, debug=debug, _result="affected", **kwargs)

    def column(self, conn=None, *, debug=False, **kwargs):
        return self(conn, debug=debug, _result="column", **kwargs)

    def cursor(self, conn=None, *, debug=False, **kwargs):
        return self(conn, debug=debug, _result="cursor", **kwargs)

    def __call__(self, conn=None, *, debug=False, _result=None, **kw):
        if conn is None:
            conn = self._conn
            if conn is None:
                raise TypeError(
                    "Query must be called with a connection argument"
                )
        rt = _result or self.metadata["result"]

        paramstyle = get_param_style(conn)
        cursor = conn.cursor()

        for sqltext, bind_params in self.prepare(paramstyle, kw):
            if debug:
                import textwrap

                print(
                    f"Executing \n{textwrap.indent(sqltext, '    ')} with {bind_params!r}",
                    file=sys.stderr,
                )
            try:
                cursor.execute(sqltext, bind_params)
            except BaseException:
                _handle_exception(conn)

        if self.get_row_mapper:
            row_mapper = self.get_row_mapper(cursor.description)
        else:
            row_mapper = None

        if rt == "one":
            row = cursor.fetchone()
            if row is None:
                raise exceptions.NoResultFound()
            if cursor.fetchone() is not None:
                raise exceptions.MultipleResultsFound()
            if row_mapper:
                return next(row_mapper([row]))
            return row

        if rt == "first":
            row = cursor.fetchone()
            if row_mapper:
                return next(row_mapper([row]))
            return row

        if rt == "many":
            if row_mapper:
                return row_mapper(iter(cursor.fetchone, None))
            return iter(cursor.fetchone, None)

        if rt == "one_or_none":
            row = cursor.fetchone()
            if cursor.fetchone() is not None:
                raise exceptions.MultipleResultsFound()
            if row_mapper:
                return next(row_mapper([row]))
            return row

        if rt == "scalar":
            result = cursor.fetchone()
            if result is None:
                raise exceptions.NoResultFound()
            if isinstance(result, Mapping):
                value = next(iter(result.values()))
            elif isinstance(result, Sequence):
                value = result[0]
            else:
                raise TypeError(
                    f"Can't find first column for row of type {type(row)}"
                )
            if row_mapper:
                return next(row_mapper([value]))
            return value

        if rt == "column":
            first = cursor.fetchone()
            if first:
                if isinstance(first, Mapping):
                    key = next(iter(first))
                elif isinstance(first, Sequence):
                    key = 0
                else:
                    raise TypeError(
                        f"Can't find first column for row of type {type(row)}"
                    )
                rows = (
                    row[key]
                    for row in chain([first], iter(cursor.fetchone, None))
                )
                if row_mapper:
                    return row_mapper(rows)
                return rows
            return iter([])

        if rt == "affected":
            return cursor.rowcount

        if rt == "cursor":
            return cursor

        raise ValueError(f"Unsupported result type: {rt}")


def _handle_exception(conn):
    """
    We have an exception of unknown type, probably raised
    from the dbapi module
    """
    exc_type, exc_value, exc_tb = sys.exc_info()
    if exc_type and exc_value:
        classes = [exc_type]
        while classes:
            cls = classes.pop()
            clsname = cls.__name__

            if clsname in exceptions.pep_249_exception_names:
                newexc = exceptions.pep_249_exception_names[clsname]()
                newexc.args = getattr(exc_value, "args", tuple())
                raise newexc.with_traceback(exc_tb) from exc_value
            classes.extend(getattr(cls, "__bases__", []))

        raise exc_value.with_traceback(exc_tb)


def row_mapper(row_spec, joins, positional, split_on, key_columns, description):

    if not isinstance(row_spec, tuple):
        row_spec = (row_spec,)

    is_multi = len(row_spec) > 1
    column_names: List[str] = [d[0] for d in description]
    split_points = []

    if is_multi:
        if not isinstance(split_on, Sequence):
            raise TypeError(f"Expected sequence, got {split_on!r}")

        isplit_on = cycle(split_on)
        last_split = 0
        next_split = next(isplit_on)
        for ix, col in enumerate(column_names):
            if ix > 0 and col.lower() == next_split:
                split_points.append(slice(last_split, ix))
                last_split = ix
                next_split = next(isplit_on)
        split_points.append(slice(last_split, ix + 1))
        mapped_column_names = [tuple(column_names[i]) for i in split_points]
    else:
        mapped_column_names = [tuple(column_names)]

    if joins:
        if not is_multi:
            raise TypeError(
                "joins may only be set when there are multiple return types"
            )

        def _maprows(rows):
            if positional:
                object_rows = ([row[i] for i in split_points] for row in rows)
            else:

                def _make_dict_items():
                    for row in rows:
                        col_data = list(zip(column_names, row))
                        yield list(
                            map(dict, map(col_data.__getitem__, split_points))  # type: ignore
                        )

                object_rows = _make_dict_items()

            return group_by_and_join(
                mapped_column_names,
                row_spec,
                joins,
                object_rows,
                positional=positional,
                key_columns=key_columns,
            )

    else:
        make_object = object_maker(
            mapped_column_names, row_spec, positional, key_columns
        )

        def _maprows(rows):
            if positional:
                if is_multi:
                    for row in rows:
                        items = [row[i] for i in split_points]
                        yield tuple(map(make_object, enumerate(items)))
                else:
                    for row in rows:
                        yield make_object((0, row))

            else:
                if is_multi:
                    for row in rows:
                        col_data = list(zip(column_names, row))
                        dictitems = map(
                            dict, map(col_data.__getitem__, split_points)  # type: ignore
                        )
                        yield tuple(map(make_object, enumerate(dictitems)))
                else:
                    for row in rows:
                        yield make_object((0, dict(zip(column_names, row))))

    return _maprows


def group_by_and_join(
    mapped_column_names: List[Tuple[str, ...]],
    row_spec,
    join_spec,
    object_rows: Iterable[List[Union[Tuple, Dict]]],
    _marker=object(),
    positional=False,
    key_columns: Optional[List[Tuple[str]]] = None,
):

    make_object = object_maker(
        mapped_column_names, row_spec, positional, key_columns
    )
    join_spec = [
        _joinedload(*i) if isinstance(i, tuple) else i for i in join_spec
    ]
    indexed_joins = translate_to_column_indexes(row_spec, join_spec)
    load_order = list(
        toposort([(t_idx, s_idx) for t_idx, _, s_idx, _ in indexed_joins])
    )
    unjoined_columns = [n for n in range(len(row_spec)) if n not in load_order]
    load_order.extend(unjoined_columns)

    backlinks: Dict[int, Optional[Tuple[int, str, str]]] = {
        ix: None for ix in load_order
    }
    backlinks.update(
        {
            s_idx: (t_idx, attr, arity)
            for t_idx, attr, s_idx, arity in indexed_joins
        }
    )

    last = [_marker] * len(row_spec)
    cur: Dict[int, Any] = {}
    return_columns = sorted(n for n in load_order if backlinks[n] is None)
    single_column = len(return_columns) == 1
    items = None

    for irow, items in enumerate(object_rows):
        matched_until = -1
        for ix, column_index in enumerate(load_order):
            lastitem = last[column_index]
            if lastitem is _marker or lastitem != items[column_index]:
                matched_until = ix
                break

        if matched_until == 0 and irow > 0:
            if single_column:
                yield cur[0]
            else:
                rv: List[Any] = []
                append = rv.append
                for ix in return_columns:
                    if ix in cur:
                        append(cur[ix])
                    else:
                        if positional:
                            append(row_spec[ix](*items[ix]))
                        else:
                            append(row_spec[ix](**items[ix]))
                yield tuple(rv)

        for column_index in load_order[matched_until:]:
            item = items[column_index]
            backlink = backlinks[column_index]
            if backlink:
                values = item if positional else item.values()
                if all(v is None for v in values):
                    cur[column_index] = None
                    continue
            ob = make_object((column_index, item))
            cur[column_index] = ob
            if backlink:
                ref_idx, attr, arity = backlink

                if arity == "*":
                    attrib = getattr(cur[ref_idx], attr, _marker)
                    if attrib is _marker:
                        attrib = []
                        setattr(cur[ref_idx], attr, attrib)
                    attrib.append(ob)
                else:
                    setattr(cur[ref_idx], attr, ob)

        last = items

    if items:
        if single_column:
            yield cur[0]
        else:
            rv = []
            append = rv.append
            for ix in return_columns:
                if ix in cur:
                    append(cur[ix])
                else:
                    append(make_object((ix, items[ix])))
            yield tuple(rv)


def one_to_one(target, attr, source):
    return _joinedload(target, attr, source, "1")


def one_to_many(target, attr, source):
    return _joinedload(target, attr, source, "*")


def translate_to_column_indexes(
    row_spec, join_spec: List[_joinedload]
) -> Sequence[Tuple[int, str, int, str]]:

    row_spec_indexes = {c: ix for ix, c in enumerate(row_spec)}

    def map_column(col: Any) -> int:
        if isinstance(col, int):
            return col
        return row_spec_indexes[col]

    return [
        (map_column(j.target), j.attr, map_column(j.source), j.arity,)
        for j in join_spec
    ]


def object_maker(
    mapped_column_names: List[Tuple[str, ...]],
    row_spec: List[Any],
    positional: bool,
    key_columns: Optional[List[Tuple[str]]],
) -> Callable[[Tuple[int, Union[Tuple, Dict]]], Any]:
    """
    Return a function that constructs the target type from a group of columns.
    The returned function will cache objects (the same input returns the
    same object) so that object identity may be relied on within the scope of a
    single query.
    """

    if key_columns:
        assert len(key_columns) == len(row_spec)
        key_column_positions: List[List[int]] = []
        for item_column_names, item_key_cols, type_ in zip(
            mapped_column_names, key_columns, row_spec
        ):
            key_column_positions.append([])
            for c in item_key_cols:
                try:
                    key_column_positions[-1].append(item_column_names.index(c))
                except ValueError:
                    raise ValueError(
                        f"{c!r} specified in key_columns does not exist "
                        f"in the returned columns for {type_!r}"
                    )

    def object_maker():
        object_cache: Dict[Any, Any] = {}
        ob = None

        # When loading multiple objects, ensure that consecutive items loaded
        # with identical values map to the same object. This makes it possible
        # for joined loads to do the right thing, even if key_columns is not
        # set.
        last_row: Dict[int, Tuple[Any, Any]] = {}
        use_last_row_cache = len(row_spec) > 1

        if positional:
            while True:
                (column_index, item) = yield ob
                if key_columns:
                    key = tuple(
                        item[x] for x in key_column_positions[column_index]
                    )
                    if key in object_cache:
                        ob = object_cache[key]
                    else:
                        ob = object_cache[key] = row_spec[column_index](*item)
                elif use_last_row_cache:
                    try:
                        last_item, last_ob = last_row[column_index]
                    except KeyError:
                        last_item = None, None
                    if last_item == item:
                        ob = last_ob
                    else:
                        ob = row_spec[column_index](*item)
                        last_row[column_index] = item, ob
                else:
                    ob = row_spec[column_index](*item)

        else:
            while True:
                (column_index, item) = yield ob
                if key_columns:
                    key = tuple(item[x] for x in key_columns[column_index])
                    if key in object_cache:
                        ob = object_cache[key]
                    else:
                        ob = object_cache[key] = row_spec[column_index](**item)
                elif use_last_row_cache:
                    try:
                        last_item, last_ob = last_row[column_index]
                    except KeyError:
                        last_item = None, None
                    if last_item == item:
                        ob = last_ob
                    else:
                        ob = row_spec[column_index](**item)
                        last_row[column_index] = item, ob
                else:
                    ob = row_spec[column_index](**item)

    func = object_maker()
    next(func)
    return func.send
