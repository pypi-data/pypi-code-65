# -*- coding: utf-8 -*-

"""
Module implementing ProfilesDialog.
"""

from PySide2.QtCore import Slot,  QAbstractTableModel, QModelIndex, Qt
from PySide2.QtCore import QSettings
from PySide2.QtWidgets import QDialog, QMessageBox, QApplication

from .ui_profiles import Ui_profiles
from .profile import ProfileDialog
from .profile_manager import Profile


class ProfilesModel(QAbstractTableModel):
    def __init__(self,  profiles,  parent=None):
        super().__init__(parent)
        self.profiles = profiles[:]
        
    def rowCount(self,  _parent=QModelIndex()):
        return len(self.profiles)
    
    def columnCount(self,  _parent=QModelIndex):
        return 4
        
    def data(self, index,  role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        p = self.profiles[index.row()]
        col = index.column()
        if col == 0:
            return p.name
        elif col == 1:
            return p.path
        elif col == 2:
            return p.mask
        else:
            return p.pattern
    
    def headerData(self,  section,  orientation,  role=Qt.DisplayRole):
        headers = [translate('profiles', 'Name'),
                   translate('profiles', 'Path'),
                   translate('profiles', 'Mask'),
                   translate('profiles', 'Pattern')]
        if role != Qt.DisplayRole or orientation != Qt.Horizontal:
            return None
        return headers[section]
    
    def set_profile(self,  row,  profile):
        self.profiles[row] = profile
        self.dataChanged.emit(self.createIndex(row,  0),  self.createIndex(row,  3))
    
    def removeRows(self,  row,  count,  parent=QModelIndex()):
        self.beginRemoveRows(parent, row,  row + count - 1)
        del self.profiles[row:row+count]
        self.endRemoveRows()


class ProfilesDialog(QDialog, Ui_profiles):
    """
    Class documentation goes here.
    """
    def __init__(self, profiles,  parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(ProfilesDialog, self).__init__(parent)
        self.setupUi(self)
        self.model = ProfilesModel(profiles)
        self.view = self.table_view
        self.view.setModel(self.model)
        settings = QSettings()
        settings.beginGroup('ProfilesDialog')
        geom = settings.value('geom')
        if geom is not None:
            self.restoreGeometry(geom)
        sz = settings.beginReadArray('col_size')
        for i in range(sz):
            settings.setArrayIndex(i)
            w = settings.value('col')
            self.view.setColumnWidth(i, w)
        settings.endArray()
        settings.endGroup()
        self.view.horizontalHeader().setStretchLastSection(True)

    @Slot()
    def on_edit_clicked(self):
        """
        Slot documentation goes here.
        """
        try:
            sel = self.view.selectedIndexes()[0].row()
        except LookupError:
            sel = None
        if sel is not None:
            dialog = ProfileDialog(self,  self.model.profiles[sel])
            cr = dialog.exec_()
            if cr:
                self.model.set_profile(sel,  Profile.from_dialog(dialog))
    
    @Slot()
    def on_remove_clicked(self):
        """
        Slot documentation goes here.
        """
        sel = self.view.selectedIndexes()
        rows = sorted(set(index.row() for index in sel), reverse=True)
        for row in rows:
            self.model.removeRows(row,  1)

    @Slot()
    def on_button_box_accepted(self):
        if self.valid():
            self.accept()

    def valid(self):
        names = []
        for row,  p in enumerate(self.model.profiles):
            if p.name in names:
                ix = names.index(p.name) + 1
                msg = translate('profiles', '"{1}" is a duplicate<br/>'
                                            'already present at row {0}'
                                ).format(ix,  p.name)
                QMessageBox.warning(self, 'Duplicate name',  msg)
                self.view.selectRow(row)
                return False
            names.append(p.name)
        return True

    @Slot()
    def done(self, r):
        settings = QSettings()
        settings.beginGroup('ProfilesDialog')
        settings.setValue('geom', self.saveGeometry())
        settings.beginWriteArray('col_size')
        for i in range(3):
            settings.setArrayIndex(i)
            settings.setValue('col', self.view.columnWidth(i))
        settings.endArray()
        settings.endGroup()
        super().done(r)


def translate(ctx, txt):
    return QApplication.translate(ctx, txt)
