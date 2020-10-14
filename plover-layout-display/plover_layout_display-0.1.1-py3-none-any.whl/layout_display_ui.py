# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'layout_display/layout_display.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LayoutDisplay(object):
    def setupUi(self, LayoutDisplay):
        LayoutDisplay.setObjectName("LayoutDisplay")
        LayoutDisplay.resize(350, 200)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(LayoutDisplay.sizePolicy().hasHeightForWidth())
        LayoutDisplay.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        LayoutDisplay.setFont(font)
        LayoutDisplay.setSizeGripEnabled(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(LayoutDisplay)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_layout_name = QtWidgets.QLabel(LayoutDisplay)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_layout_name.sizePolicy().hasHeightForWidth())
        self.label_layout_name.setSizePolicy(sizePolicy)
        self.label_layout_name.setObjectName("label_layout_name")
        self.verticalLayout.addWidget(self.label_layout_name)
        self.layout_display_view = LayoutDisplayView(LayoutDisplay)
        self.layout_display_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.layout_display_view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.layout_display_view.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.layout_display_view.setRenderHints(QtGui.QPainter.Antialiasing|QtGui.QPainter.TextAntialiasing)
        self.layout_display_view.setObjectName("layout_display_view")
        self.verticalLayout.addWidget(self.layout_display_view)
        self.action_Load = QtWidgets.QAction(LayoutDisplay)
        icon = QtGui.QIcon()
        icon.addFile(":/layout_display/document.svg", QtCore.QSize(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Load.setIcon(icon)
        self.action_Load.setObjectName("action_Load")
        self.action_Reset = QtWidgets.QAction(LayoutDisplay)
        icon1 = QtGui.QIcon()
        icon1.addFile(":/layout_display/synchronize.svg", QtCore.QSize(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Reset.setIcon(icon1)
        self.action_Reset.setObjectName("action_Reset")

        self.retranslateUi(LayoutDisplay)
        self.action_Load.triggered.connect(LayoutDisplay.on_load)
        self.action_Reset.triggered.connect(LayoutDisplay.on_reset)
        QtCore.QMetaObject.connectSlotsByName(LayoutDisplay)

    def retranslateUi(self, LayoutDisplay):
        _translate = QtCore.QCoreApplication.translate
        LayoutDisplay.setWindowTitle(_translate("LayoutDisplay", "Layout Display"))
        self.label_layout_name.setAccessibleName(_translate("LayoutDisplay", "Layout Name"))
        self.label_layout_name.setAccessibleDescription(_translate("LayoutDisplay", "The currently loaded layout\'s name"))
        self.label_layout_name.setText(_translate("LayoutDisplay", "Default Layout Name"))
        self.layout_display_view.setAccessibleName(_translate("LayoutDisplay", "Layout Display Area"))
        self.layout_display_view.setAccessibleDescription(_translate("LayoutDisplay", "The display area for the loaded layout"))
        self.action_Load.setText(_translate("LayoutDisplay", "&Load"))
        self.action_Load.setToolTip(_translate("LayoutDisplay", "Select a layout file to load."))
        self.action_Reset.setText(_translate("LayoutDisplay", "&Reset"))
        self.action_Reset.setToolTip(_translate("LayoutDisplay", "Reset the layout to the default."))
from layout_display.layout_graphics import LayoutDisplayView
from . import resources_rc
