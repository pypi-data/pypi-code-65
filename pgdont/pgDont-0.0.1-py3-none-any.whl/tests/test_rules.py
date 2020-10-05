from unittest.mock import MagicMock, patch

from pgdont.rules import (DatabaseEncodingRule, InheritanceRule, RulesRule,
                          UpperCaseColumnRule, UpperCaseTableRule)

from .database_test_case import DatabaseTestCase


class UpperCaseTableRuleTestCase(DatabaseTestCase):
    def test_it_detects_uppercased_table_names(self):
        rule = UpperCaseTableRule(self._conn)

        result = rule.process()

        self.assertTrue(len(result))
        self.assertIn('TestTableName', result['details'])


class UpperCaseColumnRuleTestCase(DatabaseTestCase):
    def test_it_detects_uppercased_column_names(self):
        rule = UpperCaseColumnRule(self._conn)

        result = rule.process()

        self.assertTrue(len(result))


class DatabaseEncodingRuleTestCase(DatabaseTestCase):

    @patch.object(DatabaseEncodingRule, '_get_encoding')
    def test_it_detects_bad_encoding(self, get_encoding_mock: MagicMock):
        rule = DatabaseEncodingRule(self._conn)

        get_encoding_mock.return_value = 'SQL_ASCII'

        result = rule.process()

        self.assertTrue(len(result))


class RulesRuleTestCase(DatabaseTestCase):
    def test_it_detects_use_of_rules(self):
        rule = RulesRule(self._conn)

        result = rule.process()

        self.assertTrue(len(result))


class InheritanceTestCase(DatabaseTestCase):
    def test_it_detects_use_of_inheritance(self):
        rule = InheritanceRule(self._conn)

        result = rule.process()

        self.assertTrue(len(result))
