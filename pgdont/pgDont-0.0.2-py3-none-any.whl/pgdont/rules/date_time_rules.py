from typing import Dict, List, Tuple

from psycopg2._psycopg import connection as Connection

from .i_rule import IRule


def get_columns_by_type(connection: Connection,
                          type_name: str) -> List[Tuple[str, str]]:
    sql = """
    SELECT c.table_name, c.column_name
    FROM information_schema.columns c
    WHERE c.table_schema NOT IN ('pg_catalog','information_schema')
    AND data_type = %(type_name)s;
    """
    with connection as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, {'type_name': type_name})
            return cursor.fetchall()


class TimestampWithoutTzRule(IRule):
    @property
    def url(self) -> str:
        return "https://wiki.postgresql.org/wiki/Don%27t_Do_This#Don.27t_use_timestamp_.28without_time_zone.29"

    def process(self) -> Dict:
        columns = get_columns_by_type(
            self.connection, 'timestamp without time zone')

        if columns:
            self.infos['details'] = ', '.join(
                f'{c[0]}:{c[1]}' for c in columns)
            return self.infos

        return {}


class TimetzRule(IRule):
    @property
    def url(self) -> str:
        return "https://wiki.postgresql.org/wiki/Don%27t_Do_This#Don.27t_use_timetz"

    def process(self) -> Dict:
        columns = get_columns_by_type(
            self.connection, 'time with time zone')
        if columns:
            self.infos['details'] = ', '.join(
                f'{c[0]}:{c[1]}' for c in columns)
            return self.infos

        return {}
