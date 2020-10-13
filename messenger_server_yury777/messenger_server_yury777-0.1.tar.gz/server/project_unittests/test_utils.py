import sys
import os
import unittest
import json

sys.path.append(os.path.join(os.getcwd(), '..'))
from general.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE, ENCODING
from general.utils import receive_message, send_message


class TestSocket:
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message = None

    def send(self, message_to_send):
        json_test_message = json.dumps(self.test_dict)
        self.encoded_message = json_test_message.encode(ENCODING)
        self.received_message = message_to_send

    def recv(self, max_len):
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(ENCODING)


class Tests(unittest.TestCase):
    test_dict_send = {
        ACTION: PRESENCE,
        TIME: 2,
        USER: {
            ACCOUNT_NAME: 'test_test'
        }
    }
    test_dict_recv_correct = {RESPONSE: 200}
    test_dict_recv_error = {
        RESPONSE: 400,
        ERROR: 'invalid request'
    }

    def test_send_message(self):
        test_socket = TestSocket(self.test_dict_send)
        send_message(test_socket, self.test_dict_send)
        self.assertEqual(test_socket.encoded_message, test_socket.received_message)
        with self.assertRaises(Exception):
            send_message(test_socket, test_socket)

    def test_get_message(self):
        test_sock_correct = TestSocket(self.test_dict_recv_correct)
        test_sock_error = TestSocket(self.test_dict_recv_error)
        self.assertEqual(receive_message(test_sock_correct), self.test_dict_recv_correct)
        self.assertEqual(receive_message(test_sock_error), self.test_dict_recv_error)


if __name__ == '__main__':
    unittest.main()
