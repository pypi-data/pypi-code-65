import unittest
from PySide2.QtWidgets import QApplication
from qtimgren import main_window, profile_manager, profiles, profile
from unittest.mock import patch, Mock


class TestProfiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication()

    def setUp(self) -> None:
        self.main = main_window.MainWindow()
        self.profiles = [profile_manager.Profile('foo', '.', 'IMG*.JPG'),
                         profile_manager.Profile('bar', '.', 'DSCF*.JPG')]
        self.dialog = profiles.ProfilesDialog(self.profiles, self.main)

    def tearDown(self) -> None:
        self.dialog.close()
        self.main.close()

    def test_init(self):
        self.assertEqual(self.profiles, self.dialog.model.profiles)
        self.assertIsNot(self.profiles, self.dialog.model.profiles)

    def test_duplicate(self):
        self.dialog.model.set_profile(1, profile_manager.Profile(
            'foo', '.', 'DSCF*.JPG')
                                      )
        with patch.object(profiles, 'QMessageBox') as msg_box:
            self.assertFalse(self.dialog.valid())
            self.assertEqual(1, msg_box.warning.call_count)

    def test_remove(self):
        view = self.dialog.table_view
        view.selectRow(0)
        remove = self.dialog.remove
        remove.clicked.emit()
        self.assertEqual(1, self.dialog.model.rowCount())
        self.assertEqual('bar', self.dialog.model.profiles[0].name)

    def test_edit_canceled(self):
        view = self.dialog.table_view
        view.selectRow(1)
        edit = self.dialog.edit
        sub = Mock(profile.ProfileDialog)
        sub.exec = sub.exec_
        with patch.object(profiles, 'ProfileDialog') as ProfileDialog:
            ProfileDialog.return_value = sub
            sub.exec_.return_value = 0
            edit.clicked.emit()
            sub.exec.assert_called_once_with()
            ProfileDialog.assert_called_once_with(self.dialog, self.profiles[1])
        self.assertIs(self.profiles[1], self.dialog.model.profiles[1])

    def test_edit_ok(self):
        view = self.dialog.table_view
        view.selectRow(1)
        edit = self.dialog.edit
        sub = Mock(profile.ProfileDialog)
        sub.exec = sub.exec_
        with patch.object(profiles, 'ProfileDialog') as ProfileDialog:
            ProfileDialog.return_value = sub
            sub.exec_.return_value = 1
            sub.get_name.return_value = 'foobar'
            sub.get_path.return_value = '.'
            sub.get_mask.return_value = 'I*.JPEG'
            sub.get_pattern.return_value = profile_manager.defaultPattern
            edit.clicked.emit()
            sub.exec.assert_called_once_with()
            ProfileDialog.assert_called_once_with(self.dialog, self.profiles[1])
            self.assertNotEqual(self.profiles[1], self.dialog.model.profiles[1])


if __name__ == '__main__':
    unittest.main()
