import unittest

from json_settings import NumberSetting

from json_settings import SettingErrorMessage
from json_settings import SettingTypeError
from json_settings import SettingNotFoundError
from json_settings import TypeAttributeNotImplementedError
from json_settings import TypeAttributeTypeError 
from json_settings import SettingRangeTypeError 
from json_settings import SettingRangeKeyError
from json_settings import SettingCheckError


class Float(NumberSetting):
    @NumberSetting.assign
    def __init__(self, value):
        self.type = float 

    def check(self):
        pass


class Int(NumberSetting):
    @NumberSetting.assign
    def __init__(self, value):
        self.type = int 
    
    def check(self):
        pass


class NoType(NumberSetting):
    @NumberSetting.assign
    def __init__(self, value):
        self.typo = int

    def check(self):
        pass


class NotType(NumberSetting):
    @NumberSetting.assign
    def __init__(self, value):
        self.type = 1 

    def check(self):
        pass


class Bound(NumberSetting):
    @NumberSetting.assign
    def __init__(self, value):
        self.type = int
    
    def check(self):
        self.lower_bound(0)
        self.upper_bound(10)


class ExclusiveBound(NumberSetting):
    @NumberSetting.assign
    def __init__(self, value):
        self.type = int
    
    def check(self):
        self.lower_bound_exclusive(0)
        self.upper_bound_exclusive(10)


class TestNumberSetting(unittest.TestCase):
    """The unit tests for the :class:`~.NumberSetting` class.
    
    """
    def test_type_attribute_not_implemented_error(self):
        with self.assertRaises(TypeAttributeNotImplementedError) as context:
            NoType(1)

    def test_type_attribute_type_error(self):
        with self.assertRaises(TypeAttributeTypeError) as context:
            NotType(1)

    def test_literal_assignment(self):
        setting = Float(1.0)
        self.assertEqual(setting.value, 1.0)
        self.assertEqual(setting.get, 1.0)

    def test_array_assignment(self):
        values = {"array": [1, 2]}
        setting = Int(values)
        self.assertEqual(setting.value, values["array"])
        self.assertEqual(setting.get, values["array"])
    
    def test_range_assignment(self):
        values = {"min": 0.0, "max": 1.0, "num": 3}
        output = [0.0, 0.5, 1.0]
        setting  = Float(values)
        self.assertEqual(setting.value, output)
        self.assertEqual(setting.get, output)

    def test_array_setting_type_error(self):
        values = {"array": [1, 2.0]}
        with self.assertRaises(SettingTypeError) as context:
            Float(values)
        values = {"array": ["1", 2.0]}
        with self.assertRaises(SettingTypeError) as context:
            Float(values)

    def test_range_setting_range_type_error(self):
        values = {"min": 0, "max": 1.0, "num": 3}
        with self.assertRaises(SettingRangeTypeError) as context:
            Float(values)
        values = {"min": 0.0, "max": 1, "num": 3}
        with self.assertRaises(SettingRangeTypeError) as context:
            Float(values)
        values = {"min": 1.0, "max": 1.0, "num": 3.0}
        with self.assertRaises(SettingRangeTypeError) as context:
            Float(values)
    
    def test_range_setting_range_key_error(self):
        values = {"mon": 0.0, "max": 1.0, "num": 3}
        with self.assertRaises(SettingRangeKeyError) as context:
            Float(values)
        values = {"min": 0.0, "mix": 1.0, "num": 3}
        with self.assertRaises(SettingRangeKeyError) as context:
            Float(values)
        values = {"min": 0.0, "max": 1.0, "nim": 3}
        with self.assertRaises(SettingRangeKeyError) as context:
            Float(values)

    def test_is_range(self):
        values = {"array": [1.0, 2.0]}
        setting = Float(values)
        self.assertTrue(setting.is_range)
        values = {"min": 0.0, "max": 1.0, "num": 3}
        setting  = Float(values)
        self.assertTrue(setting.is_range)

    def test_lower_bound_literal(self):
        with self.assertRaises(SettingCheckError) as context:
            Bound(-1) 

    def test_lower_bound_array(self):
        with self.assertRaises(SettingCheckError) as context:
            Bound({"array": [-1, 11]}) 

    def test_lower_bound_range(self):
        with self.assertRaises(SettingCheckError) as context:
            Bound({"min": -1, "max": 5, "num": 5}) 
    
    def test_upper_bound_literal(self):
        with self.assertRaises(SettingCheckError) as context:
            Bound(50) 

    def test_upper_bound_array(self):
        with self.assertRaises(SettingCheckError) as context:
            Bound({"array": [1, 11]}) 

    def test_upper_bound_range(self):
        with self.assertRaises(SettingCheckError) as context:
            Bound({"min": 1, "max": 50, "num": 5}) 
        with self.assertRaises(SettingCheckError) as context:
            Bound({"min": 991, "max": 5, "num": 5}) 
    
    def test_lower_bound_exclusive_literal(self):
        with self.assertRaises(SettingCheckError) as context:
            ExclusiveBound(0) 

    def test_lower_bound_exclusive_array(self):
        with self.assertRaises(SettingCheckError) as context:
            ExclusiveBound({"array": [0, 11]}) 

    def test_lower_bound_exclusive_range(self):
        with self.assertRaises(SettingCheckError) as context:
            ExclusiveBound({"min": 0, "max": 5, "num": 5}) 
        with self.assertRaises(SettingCheckError) as context:
            ExclusiveBound({"min": 1, "max": 0, "num": 5}) 
    
    def test_upper_bound_exclusive_literal(self):
        with self.assertRaises(SettingCheckError) as context:
            ExclusiveBound(10)

    def test_upper_bound_exclusive_array(self):
        with self.assertRaises(SettingCheckError) as context:
            ExclusiveBound({"array": [1, 10]}) 

    def test_upper_bound_exclusive_range(self):
        with self.assertRaises(SettingCheckError) as context:
            ExclusiveBound({"min": 1, "max": 10, "num": 5}) 
        with self.assertRaises(SettingCheckError) as context:
            ExclusiveBound({"min": 10, "max": 5, "num": 5}) 
    

