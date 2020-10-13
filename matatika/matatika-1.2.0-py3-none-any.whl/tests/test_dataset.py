"""test_dataset module"""

import unittest
import yaml
#import publish_dataset

class TestDataset(unittest.TestCase):
    """Class containing Dataset unit tests"""

    def setUp(self):
        yml_file = "tests/test_data/helloworld.yaml"
        with open(yml_file, 'r') as stream:
            self.yamlfile = yaml.safe_load(stream)

    def tearDown(self):
        print('Clean up')

    # def test_read_yml(self):
    #     print(self.yamlfile['version'])

    # def test_yaml_version(self):
    #     self.assertEqual('foo'.upper(), 'FOO')

    # def test_yaml(self):
    #     self.assertEqual('foo'.upper(), 'FOO')


if __name__ == '__main__':
    unittest.main()
