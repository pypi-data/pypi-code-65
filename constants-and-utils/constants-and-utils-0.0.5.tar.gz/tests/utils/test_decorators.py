from unittest import TestCase
from constants_and_utils.utils.decorators import (
    result_to_json
    )


class TestDecorators(TestCase):

    def test_result_to_json_dict(self):
        expected = '{"message": "hi, people"}'

        @result_to_json
        def hello(name):
            return {'message': f'hi, {name}'}

        result = hello('people')

        self.assertEqual(result, expected)
