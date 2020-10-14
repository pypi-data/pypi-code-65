from typing import List, Type

from beautifultable import BeautifulTable
from pydantic import BaseModel


def print_table_from_list_of_schemas(
    models: List[Type[BaseModel]], keys: List[str] = None, names: List[str] = None
):
    table = BeautifulTable(maxwidth=100)
    rows = len(models)
    table.rows.header = [str(i) for i in range(rows)]
    if rows < 1:
        raise ValueError("Nothing to print")

    first = models[0]
    if names:
        table.columns.header = names
    if not names and keys:
        table.columns.header = keys
    elif not names and not keys:
        keys = list(first.dict().keys())
        table.columns.header = keys
    for i in range(rows):
        table.rows[i] = [str(getattr(models[i], attr)) for attr in keys]
    return table
