# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""


from PySide2.QtCore import Slot,  Qt, QSettings
from PySide2.QtWidgets import QMainWindow,  QApplication,  QWidget

from .ui_main_window import Ui_MainWindow
from .about import About
from .profile import ProfileDialog
from .profiles import ProfilesDialog
from .profile_manager import ProfileManager
from .main_view import Model
from typing import Optional
from .settings import Settings
from .merge_dialog import MergeDialog


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Main window for QtImgren.
    """
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        settings = QSettings()
        geom = settings.value('MainWindow/geom')
        if geom is not None:
            self.restoreGeometry(geom)
        self.merge_folder = settings.value('MainWindow/merge', '.')
        self.profile_manager = ProfileManager(self.menu_Profiles, self)
        view = self.tableView
        model = Model(self.profile_manager.active_profile, view)
        view.initialize(model, self.images_display, )
        self.profile_manager.profile_changed.connect(view.profile_changed)
        QApplication.instance().aboutToQuit.connect(self.save)

    @Slot()
    def on_action_about_triggered(self):
        """
        Displays About dialog.
        """
        about = About()
        about.setWindowFlag(Qt.WindowContextHelpButtonHint,  False)
        about.exec_()
    
    @Slot()
    def on_action_about_qt_triggered(self):
        """
        Displays About Qt dialog.
        """
        QApplication.aboutQt()

    @Slot()
    def on_action_new_profile_triggered(self):
        """
        Create a new profile.
        """
        profile = ProfileDialog(self,  names=self.profile_manager.names())
        cr = profile.exec_()
        if cr:
            self.profile_manager.add_from_dialog(profile)
    
    @Slot()
    def on_action_manage_profiles_triggered(self):
        """
        Manage (edit or remove) existing profiles.
        """
        dialog = ProfilesDialog(self.profile_manager.profiles,  self)
        cr = dialog.exec_()
        if cr:
            self.profile_manager.reset_profiles(dialog.model.profiles)

    @Slot()
    def on_action_settings_triggered(self):
        settings = Settings(self)
        settings.use_cache.setCheckState(
            Qt.Checked if self.tableView.use_cache else Qt.Unchecked)
        settings.cache_size.setValue(self.tableView.cache_size)
        cr = settings.exec_()
        if cr:
            use_cache = settings.use_cache.checkState() == Qt.Checked
            if (settings.cache_size.value() != self.tableView.cache_size
                    or use_cache != self.tableView.use_cache):
                self.tableView.cache_size = settings.cache_size.value()
                self.tableView.use_cache = use_cache
                self.tableView.set_cache_size()
            QApplication.instance().set_language(
                settings.language.currentData())
            self.retranslateUi(self)

    @Slot()
    def on_action_merge_triggered(self):
        profile = self.profile_manager.active_profile
        if profile is not None:
            renamer = self.tableView.model().renamer
            merge = MergeDialog(profile, renamer, self.merge_folder, self)
            merge.view.use_cache = self.tableView.use_cache
            merge.view.cache_size = self.tableView.cache_size
            merge.view.images_display = self.tableView.images_display
            cr = merge.exec_()
            self.merge_folder = merge.folder.text()
            if cr:
                renamer.merge(self.merge_folder, *(merge.selected_files()))
                self.tableView.model().reset()

    @Slot()
    def save(self):
        settings = QSettings()
        settings.beginGroup('MainWindow')
        geom = self.saveGeometry()
        settings.setValue('geom', geom)
        settings.setValue('lang', QApplication.instance().get_language())
        settings.setValue('merge', self.merge_folder)
        settings.endGroup()
