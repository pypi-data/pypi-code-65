from typing import Dict, List

from .i_rule import IRule


class UpperCaseTableRule(IRule):

    @property
    def url(self) -> str:
        return "https://wiki.postgresql.org/wiki/Don%27t_Do_This#Don.27t_use_upper_case_table_or_column_names"

    def process(self) -> Dict:
        tables = self._list_tables()

        culprits: List[str] = []

        for table in tables:
            if self._has_upper_letters(table):
                culprits.append(table)

        if culprits:
            self.infos['details'] = ', '.join(culprits)
            return self.infos

        return {}

    def _has_upper_letters(self, string: str) -> bool:
        return any(c.isupper() for c in string)

    def _list_tables(self) -> List[str]:
        sql = """
        SELECT tablename
        FROM pg_catalog.pg_tables
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema');
        """
        with self.connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                tables = cursor.fetchall()

        return [table[0] for table in tables]
