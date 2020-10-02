# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 5.15.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QDate, QDateTime, QMetaObject,
    QObject, QPoint, QRect, QSize, QTime, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter,
    QPixmap, QRadialGradient)
from PySide2.QtWidgets import *

from .main_view import View


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(793, 540)
        self.action_quit = QAction(MainWindow)
        self.action_quit.setObjectName(u"action_quit")
        self.action_about = QAction(MainWindow)
        self.action_about.setObjectName(u"action_about")
        self.action_about_qt = QAction(MainWindow)
        self.action_about_qt.setObjectName(u"action_about_qt")
        self.action_new_profile = QAction(MainWindow)
        self.action_new_profile.setObjectName(u"action_new_profile")
        self.action_manage_profiles = QAction(MainWindow)
        self.action_manage_profiles.setObjectName(u"action_manage_profiles")
        self.actionChange_Folder = QAction(MainWindow)
        self.actionChange_Folder.setObjectName(u"actionChange_Folder")
        self.action_merge = QAction(MainWindow)
        self.action_merge.setObjectName(u"action_merge")
        self.action_merge.setEnabled(True)
        self.action_settings = QAction(MainWindow)
        self.action_settings.setObjectName(u"action_settings")
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.horizontalLayout_3 = QHBoxLayout(self.centralWidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.images_display = QCheckBox(self.centralWidget)
        self.images_display.setObjectName(u"images_display")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.images_display.sizePolicy().hasHeightForWidth())
        self.images_display.setSizePolicy(sizePolicy)

        self.verticalLayout_2.addWidget(self.images_display)

        self.tableView = View(self.centralWidget)
        self.tableView.setObjectName(u"tableView")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy1)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_2.addWidget(self.tableView)

        self.groupBox = QGroupBox(self.centralWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.reset = QPushButton(self.groupBox)
        self.reset.setObjectName(u"reset")

        self.horizontalLayout_2.addWidget(self.reset)

        self.renamed = QPushButton(self.groupBox)
        self.renamed.setObjectName(u"renamed")

        self.horizontalLayout_2.addWidget(self.renamed)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.verticalLayout_2.addWidget(self.groupBox)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.centralWidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.delta = QDoubleSpinBox(self.centralWidget)
        self.delta.setObjectName(u"delta")
        self.delta.setDecimals(3)
        self.delta.setMinimum(-14400.000000000000000)
        self.delta.setMaximum(14400.000000000000000)

        self.horizontalLayout.addWidget(self.delta)

        self.rename = QPushButton(self.centralWidget)
        self.rename.setObjectName(u"rename")

        self.horizontalLayout.addWidget(self.rename)

        self.back = QPushButton(self.centralWidget)
        self.back.setObjectName(u"back")

        self.horizontalLayout.addWidget(self.back)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.horizontalLayout_3.addLayout(self.verticalLayout_2)

        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 793, 26))
        self.menu_File = QMenu(self.menuBar)
        self.menu_File.setObjectName(u"menu_File")
        self.menu_Help = QMenu(self.menuBar)
        self.menu_Help.setObjectName(u"menu_Help")
        self.menu_Profiles = QMenu(self.menuBar)
        self.menu_Profiles.setObjectName(u"menu_Profiles")
        MainWindow.setMenuBar(self.menuBar)
#if QT_CONFIG(shortcut)
        self.label.setBuddy(self.delta)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.tableView, self.delta)
        QWidget.setTabOrder(self.delta, self.rename)
        QWidget.setTabOrder(self.rename, self.back)

        self.menuBar.addAction(self.menu_File.menuAction())
        self.menuBar.addAction(self.menu_Profiles.menuAction())
        self.menuBar.addAction(self.menu_Help.menuAction())
        self.menu_File.addAction(self.action_merge)
        self.menu_File.addAction(self.action_settings)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_quit)
        self.menu_Help.addAction(self.action_about)
        self.menu_Help.addAction(self.action_about_qt)
        self.menu_Profiles.addAction(self.action_new_profile)
        self.menu_Profiles.addSeparator()
        self.menu_Profiles.addSeparator()
        self.menu_Profiles.addAction(self.action_manage_profiles)

        self.retranslateUi(MainWindow)
        self.action_quit.triggered.connect(MainWindow.close)
        self.delta.valueChanged.connect(self.tableView.delta_changed)
        self.rename.clicked.connect(self.tableView.rename)
        self.back.clicked.connect(self.tableView.back)
        self.reset.clicked.connect(self.tableView.reset_selection)
        self.renamed.clicked.connect(self.tableView.select_renamed)
        self.images_display.clicked.connect(self.tableView.display_images)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"QtImgren", None))
        self.action_quit.setText(QCoreApplication.translate("MainWindow", u"&Quit", None))
        self.action_about.setText(QCoreApplication.translate("MainWindow", u"&About", None))
        self.action_about_qt.setText(QCoreApplication.translate("MainWindow", u"About &Qt", None))
        self.action_new_profile.setText(QCoreApplication.translate("MainWindow", u"&New profile", None))
        self.action_manage_profiles.setText(QCoreApplication.translate("MainWindow", u"&Manage profiles", None))
        self.actionChange_Folder.setText(QCoreApplication.translate("MainWindow", u"Change &Folder", None))
        self.action_merge.setText(QCoreApplication.translate("MainWindow", u"&Merge", None))
        self.action_settings.setText(QCoreApplication.translate("MainWindow", u"&Settings", None))
        self.images_display.setText(QCoreApplication.translate("MainWindow", u"Display &images", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Automatic selections", None))
        self.reset.setText(QCoreApplication.translate("MainWindow", u"Default &selection", None))
        self.renamed.setText(QCoreApplication.translate("MainWindow", u"Select renamed &images", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"&Delta (minutes)", None))
        self.rename.setText(QCoreApplication.translate("MainWindow", u"&Rename", None))
        self.back.setText(QCoreApplication.translate("MainWindow", u"&Back", None))
        self.menu_File.setTitle(QCoreApplication.translate("MainWindow", u"&File", None))
        self.menu_Help.setTitle(QCoreApplication.translate("MainWindow", u"&Help", None))
        self.menu_Profiles.setTitle(QCoreApplication.translate("MainWindow", u"&Profiles", None))
    # retranslateUi

