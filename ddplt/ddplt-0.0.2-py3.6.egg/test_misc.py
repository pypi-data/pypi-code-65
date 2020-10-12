import unittest

import ddplt


class TestMisc(unittest.TestCase):

    def test_version(self):
        self.assertEqual(ddplt.__version__, "0.0.2.dev2")
