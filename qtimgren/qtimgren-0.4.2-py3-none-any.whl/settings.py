#  Copyright (c) 2020  SBA - MIT License
from PySide2.QtWidgets import QDialog, QApplication
from PySide2.QtCore import Qt, Slot
from .ui_settings import Ui_settings


class Settings(QDialog, Ui_settings):
    def __init__(self, parent=None, f=Qt.WindowFlags()):
        super().__init__(parent, f)
        self.setupUi(self)
        self.init_language()

    def init_language(self):
        app = QApplication.instance()
        cur = app.get_language()
        item = 0
        for i, lang in enumerate(app.get_languages()):
            if cur == lang[0]:
                item = i
            self.language.addItem(lang[1], lang[0])
        self.language.setCurrentIndex(item)

    @Slot(bool)
    def on_use_cache_clicked(self, use):
        self.cache_size.setEnabled(use)
