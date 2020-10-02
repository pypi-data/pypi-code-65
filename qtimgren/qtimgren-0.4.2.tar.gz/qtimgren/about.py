# -*- coding: utf-8 -*-

"""
Module implementing About.
"""

from PySide2.QtWidgets import QDialog, QWidget

from .ui_about import Ui_About
from . import __version__
from pyimgren import __version__ as lib_version
from typing import Optional


class About(QDialog, Ui_About):
    """
    Class documentation goes here.
    """
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Constructor
        
        @param parent reference to the parent widget
        """
        super(About, self).__init__(parent)
        self.setupUi(self)
        self.version.setText(self.version.text() + __version__)
        lib_label = self.libversion
        lib_label.setText(lib_label.text().replace('0.0.0', lib_version))
