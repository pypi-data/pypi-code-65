import unittest

from OpenDiscord import arcane_center
from OpenDiscord import blist

blist_api = blist.API(712415898203586570, "F6QF2psvpek2Do-a8bCT")

class MyTestCase(unittest.TestCase):
    def test_blist_api(self):
        self.assertEqual(blist_api.get_id(), 744619278992539770)
        self.assertEqual(blist_api.get_name(), 'Fall Guys')
        self.assertEqual(blist_api.get_main_owner(), 261816312462835712)
        self.assertEqual(blist_api.get_owners(), [466314395677622282, 217303567361507328])


if __name__ == '__main__':
    blist_api.has_voted(662014520943706133)
    #unittest.main()
