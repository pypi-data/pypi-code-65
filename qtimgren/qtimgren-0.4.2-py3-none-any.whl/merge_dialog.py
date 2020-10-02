#  Copyright (c) 2020  SBA - MIT License

from PySide2.QtWidgets import QDialog, QFileDialog
from PySide2.QtCore import Slot, Qt, QSettings, QCoreApplication
import os.path
from .ui_merge import Ui_Dialog
from .merge import MergeModel


class MergeDialog(QDialog, Ui_Dialog):
    def __init__(self, profile, renamer, folder, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.load()
        self.folder.setText(os.path.abspath(folder))
        model = MergeModel(profile, parent, renamer, folder)
        try:
            images_display = parent.images_display.checkState() == Qt.Checked
        except LookupError:
            images_display = True
        self.view.initialize(model, images_display, )

    def selected_files(self):
        return self.view.selected_files()

    @Slot(int)
    def done(self, cr):
        self.save()
        super().done(cr)

    @Slot()
    def on_change_clicked(self):
        wd = QFileDialog.getExistingDirectory(
            self, translate('merge', 'New folder'), self.folder.text(),
            options=QFileDialog.ShowDirsOnly | QFileDialog.DontUseNativeDialog)
        if wd != '':
            self.folder.setText(wd)
            self.view.model().folder_changed(wd)

    def save(self):
        self.view.save()
        settings = QSettings()
        settings.beginGroup(self.__class__.__name__)
        geom = self.saveGeometry()
        settings.setValue('geom', geom)
        settings.endGroup()

    def load(self):
        settings = QSettings()
        settings.beginGroup(self.__class__.__name__)
        geom = settings.value('geom')
        if geom is not None:
            self.restoreGeometry(geom)
        settings.endGroup()


translate = QCoreApplication.translate
