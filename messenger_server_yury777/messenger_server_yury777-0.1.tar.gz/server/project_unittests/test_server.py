import sys
import os
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from general.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from server2 import process_messages


class TestServer(unittest.TestCase):
    error_dict = {
        RESPONSE: 400,
        ERROR: 'invalid request'
    }
    correct_dict = {RESPONSE: 200}

    def test_no_action(self):
        self.assertEqual(process_messages(
            {TIME: '2', USER: {ACCOUNT_NAME: 'Client'}}), self.error_dict)

    def test_wrong_action(self):
        self.assertEqual(process_messages(
            {ACTION: 'Some Action', TIME: '2', USER: {ACCOUNT_NAME: 'Client'}}), self.error_dict)

    def test_no_time(self):
        self.assertEqual(process_messages(
            {ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Client'}}), self.error_dict)

    def test_no_user(self):
        self.assertEqual(process_messages(
            {ACTION: PRESENCE, TIME: '2'}), self.error_dict)

    def test_unknown_user(self):
        self.assertEqual(process_messages(
            {ACTION: PRESENCE, TIME: 2, USER: {ACCOUNT_NAME: 'Guest'}}), self.error_dict)

    def test_correct(self):
        self.assertEqual(process_messages(
            {ACTION: PRESENCE, TIME: 2, USER: {ACCOUNT_NAME: 'Client'}}), self.correct_dict)


if __name__ == '__main__':
    unittest.main()
