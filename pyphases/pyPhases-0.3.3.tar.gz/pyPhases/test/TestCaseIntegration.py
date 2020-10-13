from pyPhases.test.TestCase import TestCase


class TestCaseIntegration(TestCase):
    allreadyRun = False

    def setUp(self):
        super().setUp()

    @classmethod
    def setUpClass(c):
        c().prepare()
        c.beforeRun()
        c.phase.run()
        c.afterRun()

    def beforeRun():
        pass

    def afterRun():
        pass
