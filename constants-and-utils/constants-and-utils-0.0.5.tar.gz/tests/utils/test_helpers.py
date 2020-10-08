from dataclasses import dataclass
from unittest import TestCase
from constants_and_utils.utils.helpers import (
    recursive_get,
    kebab_case,
    camel_to_snake,
    dict_keys_to_snake,
    setter_object_attrs,
)


class TestHelpers(TestCase):

    def test_recursive_get(self):
        param_d = {'NUMBER': {'ONE': 1}}
        param_keys = 'NUMBER.ONE'
        expected = 1

        result = recursive_get(
            d=param_d,
            keys=param_keys
        )

        self.assertEqual(result, expected)

    def test_kebab_case(self):
        param_str = 'Hello world'
        expected = 'hello-world'

        result = kebab_case(
            string=param_str
        )

        self.assertEqual(result, expected)

    def test_camel_to_snake(self):
        param_str = 'HelloWorld'
        expected = 'hello_world'

        result = camel_to_snake(
            string=param_str
        )

        self.assertEqual(result, expected)

    def test_dict_keys_to_snake(self):
        param_dict = {'HelloWorld': 'message'}
        expected = {'hello_world': 'message'}

        result = dict_keys_to_snake(
            d=param_dict
        )

        self.assertEqual(result, expected)

    def test_setter_object_attrs(self):

        @dataclass
        class Animal:
            name: str
            sound: str = None

        dog = Animal('rufo')

        dog_attributes = {
            'sound': 'woff',
            'class': 'mammal',
            'kingdom': 'animalia',
        }

        keys = ['sound', 'kingdom']

        setter_object_attrs(dog, keys, dog_attributes)

        self.assertTrue(hasattr(dog, 'sound'))
        self.assertTrue(hasattr(dog, 'kingdom'))

        self.assertEqual(dog.sound, 'woff')
        self.assertEqual(dog.kingdom, 'animalia')
