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
thank for this post
https://stackoverflow.com/questions/4083796/how-do-i-run-unittest-on-a-tkinter-app
"""
# pylint: disable=wrong-import-order
import _tkinter
import os
import tkinter
import unittest

# noinspection PyPep8Naming
from login_gui import LoginGui, User


class TestGui(unittest.TestCase):
    """gui test"""

    def setUp(self):
        """start up function"""
        self.root = tkinter.Tk()
        LoginGui(self.root)
        self.pump_events()
        self.login_frame = self.root.children['!loginframe']

    def tearDown(self):
        """down function"""
        if self.root:
            # self.root.destroy()
            self.pump_events()

    def pump_events(self):
        """wait function"""
        while self.root.dooneevent(_tkinter.ALL_EVENTS | _tkinter.DONT_WAIT):
            pass

    # pylint: disable=protected-access
    def test_enter(self):
        """test of all buttons"""
        self.login_frame._loader.path = os.path.abspath('\\.log')
        self.assertEqual(self.login_frame._entry_username.get(), '')
        self.login_frame._entry_username.focus_set()
        self.login_frame._entry_username.insert(0, u'user')
        self.assertEqual(self.login_frame._entry_username.get(), 'user')

        self.assertEqual(self.login_frame._entry_password.get(), '')
        self.login_frame._entry_password.focus_set()
        self.login_frame._entry_password.insert(0, u'password')
        self.assertEqual(self.login_frame._entry_password.get(), 'password')

        self.assertEqual(self.login_frame._var.get(), 1)
        self.login_frame._checkbox.toggle()
        self.assertEqual(self.login_frame._var.get(), False)

        self.pump_events()

        self.assertNotEqual(User().decode(), 'user:password')
        self.login_frame._login_button.invoke()
        self.assertEqual(User().decode(), 'user:password')
