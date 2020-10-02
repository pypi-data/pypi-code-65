#  Copyright (c) 2020  SBA - MIT License

from PySide2.QtCore import QAbstractItemModel
from .abstract_view import Model, View
from .profiles import Profile


class MergeModel(Model):
    def __init__(self, profile: Profile, parent=None, renamer=None,
                 folder=None):
        super().__init__(profile, parent, renamer, folder)

    def folder_changed(self, folder):
        self.beginResetModel()
        self.ini_files(self.renamer, folder)
        self.endResetModel()


class MergeView(View):
    def initialize(self, model: QAbstractItemModel, images_display,
                   ini_check=True):
        super().initialize(model, images_display, ini_check)
        self.hideColumn(2)
