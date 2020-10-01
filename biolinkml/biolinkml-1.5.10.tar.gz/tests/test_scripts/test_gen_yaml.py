import unittest

import click

from biolinkml.generators import yamlgen
from tests.test_scripts.environment import env
from tests.utils.clicktestcase import ClickTestCase


class GenYUMLTestCase(ClickTestCase):
    testdir = "genyaml"
    click_ep = yamlgen.cli
    prog_name = "gen-yaml"
    env = env

    def test_help(self):
        self.do_test("--help", 'help')

    def test_emit_yaml(self):
        """ Test emitting a YAML file """
        self.do_test([env.root_input_path('meta.yaml'),"--importmap", self.env.import_map, '-g'], 'meta.yaml',
                     add_yaml=False)

    def test_validate_yaml(self):
        """ Test YAML file validation """
        self.do_test([env.input_path('yaml_validate_clean.yaml'), '-v'], 'clean.txt', add_yaml=False)
        with self.assertRaises(ValueError) as e:
            self.do_test([env.input_path('yaml_validate_invalid.yaml'), '-v'], 'invalid.txt', add_yaml=False)
        self.assertIn('slot: k - unrecognized range (none)', str(e.exception))


if __name__ == '__main__':
    unittest.main()
