from chtoolset._query import _replace_tables, format, tables, table_if_is_simple_query
from collections import defaultdict
from toposort import toposort

def tables_or_sql(replacement):
    try:
        return set(tables(replacement[1], default_database=replacement[0]))
    except Exception as e:
        if replacement[1][0] == '(':
            raise e
        return set([replacement])

class ReplacementsDict(dict):
    def __getitem__(self, key):
        v = super().__getitem__(key)
        if isinstance(v, tuple):
            return (v[0], v[1]() if callable(v[1]) else v[1])
        return v() if callable(v) else v

def replace_tables(sql, replacements, default_database=''):
    if not replacements:
        return format(sql)

    _replacements = ReplacementsDict()
    for k, r in replacements.items():
        rk = k if isinstance(k, tuple) else (default_database, k)
        _replacements[rk] = r if isinstance(r, tuple) else (default_database, r)

    deps = defaultdict(set)
    _tables = tables(sql, default_database=default_database)
    seen_tables = set()
    while _tables:
        table = _tables.pop()
        seen_tables.add(table)
        if table in _replacements:
            replacement = _replacements[table]
            dependent_tables = tables_or_sql(replacement)
            deps[table] |= dependent_tables
            for dependent_table in list(dependent_tables):
                if dependent_table not in seen_tables:
                    _tables.append(dependent_table)
    deps_sorted = list(reversed(list(toposort(deps))))

    if not deps_sorted:
        return format(sql)

    for current_deps in deps_sorted:
        current_replacements = {}
        for r in current_deps:
            if r in _replacements:
                replacement = _replacements[r]
                current_replacements[r] = replacement
                dt = table_if_is_simple_query(replacement[1], default_database=replacement[0])
                if dt:
                    current_replacements[r] = dt
        if current_replacements:
            sql = _replace_tables(sql, current_replacements, default_database=default_database)
    return sql
