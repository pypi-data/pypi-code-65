import markipy as mpy
from markipy.basic import Folder, File

DEFAULT_INSTALLED_PYTHON_FOLDER = Folder(File(mpy.__file__)().parent)
DEFAULT_QML_VIEW_FOLDER = Folder(DEFAULT_INSTALLED_PYTHON_FOLDER() / 'gui' / 'views' / 'qml')

from .app import QApp
from .views import QTView
from .controllers import ListController
