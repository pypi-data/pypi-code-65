import unittest

from json_settings import DictionarySetting

from json_settings import TypeAttributeNotImplementedError
from json_settings import TypeAttributeTypeError 
from json_settings import SettingTypeError
from json_settings import SettingErrorMessage


class NoType(DictionarySetting):
    @DictionarySetting.assign
    def __init__(self, values):
        self.typo = float 

class NotType(DictionarySetting):
    @DictionarySetting.assign
    def __init__(self, values):
        self.type = 1.0 

class IntDictionary(DictionarySetting):
    @DictionarySetting.assign
    def __init__(self, values):
        self.type = int

class DictionaryIntDictionary(DictionarySetting):
    @DictionarySetting.assign
    def __init__(self, values):
        self.type = IntDictionary


class TestDictionarySetting(unittest.TestCase):

    def test_type_attribute_not_implemented_error(self):
        with self.assertRaises(TypeAttributeNotImplementedError) as context:
            NoType({"one": 1.0, "two": 2.0})
    
    def test_type_attribute_type_error(self):
        with self.assertRaises(TypeAttributeTypeError) as context:
            NotType({"one": 1.0, "two": 2.0})

    def test_setting_type_error(self):
        with self.assertRaises(SettingTypeError) as context:
            IntDictionary(1.0)
    
    def test_normal_init_int_dictionary(self):
        l = {str(i): i for i in range(5)} 
        setting = IntDictionary(l)
        self.assertEqual(setting.value, l)
        self.assertEqual(setting.get, l)
        self.assertEqual(setting["1"], 1)
        self.assertEqual(setting["3"], 3)
        with self.assertRaises(KeyError) as context:
            setting["6"]

    def test_normal_init_dict_int_dict(self):
        l = {
            "first": {str(i): i for i in range(5)},
            "second": {str(i): i for i in range(5)}
        }
        setting = DictionaryIntDictionary(l)
        self.assertEqual(setting["first"]["1"], 1)
        self.assertEqual(setting["second"]["3"], 3)
        with self.assertRaises(KeyError) as context:
            setting["fish"]["3"]
        with self.assertRaises(KeyError) as context:
            setting["first"][1]
        self.assertIsInstance(setting["first"], IntDictionary)
        self.assertIsInstance(setting["second"], IntDictionary)
