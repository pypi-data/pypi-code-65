from typing import Dict, List, Tuple

from .i_rule import IRule


class UpperCaseColumnRule(IRule):

    @property
    def url(self) -> str:
        return "https://wiki.postgresql.org/wiki/Don%27t_Do_This#Don.27t_use_upper_case_table_or_column_names"

    def process(self) -> Dict:
        columns = self._list_columns()

        culprits: List[str] = []

        for table, column in columns:
            if self._has_upper_letters(column):
                culprits.append(f'{table}::{column}')

        if culprits:
            self.infos['details'] = ', '.join(culprits)
            return self.infos

        return {}

    def _has_upper_letters(self, string: str) -> bool:
        return any(c.isupper() for c in string)

    def _list_columns(self) -> List[Tuple[str, str]]:
        sql = """
        SELECT
               c.relname AS table,
               a.attname AS column
        FROM pg_catalog.pg_attribute a
             JOIN pg_catalog.pg_class c 
             ON (a.attrelid = c.oid)
             JOIN pg_catalog.pg_namespace n 
             ON (c.relnamespace = n.oid)
        WHERE
            c.relkind in ('r','v')
            AND a.attnum > 0
            AND n.nspname NOT IN ('pg_catalog','information_schema')
        """
        with self.connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
