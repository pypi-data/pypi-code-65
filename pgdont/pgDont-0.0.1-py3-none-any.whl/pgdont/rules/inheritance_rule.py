from typing import Dict, List, Tuple

from .i_rule import IRule


class InheritanceRule(IRule):
    @property
    def url(self) -> str:
        return "https://wiki.postgresql.org/wiki/Don%27t_Do_This#Don.27t_use_table_inheritance"

    def process(self) -> Dict:
        inherited_tables = self._get_inherited_tables()

        if len(inherited_tables):
            self.infos['details'] = ', '.join(
                f'{t[0]}:{t[1]}' for t in inherited_tables)
            return self.infos

        return {}

    def _get_inherited_tables(self) -> List[Tuple[str, str]]:
        sql = """
            SELECT
            cn.nspname AS child_schema, c.relname AS child,
            pn.nspname AS parent_schema, p.relname AS parent
            FROM pg_inherits i
            JOIN pg_class AS c ON i.inhrelid=c.oid
            JOIN pg_class as p ON i.inhparent=p.oid
            JOIN pg_namespace pn ON pn.oid = p.relnamespace
            JOIN pg_namespace cn ON cn.oid = c.relnamespace
        """
        with self.connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
