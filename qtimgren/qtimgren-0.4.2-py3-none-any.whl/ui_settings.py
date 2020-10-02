# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings.ui'
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


class Ui_settings(object):
    def setupUi(self, settings):
        if not settings.objectName():
            settings.setObjectName(u"settings")
        settings.resize(243, 163)
        self.verticalLayout = QVBoxLayout(settings)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(settings)
        self.label.setObjectName(u"label")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.use_cache = QCheckBox(settings)
        self.use_cache.setObjectName(u"use_cache")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.use_cache)

        self.label_2 = QLabel(settings)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.cache_size = QSpinBox(settings)
        self.cache_size.setObjectName(u"cache_size")
        self.cache_size.setMinimum(-1)
        self.cache_size.setMaximum(65535)
        self.cache_size.setSingleStep(100)
        self.cache_size.setValue(1000)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.cache_size)

        self.label_3 = QLabel(settings)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self.language = QComboBox(settings)
        self.language.setObjectName(u"language")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.language)


        self.verticalLayout.addLayout(self.formLayout)

        self.verticalSpacer = QSpacerItem(20, 11, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.buttonBox = QDialogButtonBox(settings)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)

#if QT_CONFIG(shortcut)
        self.label.setBuddy(self.use_cache)
        self.label_2.setBuddy(self.cache_size)
        self.label_3.setBuddy(self.language)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(settings)
        self.buttonBox.accepted.connect(settings.accept)
        self.buttonBox.rejected.connect(settings.reject)

        QMetaObject.connectSlotsByName(settings)
    # setupUi

    def retranslateUi(self, settings):
        settings.setWindowTitle(QCoreApplication.translate("settings", u"Settings", None))
#if QT_CONFIG(whatsthis)
        self.label.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
        self.label.setText(QCoreApplication.translate("settings", u"&Use cache", None))
#if QT_CONFIG(whatsthis)
        self.use_cache.setWhatsThis(QCoreApplication.translate("settings", u"If unchecked no image caching will occur. It will save memory at the price of slow and not smooth scrolling", None))
#endif // QT_CONFIG(whatsthis)
        self.use_cache.setText("")
        self.label_2.setText(QCoreApplication.translate("settings", u"Cache &size", None))
#if QT_CONFIG(whatsthis)
        self.cache_size.setWhatsThis(QCoreApplication.translate("settings", u"Maximum number of images that can be cached or \"unlimited'. It should be unlimited if you have enough memory, but can allow qtimgren to run on smaller systems.", None))
#endif // QT_CONFIG(whatsthis)
        self.cache_size.setSpecialValueText(QCoreApplication.translate("settings", u"Unlimited", None))
#if QT_CONFIG(whatsthis)
        self.label_3.setWhatsThis(QCoreApplication.translate("settings", u"Choose the language for the interface", None))
#endif // QT_CONFIG(whatsthis)
        self.label_3.setText(QCoreApplication.translate("settings", u"&Language", None))
    # retranslateUi

