import unittest

from realnet_core import Item, Type


class ItemTestCase(unittest.TestCase):

    def test_dict(self):
        t1 = Type('1', '2', attributes={'three': 'four'})
        i1 = Item('5', '6', t1, attributes={'seven': 'eight'})
        i2 = Item.from_dict(i1.to_dict())

        self.assertEqual(i2.type.id, '1')
        self.assertEqual(i2.type.name, '2')
        self.assertEqual(i2.type.attributes['three'], 'four')
        self.assertEqual(i2.id, '5')
        self.assertEqual(i2.name, '6')
        self.assertEqual(i2.attributes['seven'], 'eight')

    def test_json(self):
        t1 = Type('1', '2', attributes={'three': 'four'})
        i1 = Item('5', '6', t1, attributes={'seven': 'eight'})
        i2 = Item.from_json(i1.to_json())

        self.assertEqual(i2.type.id, '1')
        self.assertEqual(i2.type.name, '2')
        self.assertEqual(i2.type.attributes['three'], 'four')
        self.assertEqual(i2.id, '5')
        self.assertEqual(i2.name, '6')
        self.assertEqual(i2.attributes['seven'], 'eight')

    def test_create_item_from_type_no_override(self):
        t1 = Type('1', '2', attributes={'three': 'four'})
        i1 = t1.create_item('5', '6')

        self.assertEqual(i1.type.id, '1')
        self.assertEqual(i1.type.name, '2')
        self.assertEqual(i1.type.attributes['three'], 'four')
        self.assertEqual(i1.id, '5')
        self.assertEqual(i1.name, '6')

    def test_create_item_from_type_override_attributes(self):
        t1 = Type('1', '2', attributes={'three': 'four', 'ten': 'eleven'})
        i1 = t1.create_item('5', '6',  attributes={'three': 'seven', 'eight': 'nine'})

        self.assertEqual(i1.type.id, '1')
        self.assertEqual(i1.type.name, '2')
        self.assertEqual(i1.type.attributes['three'], 'four')
        self.assertEqual(i1.id, '5')
        self.assertEqual(i1.name, '6')
        self.assertEqual(i1.attributes['three'], 'seven')
        self.assertEqual(i1.attributes['eight'], 'nine')
        self.assertEqual(i1.attributes['ten'], 'eleven')

    def test_create_item_from_type_with_children(self):
        t1 = Type('1', '2', attributes={'three': 'four', 'ten': 'eleven'})
        i1 = t1.create_item('5', '6', {'three': 'seven', 'eight': 'nine'})

        self.assertEqual(i1.type.id, '1')
        self.assertEqual(i1.type.name, '2')
        self.assertEqual(i1.type.attributes['three'], 'four')
        self.assertEqual(i1.id, '5')
        self.assertEqual(i1.name, '6')
        self.assertEqual(i1.attributes['three'], 'seven')
        self.assertEqual(i1.attributes['eight'], 'nine')
        self.assertEqual(i1.attributes['ten'], 'eleven')



if __name__ == '__main__':
    unittest.main()
