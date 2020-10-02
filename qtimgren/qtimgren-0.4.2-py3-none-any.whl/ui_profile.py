# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'profile.ui'
##
## Created by: Qt User Interface Compiler version 5.15.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(696, 281)
        Dialog.setSizeGripEnabled(True)
        self.layoutWidget = QWidget(Dialog)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(20, 40, 641, 188))
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setSizeConstraint(QLayout.SetNoConstraint)
        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.name = QLineEdit(self.layoutWidget)
        self.name.setObjectName(u"name")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.name)

        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(0, 24))

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.frame = QFrame(self.layoutWidget)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(0, 30))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.path = QLineEdit(self.frame)
        self.path.setObjectName(u"path")
        self.path.setGeometry(QRect(0, 0, 391, 24))
        self.change = QPushButton(self.frame)
        self.change.setObjectName(u"change")
        self.change.setGeometry(QRect(400, 0, 93, 28))

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.frame)

        self.label_3 = QLabel(self.layoutWidget)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self.mask_edit = QLineEdit(self.layoutWidget)
        self.mask_edit.setObjectName(u"mask_edit")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.mask_edit)

        self.recurseIntoSubFolderLabel = QLabel(self.layoutWidget)
        self.recurseIntoSubFolderLabel.setObjectName(u"recurseIntoSubFolderLabel")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.recurseIntoSubFolderLabel)

        self.pattern = QLineEdit(self.layoutWidget)
        self.pattern.setObjectName(u"pattern")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.pattern)


        self.verticalLayout.addLayout(self.formLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.button_box = QDialogButtonBox(self.layoutWidget)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.button_box)

#if QT_CONFIG(shortcut)
        self.label.setBuddy(self.name)
        self.label_2.setBuddy(self.path)
        self.label_3.setBuddy(self.mask_edit)
        self.recurseIntoSubFolderLabel.setBuddy(self.pattern)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.name, self.path)
        QWidget.setTabOrder(self.path, self.change)
        QWidget.setTabOrder(self.change, self.mask_edit)

        self.retranslateUi(Dialog)
        self.button_box.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Profile", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"&Name", None))
#if QT_CONFIG(whatsthis)
        self.name.setWhatsThis(QCoreApplication.translate("Dialog", u"<html><head/><body><p>Name of the profile</p><p>Will be used in the <span style=\" font-style:italic;\">Profiles</span> menu</p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.label_2.setText(QCoreApplication.translate("Dialog", u"&Directory", None))
#if QT_CONFIG(whatsthis)
        self.path.setWhatsThis(QCoreApplication.translate("Dialog", u"Path of the image (jpeg) files", None))
#endif // QT_CONFIG(whatsthis)
        self.change.setText(QCoreApplication.translate("Dialog", u"&Select", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Image &mask", None))
#if QT_CONFIG(whatsthis)
        self.mask_edit.setWhatsThis(QCoreApplication.translate("Dialog", u"Pattern of camera images (e.g. IMG*.JPG or DSCF*.JPG)", None))
#endif // QT_CONFIG(whatsthis)
        self.mask_edit.setText(QCoreApplication.translate("Dialog", u"*.JPG", None))
        self.recurseIntoSubFolderLabel.setText(QCoreApplication.translate("Dialog", u"New name &pattern", None))
        self.pattern.setText(QCoreApplication.translate("Dialog", u"%Y%m%d_%H%M%S.jpg", None))
    # retranslateUi

