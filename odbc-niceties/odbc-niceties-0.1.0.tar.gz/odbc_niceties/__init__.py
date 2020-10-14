__version__ = '0.1.0'

from tabulate import tabulate
import collections
import toolz as tz


class ODBCNicetiesException(Exception):
    "Exception class for database utilities"


def get_column_names(cur):
    if not cur.description:
        raise ODBCNicetiesException("No Column metadata on cursor. "
                                    "Did you execute sql?")
    columns = [column[0] for column in cur.description]

    # If we have duplicate columns things will get strange
    dups = [item for item, count
            in collections.Counter(columns).items()
        if count > 1]
    if dups:
        msg = f"Duplicate Columns in resultset: \n {dups}"
        raise ODBCNicetiesException(msg)

    return columns


def sql_data(cur):
    """with given sql cursor return a list-of-dicts (greedy)."""
    columns = get_column_names(cur)
    return [dict(zip(columns, row))
            for row in cur.fetchall()]


def sql_data_lazy(cur, arraysize=100):
    """with given sql cursor yield an iterator for each row; Return
    maps/dicts."""

    # get column names; only do this once (memoize?)
    columns = get_column_names(cur)

    while True:
        results = cur.fetchmany(arraysize)
        if not results:
            break
        for row in results:
            yield dict(zip(columns, row))


def generate_prepared_insert(table_name: str,
                             field_names: list,
                             ms_quote_cols: bool=False) -> str:
    "Have to keep an eye on silly ms [\\] escaping"
    if ms_quote_cols:
        cols = [f"[{col}]" for col in field_names]
    else:
        cols = [f'"{col}"' for col in field_names]

    cols_str         = ', '.join(cols)
    placeholders     = ['?' for _ in range(len(cols))]
    placeholders_str = ', '.join(placeholders)

    return (f"insert into {table_name}\n"
            f"({cols_str})\n"
            f"values({placeholders_str})")


def generate_ddl(*args):
    raise NotImplementedError


def make_table(something, batch_size=10, pages=False):
    parts = tz.partition_all(batch_size, something)

    for part in parts:
        tab = tabulate(part, headers="keys")
        print("")
        print(tab)

        if pages:
            q = input("'q' to quit, enter to continue.\n")
            if q == "q":
                break
