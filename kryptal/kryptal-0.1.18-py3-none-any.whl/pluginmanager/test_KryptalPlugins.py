from kryptal.pluginmanager.IFilesystem import IFilesystem
from kryptal.pluginmanager.IStorageProvider import IStorageProvider
from kryptal.pluginmanager.KryptalPlugins import KryptalPlugins
import unittest


class test_KryptalPlugins(unittest.TestCase):
    def test_filesystems_is_array(self) -> None:
        self.assertTrue(isinstance(KryptalPlugins().filesystems(), dict))

    def test_storageproviders_is_array(self) -> None:
        self.assertTrue(isinstance(KryptalPlugins().storage_providers(), dict))

    def test_filesystems_not_empty(self) -> None:
        self.assertGreater(len(KryptalPlugins().filesystems()), 0)

    def test_storageproviders_not_empty(self) -> None:
        self.assertGreater(len(KryptalPlugins().storage_providers()), 0)

    def test_filesystems_valid(self) -> None:
        for _name, fs in KryptalPlugins().filesystems().items():
            self.assertTrue(isinstance(fs, IFilesystem))

    def test_storageproviders_valid(self) -> None:
        for _name, fs in KryptalPlugins().storage_providers().items():
            self.assertTrue(isinstance(fs, IStorageProvider))

    def test_filesystems_has_cryfs(self) -> None:
        names = [name for name, fs in KryptalPlugins().filesystems().items()]
        self.assertEqual(1, names.count("CryFS"))

    def test_storageproviders_has_localstorage(self) -> None:
        names = [name for name, sp in KryptalPlugins().storage_providers().items()]
        self.assertEqual(1, names.count("LocalFolder"))

    def test_filesystems_names_correct(self) -> None:
        for name, fs in KryptalPlugins().filesystems().items():
            self.assertEqual(name, fs.name())

    def test_storageproviders_names_correct(self) -> None:
        for name, sp in KryptalPlugins().storage_providers().items():
            self.assertEqual(name, sp.name())
