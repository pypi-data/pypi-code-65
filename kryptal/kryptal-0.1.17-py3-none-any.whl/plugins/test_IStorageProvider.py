from kryptal.pluginmanager.IStorageProvider import IStorageProvider
from kryptal.pluginmanager.KryptalPlugins import KryptalPlugins
import unittest


STORAGEPROVIDERS = [
    (name, sp) for name, sp in KryptalPlugins().storage_providers().items()]


class test_IStorageProvider(unittest.TestCase):
    def test_has_name(self) -> None:
        for (name, provider) in STORAGEPROVIDERS:
            with self.subTest(name):
                self.assertTrue(isinstance(provider.name(), str))
