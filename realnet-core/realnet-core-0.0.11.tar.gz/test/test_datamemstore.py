import unittest

from realnet_core import DataMemStore


class DataStoreTestCase(unittest.TestCase):

    def test_create_data(self):

        ds = DataMemStore()

        t1 = ds.create_data('2', attributes={'three': 'four'})
        t2 = ds.get_data(t1.id)

        self.assertEqual(t2.data, '2')
        self.assertEqual(t2.attributes['three'], 'four')


if __name__ == '__main__':
    unittest.main()
