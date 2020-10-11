import numpy as np
import warnings
from collections import namedtuple
from PIL import ImageGrab
from time import sleep
from typing import List, Union
from wendigo import IS_ADMIN, Colors, Point
from wendigo.core import Area, Point
from wendigo.screen.dll import FormController as DllFormController
from wendigo.system.color import Color
from wendigo.warnings import AdministrationWarning

FormInfo = namedtuple("FormInfo", ("form_class", "form_title"))

class FormController:
    """
    Form controller.
    """
    @classmethod
    def get_form_info(cls) -> List[FormInfo]:
        """
        Get form information.

        Returns
        -------
        form_info: Form information.
        """
        return [FormInfo(form_class=c, form_title=t) for c, t in DllFormController.GetFormInfo()]

    @classmethod
    def get_area(cls, form_class: str=None, form_title: str=None, client_only: bool=False) -> Area:
        """
        Get an area by a form class or title.

        Parameters
        ----------
        form_class: Form class.
        form_title: Form title.
        client_only: Only the client area or not.

        Returns
        -------
        area: Area.
        """
        rect = DllFormController.GetArea(form_class, form_title, client_only)
        return Area(rect.X, rect.Y, rect.Width, rect.Height) if rect is not None else None

    @classmethod
    def activate_form(cls, form_class: str=None, form_title: str=None, duration: float=0.5):
        """
        Activate a form by a class or title.

        Parameters
        ----------
        form_class: Form class.
        form_title: Form title.
        duration: Duration in seconds until the form pops up.
        """
        if not IS_ADMIN:
            warnings.warn("Because it's not administrator mode, activate_form won't work if the target form is minimized", AdministrationWarning)

        DllFormController.ActivateForm(form_class, form_title)
        sleep(duration)

    @classmethod
    def get_color(cls, position: Point) -> Color:
        """
        Get color of a pixel.

        Parameters
        ----------
        position: Position.

        Returns
        -------
        color: Color.
        """
        return Colors.to_color(DllFormController.GetColor(position.x, position.y))

    @classmethod
    def _capture(cls, area: Area, scale: float, grayscale: bool, as_array: bool) -> Union["Image", np.ndarray]:
        """
        Capture screen.

        Parameters
        ----------
        area: Area.
        scale: Scale.
        grayscale: Make it grayscale or not.
        as_array: Get the image as ndarray or not.

        Returns
        -------
        image: Image.
        """
        bbox = (area.x, area.y, area.x + area.width, area.y + area.height) if area is not None else None
        image = ImageGrab.grab(bbox=bbox)
        if scale != 1.0:
            image = image.resize((round(image.width * scale), round(image.height * scale)))
        if grayscale:
            image = image.convert("L")
        return np.array(image) if as_array else image

    @classmethod
    def capture(cls, area: Area=None, scale: float=1.0, grayscale: bool=False, as_array: bool=False) -> Union["Image", np.ndarray]:
        """
        Capture screen.

        Parameters
        ----------
        area: Area.
        scale: Scale.
        grayscale: Make it grayscale or not.
        as_array: Get the image as ndarray or not.

        Returns
        -------
        image: Image.
        """
        return cls._capture(area, scale, grayscale, as_array)

    @classmethod
    def capture_window(cls, form_class: str=None, form_title: str=None, client_only: bool=False,
        scale: float=1.0, grayscale: bool=False, as_array: bool=False) -> Union["Image", np.ndarray]:
        """
        Capture window.

        Parameters
        ----------
        form_class: Form class.
        form_title: Form title.
        client_only: Only the client area or not.
        scale: Scale.
        grayscale: Make it grayscale or not.
        as_array: Get the image as ndarray or not.

        Returns
        -------
        image: Image.
        """
        if form_class is None and form_title is None:
            raise ValueError("Form class or title must be specified.")

        cls.activate_form(form_class=form_class, form_title=form_title)
        area = cls.get_area(form_class=form_class, form_title=form_title, client_only=client_only)
        if area is None: return None    # Form doesn't exist.
        
        return cls._capture(area, scale, grayscale, as_array)