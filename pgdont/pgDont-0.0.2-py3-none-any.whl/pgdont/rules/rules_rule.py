from typing import Dict, List, Tuple

from .i_rule import IRule


class RulesRule(IRule):

    @property
    def url(self) -> str:
        return "https://wiki.postgresql.org/wiki/Don%27t_Do_This#Don.27t_use_rules"

    def process(self) -> Dict:
        rules = self._get_rules()

        if len(rules):
            self.infos['details'] = ', '.join(f'{r[0]}:{r[1]}' for r in rules)
            return self.infos

        return {}

    def _get_rules(self) -> List[Tuple[str, str]]:
        sql = """
        SELECT tablename, rulename
        FROM pg_rules
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema');
        """
        with self.connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
