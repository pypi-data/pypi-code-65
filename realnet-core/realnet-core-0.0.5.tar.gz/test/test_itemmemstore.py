import unittest

from realnet_core import ItemMemStore


class MemoryStoreTestCase(unittest.TestCase):

    def test_create_type(self):
        ms = ItemMemStore()

        t1 = ms.create_type('2', attributes={'three': 'four'})
        t2 = ms.retrieve_type(t1.id)

        self.assertEqual(t2.name, '2')
        self.assertEqual(t2.attributes['three'], 'four')

    def test_create_item(self):
        ms = ItemMemStore()

        t1 = ms.create_type('2', attributes={'three': 'four'})
        i1 = ms.create_item(t1, '6', attributes={'seven': 'eight'})

        i2 = ms.retrieve_item(i1.id)

        self.assertEqual(i2.type.name, '2')
        self.assertEqual(i2.type.attributes['three'], 'four')
        self.assertEqual(i2.name, '6')
        self.assertEqual(i2.attributes['seven'], 'eight')



if __name__ == '__main__':
    unittest.main()
