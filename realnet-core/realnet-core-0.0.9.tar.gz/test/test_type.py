import unittest

from realnet_core import Type


class TypeTestCase(unittest.TestCase):

    def test_dict(self):
        t1 = Type('1', '2', attributes={'three': 'four'})
        t2 = Type.from_dict(t1.to_dict())

        self.assertEqual(t2.id, '1')
        self.assertEqual(t2.name, '2')
        self.assertEqual(t2.attributes['three'], 'four')

    def test_json(self):
        t1 = Type('1', '2', attributes={'three': 'four'})
        t2 = Type.from_json(t1.to_json())

        self.assertEqual(t2.id, '1')
        self.assertEqual(t2.name, '2')
        self.assertEqual(t2.attributes['three'], 'four')

    def test_children_dict(self):
        t1a = Type('t1a', 't1a_name', attributes={'three': 'four'})
        i1a = t1a.create_item('i1a', 'i1a_name', {'six': 'seven'})
        t1b = Type('t1b', 't1b_name', attributes={'eight': 'nine'})
        i1b = t1b.create_item('i1b', 'i1b_name', {'ten': 'eleven'})
        t1c = Type('t1c', 't1c_name', [i1a, i1b], {'twelve': 'thirteen'})

        t2 = Type.from_dict(t1c.to_dict())

        self.assertEqual(t2.id, 't1c')
        self.assertEqual(t2.name, 't1c_name')
        self.assertEqual(t2.attributes['twelve'], 'thirteen')
        self.assertEqual(t2.items[0].name, 'i1a_name')
        self.assertEqual(t2.items[0].attributes['six'], 'seven')
        self.assertEqual(t2.items[0].type.name, 't1a_name')
        self.assertEqual(t2.items[1].name, 'i1b_name')
        self.assertEqual(t2.items[1].attributes['ten'], 'eleven')
        self.assertEqual(t2.items[1].type.name, 't1b_name')

    def test_children_json(self):
        t1a = Type('t1a', 't1a_name', attributes={'three': 'four'})
        i1a = t1a.create_item('i1a', 'i1a_name', {'six': 'seven'})
        t1b = Type('t1b', 't1b_name', attributes={'eight': 'nine'})
        i1b = t1b.create_item('i1b', 'i1b_name', {'ten': 'eleven'})
        t1c = Type('t1c', 't1c_name', [i1a, i1b], {'twelve': 'thirteen'})

        t2 = Type.from_json(t1c.to_json())

        self.assertEqual(t2.id, 't1c')
        self.assertEqual(t2.name, 't1c_name')
        self.assertEqual(t2.attributes['twelve'], 'thirteen')
        self.assertEqual(t2.items[0].name, 'i1a_name')
        self.assertEqual(t2.items[0].attributes['six'], 'seven')
        self.assertEqual(t2.items[0].type.name, 't1a_name')
        self.assertEqual(t2.items[1].name, 'i1b_name')
        self.assertEqual(t2.items[1].attributes['ten'], 'eleven')
        self.assertEqual(t2.items[1].type.name, 't1b_name')


if __name__ == '__main__':
    unittest.main()
