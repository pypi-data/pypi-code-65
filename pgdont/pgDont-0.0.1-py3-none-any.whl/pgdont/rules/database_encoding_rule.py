from typing import Dict, List

from .i_rule import IRule


class DatabaseEncodingRule(IRule):

    @property
    def url(self) -> str:
        return "https://wiki.postgresql.org/wiki/Don't_Do_This#Don.27t_use_SQL_ASCII"

    def process(self) -> Dict:
        encoding = self._get_encoding()

        if 'SQL_ASCII' == encoding:
            self.infos['details'] = f'Encoding: {encoding}'
            return self.infos

        return {}

    def _get_encoding(self) -> str:
        sql = """
        SHOW SERVER_ENCODING;
        """
        with self.connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchone()
