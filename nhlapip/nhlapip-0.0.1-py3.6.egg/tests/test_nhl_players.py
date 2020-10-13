import unittest
from nhlapip.nhl_players import Player
from nhlapip.const import NHLAPI_BASEURL

class TestConst(unittest.TestCase):

    def test_player_sconstructor(self):           
       pl = Player("1")
       self.assertEqual(pl.url, NHLAPI_BASEURL + "people/1")
       self.assertEqual(pl.endpoint, "people")
       self.assertEqual(pl.suffixes, "1")
       self.assertEqual(pl.data, None)

    def test_player_getdata(self):           
       pl = Player("8451101").get_data()
       self.assertIsInstance(pl.data, dict)
       self.assertEqual(pl.data["id"], pl.id)
       