from unittest import TestCase
from constants_and_utils.constants.enums import (
    HttpCode,
    Gender
    )


class TestEnums(TestCase):

    def test_http_code(self):
        expected = [
            200, 201, 202, 204, 400,
            401, 402, 403, 404, 405,
            406, 500, 502, 504]

        result = HttpCode.values()

        self.assertEqual(result, expected)

    def test_gender(self):
        expected = ['F', 'M']

        result = Gender.values()

        self.assertEqual(result, expected)
