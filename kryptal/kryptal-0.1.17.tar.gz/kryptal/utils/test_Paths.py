from kryptal.utils import Paths
import unittest


class test_Paths(unittest.TestCase):
    def test_plugin_paths_not_empty(self) -> None:
        self.assertGreater(len(Paths.plugin_paths()), 0)

    def test_plugin_paths_are_strings(self) -> None:
        for path in Paths.plugin_paths():
            self.assertTrue(isinstance(path, str))

    def test_plugin_paths_filesystems_not_empty(self) -> None:
        self.assertGreater(len(Paths.plugin_paths_filesystems()), 0)

    def test_plugin_paths_filesystems_are_strings(self) -> None:
        for path in Paths.plugin_paths_filesystems():
            self.assertTrue(isinstance(path, str))

    def test_plugin_paths_storageproviders_not_empty(self) -> None:
        self.assertGreater(len(Paths.plugin_paths_storageproviders()), 0)

    def test_plugin_paths_storageproviders_are_strings(self) -> None:
        for path in Paths.plugin_paths_storageproviders():
            self.assertTrue(isinstance(path, str))
