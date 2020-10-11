from unittest.mock import patch, Mock
from kryptal.gui import Application
from kryptal.gui import __main__
import unittest


class test_main(unittest.TestCase):
    @patch('kryptal.gui.Application.create_prod_instance')
    @patch('kryptal.gui.Application.Application.run')
    @patch('sys.exit')
    def test_runs_application(self, exitMock: Mock, runMock: Mock, createProd: Mock) -> None:
        # main() calls Application.create_prod_instance(), but we mocked that out.
        # To make sure we actually have an instance to run, let's first create a test instance.
        Application.create_test_instance()
        
        runMock.return_value = 0
        __main__.main()
        createProd.assert_called_once_with()
        runMock.assert_called_once_with()

    # TODO Re-enable these tests, once an Application can be run in prod mode during the tests
    # @patch('kryptal.gui.Application.QApplication.exec_')
    # @patch('kryptal.gui.MainWindow.MainWindow.show')
    # @patch('sys.exit')
    # def test_shows_mainwindow(exitMock: Mock, mainWindowShowMock: Mock, execMock: Mock) -> None:
    #    __main__.main()
    #    mainWindowShowMock.assert_called_once_with()
