#! /usr/bin/python3.7.6
from pathlib import Path
from typing import List, Union
from simplysql.base_interfaces.datatable import DataTable
from simplysql.conn_interfaces.connection import Connection


class DataBase(object):
    def __init__(self, path: str = None):
        self._path = self._get_path(Path(path)).absolute()
        self._filename = self._path.stem
        self._filetype = self._path.suffix.split(".")[1]
        self._name = self._path.name

        self._tables = {}
        self.open = True

        self._get_all_tables()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.open = False

    def get_connection(self) -> Connection:
        """
        Get a connection to this Database.

        """

        return Connection(self._path)

    @property
    def name(self) -> str:
        return self._name

    @property
    def tables(self) -> List[DataTable]:
        return self._tables

    def query(self, sql: str, params=None):
        with self.get_connection() as conn:
            conn.execute(sql, params or ())
            return conn.fetchall()

    def create_table(self, table_name: str, columns: List[str], datatypes: List[str]) -> None:
        if not self.has_table(table_name):
            table_id = self.count_tables()
            table = DataTable(self, table_id, table_name, columns, datatypes, False)

            self._tables[table_id] = {"table": table,
                                      "name": table.name,
                                      "columns": table.header(),
                                      "datatypes": table.htypes()}

    def delete_table(self, index: Union[str, int]) -> None:
        if isinstance(index, int):
            table_name = self._tables[index]["name"]
            table_id = index

        if isinstance(index, str):
            table_name = index
            table_id = next((table_id for table_id in self.tables if
                             self.tables[table_id]["name"] == table_name), None)

        if table_id and table_name:
            sql = "DROP TABLE {}".format(table_name)
            self.query(sql)

            del self._tables[table_id]

    def count_tables(self) -> int:
        return len(self._tables)

    def has_table(self, table: str) -> bool:
        return True if table in self.get_tablenames() else False

    def has_tables(self) -> bool:
        return True if self.count_tables() > 0 else False

    def get_tablenames(self) -> List[str]:
        return [table["name"] for table in self._tables.values()]

    def get_tables(self) -> List[DataTable]:
        return [table["table"] for table in self._tables.values()]

    def table(self, index: int) -> DataTable:
        if index in self._tables.keys():
            return self._tables[index]["table"]

        raise IndexError("DataBase has no table with index {}".format(index))

    def first_table(self) -> DataTable:
        if not self.has_tables():
            raise ValueError("DataBase has no tables")

        return self._tables[0]["table"]

    def last_table(self) -> DataTable:
        if not self.has_tables():
            raise ValueError("DataBase has no tables")

        if self.count_tables() > 1:
            return self._tables[self.count_tables()]["table"]

        return self.first_table()

    def attributes(self) -> str:
        return(f"___DataBase___\n"
               f"Name:               {self.name}\n"
               f"Filetype:           {self._filetype}\n"
               f"Path:               {self._path}\n"
               f"Has tables:         {self.has_tables()}\n"
               f"Number of tables:   {self.count_tables()}\n"
               f"Tables:             {self.get_tablenames()}"
               )

    def _get_all_tables(self) -> None:

        with self.get_connection() as conn:
            sql = "SELECT * FROM sqlite_master WHERE type='table'"

            for tables in conn.query(sql):
                sql = "PRAGMA TABLE_INFO({})".format(tables[1])
                table_info = conn.query(sql)

                columns = [table[1] for table in table_info]
                datatypes = [table[2] for table in table_info]

                table_id = self.count_tables()
                table_name = tables[1]

                table = DataTable(self, table_id, table_name, columns, datatypes, True)

                self._tables[table_id] = {"table": table,
                                          "name": table.name,
                                          "columns": table.header(),
                                          "datatypes": table.htypes()}

    def _rename_table_column(self, table_id: int, old_name: str, new_name: str) -> None:
        columns = self._tables[table_id]["columns"]

        columns[columns.index(old_name)] = new_name

    def _get_path(self, path: Path) -> Path:
        if not path:
            raise FileNotFoundError("You must provide a file path.")

        return path

    def __repr__(self) -> str:
        return "DataBase(name={})".format(self.name)
