import os, sys, urllib.request, json
import PySide2.QtQml
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import QStringListModel, Qt, QUrl, QSize, QObject, Slot
from PySide2.QtGui import QGuiApplication
from markipy.basic import Folder
from pathlib import Path


class PythonClass(QObject):
    @Slot(str, result=list)  # also works: @pyqtSlot(QVariant, result=QVariant)
    def back_to_python(self, variable):
        print(variable)
        return ["python is awesome!"]


def DisplayData(data):
    # Set up the application window
    app = QGuiApplication(sys.argv)
    view = QQuickView()
    view.setMaximumSize(QSize(960, 500))
    view.setResizeMode(QQuickView.SizeRootObjectToView)

    # Expose the controllers to the Qml code
    my_model = QStringListModel()
    my_model.setStringList(data)

    pclass = PythonClass()
    view.rootContext().setContextProperty("myModel", my_model)
    view.rootContext().setContextProperty("PythonClass", pclass)

    # Load the QML file
    qml_file = os.path.join(os.path.dirname(__file__), "view.qml")
    view.setSource(QUrl.fromLocalFile(os.path.abspath(qml_file)))

    # Show the window
    if view.status() == QQuickView.Error:
        sys.exit(-1)
    view.show()

    # execute and cleanup
    app.exec_()
    del view


def ExampleDisplayData():
    DisplayData([str(x) for x in Folder(Path().home()).ls()])


if __name__ == '__main__':
    ExampleDisplayData()
