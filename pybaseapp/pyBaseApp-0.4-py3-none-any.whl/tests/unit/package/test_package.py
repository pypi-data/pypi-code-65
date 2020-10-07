import unittest
import logging
import shutil
import os

from pyBaseApp.package import Package, Options
from pyBaseApp.applauncher import Configuration

class TestPackage(unittest.TestCase):

    def test_package(self):
     
        settings = Configuration().settings('tests/unit/package/resources/settings.yml')
        try:
            options = Options(settings)
            Package(options)
        except ValueError:
            logging.error('package value is missing in settings')

        self.assertTrue(os.path.exists(settings['distpath']))
        shutil.rmtree(settings['distpath'], ignore_errors=True)
