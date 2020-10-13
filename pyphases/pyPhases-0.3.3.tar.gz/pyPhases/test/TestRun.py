from unittest.loader import TestLoader
from unittest.runner import TextTestRunner
from unittest.suite import TestSuite
from pyPhases.test.TestCase import TestCase


class TestRun(TestCase):
    phaseTests = []

    def setProject(self):
        for test in self.phaseTests:
            test.setProject()

    def testPhases(self):
        loader = TestLoader()
        suite = TestSuite()
        for test in self.phaseTests:
            subTests = loader.loadTestsFromTestCase(type(test))
            suite.addTests(subTests)

        runner = TextTestRunner()
        return runner.run(suite)
