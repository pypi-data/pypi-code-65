from .database_encoding_rule import DatabaseEncodingRule
from .inheritance_rule import InheritanceRule
from .rules_rule import RulesRule
from .upper_case_column_rule import UpperCaseColumnRule
from .upper_case_table_rule import UpperCaseTableRule

__all__ = [
    'UpperCaseTableRule',
    'UpperCaseColumnRule',
    'DatabaseEncodingRule',
    'RulesRule',
    'InheritanceRule',
]

_rules = __all__
