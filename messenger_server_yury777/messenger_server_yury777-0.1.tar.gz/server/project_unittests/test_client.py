import sys
import os
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from general.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from client import create_presence, process_ans


class TestClass(unittest.TestCase):
    def test_correct_request(self):
        test = create_presence()
        test[TIME] = 2
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 2, USER: {ACCOUNT_NAME: 'Client'}})

    def test_200_answer(self):
        self.assertEqual(process_ans({RESPONSE: 200}), '200 : OK')

    def test_400_answer(self):
        self.assertEqual(process_ans({RESPONSE: 400, ERROR: 'Invalid Request'}), '400 : Invalid Request')

    def test_no_response(self):
        with self.assertRaises(ValueError):
            process_ans({})


if __name__ == '__main__':
    unittest.main()
