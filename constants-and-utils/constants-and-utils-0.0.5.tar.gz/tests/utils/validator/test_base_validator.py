from datetime import datetime, date
from typing import Any, List
from unittest import TestCase
from constants_and_utils.utils.validator import BaseValidator


class ValidatorTestCase(TestCase):

    def validation(
            self,
            key: str,
            success_value: List[Any],
            failed_values: List[Any],
            key_value: Any = True
    ) -> None:
        schema_test = {
            'test': {
                key: key_value,
            }
        }
        v = BaseValidator(schema_test)

        for value in success_value:
            success_dict = {
                'test': value,
            }
            is_valid = v.validate(success_dict)
            self.assertTrue(is_valid)
            self.assertFalse(bool(v.errors))

        for value in failed_values:
            failed_dict = {
                'test': value,
            }
            is_valid = v.validate(failed_dict)
            self.assertFalse(is_valid)
            self.assertTrue(bool(v.errors))

    def test_validator_no_spaces(self):
        key = 'no_spaces'
        success_value = ['Scrum', 'Lean', 'Safe']
        failed_values = ['Design Thinking', 'Brain Storm']

        self.validation(key, success_value, failed_values)

    def test_validator_only_numbers(self):
        key = 'only_numbers'
        success_value = ['12354123', '198401923']
        failed_values = ['049810232A', 'Aguacate']

        self.validation(key, success_value, failed_values)

    def test_validate_multiple(self):
        key = 'multiple'
        success_value = [10, 100, 1000]
        failed_values = [11, 12, 13]

        self.validation(key, success_value, failed_values, 5)

    def test_normalize_date(self):
        schema_test = {
            'date1': {
                'coerce': 'date',
            },
            'date2': {
                'coerce': 'date',
            },
            'date3': {
                'coerce': 'date',
            },
        }

        v = BaseValidator(schema_test)

        success_schema = {
            'date1': datetime(2020, 6, 15),
            'date2': '2020-06-15',
            'date3': date(2020, 6, 15),
        }
        expected_result = {
            'date1': datetime(2020, 6, 15),
            'date2': date(2020, 6, 15),
            'date3': date(2020, 6, 15),
        }
        result = v.normalized(success_schema)
        self.assertEqual(expected_result, result)
