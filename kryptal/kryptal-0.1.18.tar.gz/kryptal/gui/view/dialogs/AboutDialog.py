import pkg_resources
from PyQt5 import uic  #type: ignore
from PyQt5.QtWidgets import QWidget  #type: ignore
from kryptal.pluginmanager.KryptalPlugins import KryptalPlugins
from kryptal.gui.view.utils.AsyncQDialog import AsyncQDialog
from typing_extensions import final


@final
class AboutDialog(AsyncQDialog):
    def __init__(self, plugins: KryptalPlugins, parent: QWidget = None):
        super().__init__(parent)

        uipath = pkg_resources.resource_filename(__name__, "about.ui")
        uic.loadUi(uipath, self)

        self.versionLabel.setText(pkg_resources.require("Kryptal")[0].version)
        self.filesystemsList.addItems([fs.name() for fs in plugins.filesystems().values()])
        self.storagesList.addItems([sp.name() for sp in plugins.storage_providers().values()])
