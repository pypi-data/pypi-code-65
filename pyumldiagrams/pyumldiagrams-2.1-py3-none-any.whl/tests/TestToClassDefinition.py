
from logging import Logger
from logging import getLogger

from unittest import TestSuite
from unittest import main as unitTestMain

from pkg_resources import resource_filename

from pyumldiagrams.xmlsupport.ToClassDefinition import ToClassDefinition

from tests.TestBase import TestBase
from tests.TestBase import BEND_TEST_XML_FILE

EXPECTED_CLASS_COUNT: int = 7
EXPECTED_LINE_COUNT:  int = 6


class TestXmlInput(TestBase):
    """
    """
    clsLogger: Logger = None

    @classmethod
    def setUpClass(cls):
        TestBase.setUpLogging()
        TestXmlInput.clsLogger = getLogger(__name__)

    def setUp(self):
        self.logger: Logger = TestXmlInput.clsLogger

        self._fqFileName: str = resource_filename(TestBase.RESOURCES_PACKAGE_NAME, BEND_TEST_XML_FILE)

    def tearDown(self):
        pass

    def testBasicClassDefinitions(self):

        toClassDefinition: ToClassDefinition = ToClassDefinition(fqFileName=self._fqFileName)

        toClassDefinition.generateClassDefinitions()

        self.assertIsNotNone(toClassDefinition.classDefinitions, 'We need some class definitions')
        self.assertEqual(EXPECTED_CLASS_COUNT, len(toClassDefinition.classDefinitions), 'Did not parse the correct number classes')

    def testLineDefinitions(self):

        toClassDefinition: ToClassDefinition = ToClassDefinition(fqFileName=self._fqFileName)

        toClassDefinition.generateUmlLineDefinitions()

        self.assertIsNotNone(toClassDefinition.umlLineDefinitions, 'We need some line definitions')
        self.assertEqual(EXPECTED_LINE_COUNT, len(toClassDefinition.umlLineDefinitions), 'Did not parse the correct number lines')


def suite() -> TestSuite:
    """You need to change the name of the test class here also."""
    import unittest

    testSuite: TestSuite = TestSuite()
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestXmlInput))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
