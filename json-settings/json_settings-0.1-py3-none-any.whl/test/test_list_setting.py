import unittest

from json_settings import ListSetting

from json_settings import TypeAttributeNotImplementedError
from json_settings import TypeAttributeTypeError 
from json_settings import SettingTypeError
from json_settings import SettingErrorMessage


class NoType(ListSetting):
    @ListSetting.assign
    def __init__(self, values):
        self.typo = float 

class NotType(ListSetting):
    @ListSetting.assign
    def __init__(self, values):
        self.type = 1.0 

class IntList(ListSetting):
    @ListSetting.assign
    def __init__(self, values):
        self.type = int

class ListIntList(ListSetting):
    @ListSetting.assign
    def __init__(self, values):
        self.type = IntList


class TestListSetting(unittest.TestCase):

    def test_type_attribute_not_implemented_error(self):
        with self.assertRaises(TypeAttributeNotImplementedError) as context:
            NoType([1.0, 2.0])
    
    def test_type_attribute_type_error(self):
        with self.assertRaises(TypeAttributeTypeError) as context:
            NotType([1.0, 2.0])

    def test_setting_type_error(self):
        with self.assertRaises(SettingTypeError) as context:
            IntList(1.0)
    
    def test_normal_init_int_list(self):
        l = [1, 2, 3, 4, 5]
        setting = IntList(l)
        self.assertEqual(setting.value, l)
        self.assertEqual(setting.get, l)
        self.assertEqual(setting[0], 1)
        self.assertEqual(setting[2], 3)
        with self.assertRaises(IndexError) as context:
            setting[10]

    def test_normal_init_list_int_list(self):
        l = [[1, 2], [3, 4]]
        setting = ListIntList(l)
        self.assertEqual(setting[0][0], 1)
        with self.assertRaises(IndexError) as context:
            setting[1][3]
        self.assertIsInstance(setting[0], IntList)
        
        
