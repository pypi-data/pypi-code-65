import logging

from aio_wx_widgets.frame import DefaultFrame
from demo.controller.controller_one import ControllerOne
from demo.model.demo_model import DemoModel
from demo.views.view_one import ViewOne

_LOGGER = logging.getLogger(__name__)


class MainWindow(DefaultFrame):
    def __init__(self):
        super().__init__("Main window")

        model = DemoModel()
        controller = ControllerOne(model)
        view = ViewOne(self, controller)
        view.populate()
