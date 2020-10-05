"""Settings widget"""


# --- import --------------------------------------------------------------------------------------


import collections
import logging
import os

from qtpy import QtWidgets

from ..core.ini import INI

from .tab_widget import TabWidget


# --- define --------------------------------------------------------------------------------------


here = os.path.abspath(os.path.dirname(__file__))

colors = INI(os.path.join(here, "colors.ini")).dictionary["night"]

log = logging.getLogger(__name__)


# --- class ---------------------------------------------------------------------------------------


class SettingsWidget(TabWidget):
    def __init__(self, parent):
        super().__init__()
        self.add_tab("BASIC")
        self.add_tab("ADVANCED")
        self.add_tab("LOGS")
        self.add_tab("HARDWARE")
