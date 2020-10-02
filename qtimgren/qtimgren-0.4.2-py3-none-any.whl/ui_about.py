# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'about.ui'
##
## Created by: Qt User Interface Compiler version 5.15.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_About(object):
    def setupUi(self, About):
        if not About.objectName():
            About.setObjectName(u"About")
        About.setWindowModality(Qt.ApplicationModal)
        About.resize(400, 300)
        About.setSizeGripEnabled(False)
        About.setModal(True)
        self.Ok = QPushButton(About)
        self.Ok.setObjectName(u"Ok")
        self.Ok.setGeometry(QRect(130, 220, 93, 28))
        self.Ok.setAutoDefault(True)
        self.label = QLabel(About)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(50, 50, 81, 16))
        self.version = QLabel(About)
        self.version.setObjectName(u"version")
        self.version.setGeometry(QRect(50, 110, 151, 16))
        self.libversion = QLabel(About)
        self.libversion.setObjectName(u"libversion")
        self.libversion.setGeometry(QRect(50, 150, 271, 16))

        self.retranslateUi(About)
        self.Ok.clicked.connect(About.accept)

        self.Ok.setDefault(True)


        QMetaObject.connectSlotsByName(About)
    # setupUi

    def retranslateUi(self, About):
        About.setWindowTitle(QCoreApplication.translate("About", u"About", None))
        self.Ok.setText(QCoreApplication.translate("About", u"Ok", None))
        self.label.setText(QCoreApplication.translate("About", u"QtImgren", None))
        self.version.setText(QCoreApplication.translate("About", u"Version: ", None))
        self.libversion.setText(QCoreApplication.translate("About", u"(pyimgren version: 0.0.0)", None))
    # retranslateUi

