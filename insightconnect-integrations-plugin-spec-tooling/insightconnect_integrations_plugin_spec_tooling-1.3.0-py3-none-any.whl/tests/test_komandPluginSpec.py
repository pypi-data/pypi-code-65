from unittest import TestCase
from ..plugin_spec import KomandPluginSpec


class TestKomandPluginSpec(TestCase):
    def setUp(self) -> None:
        self.normal_spec = KomandPluginSpec(directory="icon_plugin_spec/tests/resources",
                                            spec_file_name="normal_plugin.spec.yaml")
        self.obsolete_spec = KomandPluginSpec(directory="icon_plugin_spec/tests/resources",
                                              spec_file_name="obsolete_plugin.spec.yaml")
        self.cloud_ready_spec = KomandPluginSpec(directory="icon_plugin_spec/tests/resources",
                                                 spec_file_name="cloud_ready_plugin.spec.yaml")

    def test_is_plugin_obsolete_false(self):
        is_obsolete = self.normal_spec.is_plugin_obsolete()
        self.assertFalse(is_obsolete)

    def test_is_plugin_obsolete_true(self):
        is_obsolete = self.obsolete_spec.is_plugin_obsolete()
        self.assertTrue(is_obsolete)

    def test_is_plugin_cloud_ready_false(self):
        cloud_ready = self.normal_spec.is_cloud_ready()
        self.assertFalse(cloud_ready)

    def test_is_plugin_cloud_ready_true(self):
        cloud_ready = self.cloud_ready_spec.is_cloud_ready()
        self.assertTrue(cloud_ready)
