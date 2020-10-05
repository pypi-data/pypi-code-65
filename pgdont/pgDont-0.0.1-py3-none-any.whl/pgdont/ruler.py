from typing import Dict, List

from psycopg2._psycopg import connection as Connection

from pgdont.rules import *
from pgdont.rules import _rules
from pgdont.rules.i_rule import IRule


class Ruler:

    def __init__(self, connection: Connection) -> None:
        self._cnx: Connection = connection
        self._rules: List[IRule] = []

    def load_rules(self) -> None:
        for rule_name in _rules:
            self._rules.append(globals()[rule_name](self._cnx))

    def process_rule(self, rule: IRule) -> Dict:
        return rule.process()

    def process_all(self) -> List[Dict]:
        result = []
        for rule in self._rules:
            result.append(self.process_rule(rule))
        return result
