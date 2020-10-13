from json_settings.settings import Settings
from json_settings import SettingErrorMessage
from json_settings import SettingTypeError
from json_settings import SettingNotFoundError

import unittest


class SingleSetting(Settings):
    @Settings.assign
    def __init__(self, values):
        self.item = int

class SettingOfSetting(Settings):
    @Settings.assign
    def __init__(self, values):
        self.item = SingleSetting


class TestSettings(unittest.TestCase):
    """The unit tests for the :class:`~.Settings` class.
    
    """
    def test_not_a_dict(self):
        with self.assertRaises(SettingTypeError) as context:
            SingleSetting(0)
        with self.assertRaises(SettingTypeError) as context:
            SingleSetting("")
        with self.assertRaises(SettingTypeError) as context:
            SingleSetting(0.0)

    def test_setting_not_found(self):
        with self.assertRaises(SettingErrorMessage) as context:
            SingleSetting({"notitem": 1})
        try:
            SingleSetting({"notitem": 1})
        except SettingErrorMessage as e:
            self.assertIsInstance(e.original_error, SettingNotFoundError)

    def test_subsetting_not_a_dict(self):
        pass

   