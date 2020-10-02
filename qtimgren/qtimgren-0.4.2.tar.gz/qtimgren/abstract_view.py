from PySide2.QtWidgets import QTableView, QStyledItemDelegate, \
    QStyleOptionViewItem, QHeaderView
from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt, Slot, \
    QItemSelection, QItemSelectionModel, QAbstractItemModel, QSize, \
    QTimer, QSettings, QCoreApplication
from PySide2.QtGui import QImage, QPainter
from pyimgren.pyimgren import Renamer, exif_dat
from .profile_manager import Profile
import os.path
import re
import typing
import datetime
from fnmatch import fnmatch
from functools import lru_cache


class Model(QAbstractTableModel):
    rx = re.compile(r'.*\.jpe?g*', re.I)

    def __init__(self, profile: Profile, parent=None, renamer=None,
                 folder=None):
        super().__init__(parent)
        self.profile = profile
        self.files = []
        self.orig = {}
        self.folder = None
        self.renamer = None
        if profile is not None:
            self.ini_files(renamer, folder)

    def ini_files(self, renamer, folder):
        if folder is None:
            self.folder = self.profile.path
        else:
            self.folder = folder
        if renamer is None:
            self.renamer = Renamer(self.folder, self.profile.mask,
                                   self.profile.pattern, ext_mask='')
            self.orig = self.renamer.load_names()
        else:
            self.renamer = renamer
        if self.folder is not None:
            if not os.path.isdir(self.folder):
                self.folder = '.'
            self.files = ['..'] + [entry.name for entry in os.scandir(
                self.folder) if entry.is_dir() or self.rx.match(entry.name)]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.files)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 4

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole) -> typing.Any:
        header = [translate('view', 'Image'), translate('view', 'Name'),
                  translate('view', 'Original'), translate('view', 'New name')]
        if orientation == Qt.Orientation.Horizontal and role == Qt.DisplayRole:
            return header[section]

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> typing.Any:
        file = self.files[index.row()]
        if role == Qt.DisplayRole:
            if index.column() <= 1:
                return file
            if index.column() == 2:
                return self.orig.get(file, None)
            if index.column() == 3:
                try:
                    dat = exif_dat(os.path.join(self.folder, file))
                    if dat is not None:
                        dat += datetime.timedelta(minutes=self.renamer.delta)
                        return dat.strftime(self.profile.pattern)
                except OSError:
                    pass
        elif index.column() == 0:
            if role == Qt.DecorationRole:
                return QImage(os.path.join(self.folder, file))
        return None

    @Slot()
    def profile_changed(self, profile):
        self.beginResetModel()
        self.profile = profile
        self.ini_files(self.renamer, self.profile.path)
        self.endResetModel()

    @Slot()
    def delta_changed(self, delta):
        self.dataChanged.emit(self.index(0, 3),
                              self.index(self.rowCount() - 1, 3))

    def item_selection(self, direct: bool = True) -> QItemSelection:
        sel = QItemSelection()
        sel1 = QItemSelection()
        if direct:
            for i, file in enumerate(self.files):
                if fnmatch(file, self.renamer.src_mask):
                    sel1.select(self.index(i, 0), self.index(i, 3))
                    sel.merge(sel1, QItemSelectionModel.SelectCurrent)
        else:
            for i, file in enumerate(self.files):
                if file in self.renamer.load_names():
                    sel1.select(self.index(i, 0), self.index(i, 3))
                    sel.merge(sel1, QItemSelectionModel.SelectCurrent)
        return sel

    def reset(self):
        self.beginResetModel()
        self.ini_files(self.renamer, self.folder)
        self.endResetModel()


class View(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.images_display = None
        self.cache_id = 0
        self.doubleClicked.connect(self.on_double_click)

    def initialize(self, model: QAbstractItemModel, images_display,
                   ini_check=True):
        super().setModel(model)
        self.ini_check = ini_check
        self.images_display = images_display
        self.load(ini_check)

    @Slot(float)
    def delta_changed(self, delta):
        self.model().delta_changed(delta)

    @Slot()
    def display_images(self, display):
        self.setColumnHidden(0, not display)
        if not display:
            self.verticalHeader().resizeSections(QHeaderView.ResizeToContents)

    @Slot(QModelIndex)
    def on_double_click(self, index):
        print('index', index.row(), 'clicked')
        model = self.model()
        path = os.path.join(model.folder, model.data(model.index(
            index.row(), 1), Qt.DisplayRole))
        if os.path.isdir(path):
            if hasattr(self.parent(), 'folder'):
                self.parent().folder.setText(path)
            model.folder_changed(path)

    def set_cache_size(self):
        if self.use_cache:
            size = self.cache_size
            if size == -1:
                size = None
        else:
            size = 0
        self.cache_id += 1
        if self.cache_id >= 32768:
            self.cache_id = 0
        return size()

    def load(self, ini_check):
        settings = QSettings()
        settings.beginGroup(self.__class__.__name__)
        sz = settings.beginReadArray('col_size')
        for i in range(sz):
            settings.setArrayIndex(i)
            w = settings.value('col', type=int)
            if w is not None:
                self.setColumnWidth(i, w)
        settings.endArray()
        if ini_check:
            display = settings.value('display_images', type=bool)
            self.images_display.setCheckState(Qt.Checked if display
                                              else Qt.Unchecked)
            self.use_cache = settings.value('use_cache', True, type=bool)
            self.cache_size = settings.value('cache_size', 1000)
        else:
            display = self.images_display
        if not display:
            self.setColumnHidden(0, True)
        settings.endGroup()
        delegate = ImageDelegate(self)
        self.setItemDelegateForColumn(0, delegate)
        self.pre_load(delegate)

    @Slot()
    def save(self):
        settings = QSettings()
        settings.beginGroup(self.__class__.__name__)
        settings.beginWriteArray('col_size')
        for i in range(3):
            settings.setArrayIndex(i)
            w = self.columnWidth(i)
            if i != 0 or w != 0:
                settings.setValue('col', w)
        settings.endArray()
        if self.ini_check:
            settings.setValue('display_images',
                              self.images_display.checkState() == Qt.Checked)
            settings.setValue('use_cache', self.use_cache)
            settings.setValue('cache_size', self.cache_size)
        settings.endGroup()

    def selected_files(self):
        return [self.model().data(ix, Qt.DisplayRole)
                for ix in self.selectionModel().selectedRows(1)]

    def pre_load(self, delegate):
        view = self
        files = view.model().files
        width = view.columnWidth(0)
        cur = 0
        timer = QTimer(view)
        cache_id = self.cache_id

        def step():
            nonlocal width, cur, files, cache_id
            model = view.model()
            if model.files is not files:
                cur = 0
                files = view.model().files
                ImageDelegate.do_get_image.cache_clear()
            if view.columnWidth(0) != 0 and view.columnWidth(0) != width:
                cur = 0
                width = view.columnWidth(0)
                ImageDelegate.do_get_image.cache_clear()
            if self.cache_id != cache_id:
                cache_id = self.cache_id
                cur = 0
            if not self.use_cache:
                cur = len(files)
            else:
                info = ImageDelegate.do_get_image.cache_info()
                if info.maxsize is not None and info.currsize >= info.maxsize:
                    cur = len(files)
            if cur < len(files) and width != 0:
                delegate.do_get_image(os.path.join(model.folder,
                                                   model.files[cur]), width)
                cur += 1
            if cur >= len(files):
                timer.setInterval(1000)
            else:
                timer.setInterval(0)

        timer.timeout.connect(step)
        timer.start()


class ImageDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cache = {}

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        pixmap = self.get_pixmap(option, index)
        return QSize() if pixmap.isNull() else pixmap.size()

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        pixmap = self.get_pixmap(option, index)
        if not pixmap.isNull():
            view = option.styleObject
            view.setRowHeight(index.row(), pixmap.height())
            painter.drawImage(option.rect, pixmap)

    def get_pixmap(self, option: QStyleOptionViewItem,
                   index: QModelIndex) -> QImage:
        view = option.styleObject
        model = view.model()
        w = view.columnWidth(0)
        if w == 0:
            return QImage()
        else:
            file = model.data(index)
            file = os.path.join(model.folder, file)
            if os.path.isdir(file):
                return QImage()
            return self.do_get_image(file, w)

    @lru_cache(maxsize=None)
    def do_get_image(self, file, w):
        image = QImage(file)
        image = image.scaledToWidth(w)
        return image


translate = QCoreApplication.translate
