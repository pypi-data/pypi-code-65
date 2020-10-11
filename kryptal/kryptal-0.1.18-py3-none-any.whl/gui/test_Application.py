# TODO Re-enable these tests, once an Application can be run in prod mode during the tests
# @patch('kryptal.gui.Application.QApplication.exec_')
# @patch('kryptal.gui.MainWindow.MainWindow.show')
# def test_starts_mainloop(mainWindowShowMock: Mock, execMock: Mock) -> None:
#    app.run()
#    execMock.assert_called_once_with()
#
# @patch('kryptal.gui.Application.QApplication.exec_')
# @patch('kryptal.gui.MainWindow.MainWindow.show')
# def test_shows_mainwindow(mainWindowShowMock: Mock, execMock: Mock) -> None:
#    app.run()
#    mainWindowShowMock.assert_called_once_with()