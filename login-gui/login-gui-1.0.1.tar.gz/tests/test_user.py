#     _________             .__
#    /   _____/____    _____|  |__ _____
#    \_____  \\__  \  /  ___/  |  \\__  \
#    /        \/ __ \_\___ \|   Y  \/ __ \_
#   /_______  (____  /____  >___|  (____  /
#           \/     \/     \/     \/     \/
#     _________       _____  __
#    /   _____/ _____/ ____\/  |_
#    \_____  \ /  _ \   __\\   __\
#    /        (  <_> )  |   |  |
#   /_______  /\____/|__|   |__|
#           \/
#   Copyright (c) 2020.
"""
test of user class
"""
import unittest

from login_gui import User
from login_gui.user import _is_base64


class UserCase(unittest.TestCase):
    """
    Test for user singleton class
    """
    def setUp(self) -> None:
        """
        user setup function
        """
        self.user = User()
        self.user.save('user:password')

    def test_save(self):
        """
        test singleton
        """
        user2 = User()
        user3 = User().save('testuser')

        self.assertEqual(self.user, user2)
        self.assertEqual(self.user.user64, user3)
        self.assertEqual(user2.user64, user3)

    def test_convert_to_string(self):
        """
        test convert to string function
        """
        self.assertEqual(str(self.user), 'dXNlcjpwYXNzd29yZA==')

    def test_decode(self):
        """
        test decode function
        """
        self.assertEqual(self.user.decode(), 'user:password')

    def test_check_function(self):
        """
        test for test function
        """
        self.assertTrue(_is_base64(self.user.user64))
        self.assertFalse(_is_base64('string'))
