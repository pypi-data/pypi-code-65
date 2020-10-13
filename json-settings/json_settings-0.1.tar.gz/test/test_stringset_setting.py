import unittest

from json_settings import StringSetSetting

from json_settings import OptionsAttributeNotImplementedError
from json_settings import OptionsAttributeTypeError
from json_settings import SettingTypeError
from json_settings import SettingStringSelectionError


class NoOptions(StringSetSetting):
    @StringSetSetting.assign
    def __init__(self, value):
        self.fish = ["carp"]


class WrongTypeOptions(StringSetSetting):
    @StringSetSetting.assign
    def __init__(self, value):
        self.options = "carp"


class Fish(StringSetSetting):
    @StringSetSetting.assign
    def __init__(self, value):
        self.options = [
            "carp",
            "barbel",
            "trout"
        ]


class TestStringSetSetting(unittest.TestCase):
    """The unit tests for the :class:`~.StringSetSetting` class.
    
    """
    def test_options_attribute_not_implemented_error(self):
        with self.assertRaises(OptionsAttributeNotImplementedError) as context:
            NoOptions("carp")
    
    def test_options_attribute_type_error(self):
        with self.assertRaises(OptionsAttributeTypeError) as context:
            WrongTypeOptions("carp")

    def test_setting_type_error(self):
        with self.assertRaises(SettingTypeError) as context:
            Fish(1)
    
    def test_setting_string_selection_error(self):
        with self.assertRaises(SettingStringSelectionError) as context:
            Fish("cod")
        
    def test_normal_init(self):
        setting = Fish("carp")
        self.assertEqual(setting.value, "carp")
        self.assertEqual(setting.get, "carp")






