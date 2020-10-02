from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Slot, QItemSelectionModel, QAbstractItemModel
import re
from functools import lru_cache
from .abstract_view import Model as AbstractModel, View as AbstractView, \
    ImageDelegate


class Model(AbstractModel):
    rx = re.compile(r'.*\.jpe?g*', re.I)

    @Slot()
    def delta_changed(self, delta):
        self.renamer.delta = delta
        super().delta_changed(delta)

    def rename(self, files: list):
        self.renamer.rename(*files)
        self.reset()

    def back(self, files: list):
        self.renamer.back(*files)
        self.reset()

    def folder_changed(self, folder):
        self.beginResetModel()
        self.ini_files(None, folder)
        self.endResetModel()


class View(AbstractView):
    def __init__(self, parent=None):
        super().__init__(parent)
        QApplication.instance().aboutToQuit.connect(self.save)

    def initialize(self, model: QAbstractItemModel, images_display,
                   **_kwargs):
        super().initialize(model, images_display)
        self.reset_selection()

    @Slot()
    def profile_changed(self, profile):
        old = self.model().profile.path if self.model().profile else None
        self.model().profile_changed(profile)
        if old != profile.path:
            ImageDelegate.do_get_image.cache_clear()
        self.reset_selection()

    @Slot()
    def rename(self):
        self.model().rename(self.selected_files())

    @Slot()
    def back(self):
        self.model().back(self.selected_files())

    @Slot()
    def reset_selection(self):
        return self._do_selection(True)

    def _do_selection(self, direction: bool):
        selection = self.selectionModel()
        item_sel = self.model().item_selection(direction)
        selection.select(item_sel, QItemSelectionModel.ClearAndSelect)

    @Slot()
    def select_renamed(self):
        return self._do_selection(False)

    @Slot()
    def set_cache_size(self):
        size = super().set_cache_size()
        ImageDelegate.do_get_image = lru_cache(maxsize=size)(
            ImageDelegate.do_get_image.__wrapped__)
