import  unittest
from publicdata.pums import PumsUrl
from publicdata.pums.exceptions import PumsUrlError
from test_support import TestCase
from rowgenerators import parse_app_url, Downloader

class TestBasic(TestCase):

    def test_basic(self):

        u = PumsUrl('pums://CA/h/2018/1')
        print(str(u))

        with self.assertRaises(PumsUrlError) as e:
            u = PumsUrl('pums:')

        self.assertIn('No state',  str(e.exception))
        self.assertIn('No year', str(e.exception))
        self.assertIn('No release', str(e.exception))
        self.assertIn('No record_type', str(e.exception))

        with self.assertRaises(PumsUrlError) as e:
            u = PumsUrl('pums:CA')

        self.assertNotIn('No state', str(e.exception))
        self.assertIn('No year', str(e.exception))
        self.assertIn('No release', str(e.exception))
        self.assertIn('No record_type', str(e.exception))

        with self.assertRaises(PumsUrlError) as e:
            u = PumsUrl('pums:CA/x/year/1')

        self.assertNotIn('No state', str(e.exception))
        self.assertIn('Bad year', str(e.exception))
        self.assertNotIn('release', str(e.exception))
        self.assertIn('Bad record type', str(e.exception))

        u = PumsUrl('pums:RI/h/2018/1')

        df = u.dataframe()
        print(df.head())


if __name__ == '__main__':
    unittest.main()
