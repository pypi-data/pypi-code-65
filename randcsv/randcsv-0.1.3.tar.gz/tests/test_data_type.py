import unittest
from randcsv.data_type import DataType


class TestDataType(unittest.TestCase):

    def test_data_types(self):
        enum = DataType
        self.assertEqual(enum.integer.value, 'integer')
        self.assertEqual(enum.floating_point.value, 'float')
        self.assertEqual(enum.token.value, 'token')

        self.assertEqual(str(enum.integer), 'integer')
        self.assertEqual(str(enum.floating_point), 'float')
        self.assertEqual(str(enum.token), 'token')
