# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'profiles.ui'
##
## Created by: Qt User Interface Compiler version 5.15.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_profiles(object):
    def setupUi(self, profiles):
        if not profiles.objectName():
            profiles.setObjectName(u"profiles")
        profiles.resize(602, 442)
        profiles.setSizeGripEnabled(True)
        self.horizontalLayout_2 = QHBoxLayout(profiles)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.table_view = QTableView(profiles)
        self.table_view.setObjectName(u"table_view")
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.horizontalLayout.addWidget(self.table_view)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.edit = QPushButton(profiles)
        self.edit.setObjectName(u"edit")

        self.verticalLayout.addWidget(self.edit)

        self.remove = QPushButton(profiles)
        self.remove.setObjectName(u"remove")

        self.verticalLayout.addWidget(self.remove)


        self.horizontalLayout.addLayout(self.verticalLayout)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.button_box = QDialogButtonBox(profiles)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout_2.addWidget(self.button_box)


        self.horizontalLayout_2.addLayout(self.verticalLayout_2)


        self.retranslateUi(profiles)
        self.button_box.rejected.connect(profiles.reject)

        QMetaObject.connectSlotsByName(profiles)
    # setupUi

    def retranslateUi(self, profiles):
        profiles.setWindowTitle(QCoreApplication.translate("profiles", u"Profiles", None))
#if QT_CONFIG(whatsthis)
        self.edit.setWhatsThis(QCoreApplication.translate("profiles", u"Edit the (first) selected profile", None))
#endif // QT_CONFIG(whatsthis)
        self.edit.setText(QCoreApplication.translate("profiles", u"&Edit", None))
#if QT_CONFIG(whatsthis)
        self.remove.setWhatsThis(QCoreApplication.translate("profiles", u"Remove every selected profile", None))
#endif // QT_CONFIG(whatsthis)
        self.remove.setText(QCoreApplication.translate("profiles", u"&Remove", None))
    # retranslateUi

