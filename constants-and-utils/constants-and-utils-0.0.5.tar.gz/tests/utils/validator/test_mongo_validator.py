from typing import Any, List
from unittest import TestCase
from bson import ObjectId
from constants_and_utils.utils.validator import MongoValidator


class BaseValidator(TestCase):

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
        v = MongoValidator(schema_test)

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

    def test_validator_mongo_id(self):
        key = 'mongo_id'
        success_value = [ObjectId()]
        failed_values = [True, 'Sky', 948293]

        self.validation(key, success_value, failed_values)
