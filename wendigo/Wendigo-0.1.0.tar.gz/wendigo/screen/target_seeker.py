import cv2
import numpy as np
from enum import Enum
from pathlib import Path
from typing import List, Tuple
from wendigo.core import Area
from wendigo.screen.form_controller import FormController

class HaarCascade(Enum):
    """
    Haar cascade classifiers.
    """
    Frontalface = "haarcascade_frontalface_alt.xml"
    Upperbody = "haarcascade_upperbody.xml"
    Lower_body = "haarcascade_lowerbody.xml"
    Fullbody = "haarcascade_fullbody.xml"

class TargetSeeker:
    """
    Target seeker.
    """
    @classmethod
    def seek(cls, template: str, scale: float=1.0, threshold: float=0.8,
        form_class: str=None, form_title: str=None, client_only: bool=False) -> Tuple[Area, float]:
        """
        Seek a target.

        Parameters
        ----------
        template: Template file path.
        scale: Scale.
        threshold: Threshold.
        form_class: Form class.
        form_title: Form title.
        client_only: Only the client area or not.

        Returns
        -------
        area: Area.
        probability: Probability.
        """
        image = FormController.capture_window(form_class=form_class, form_title=form_title, client_only=client_only, scale=scale, grayscale=True, as_array=True)
        if image is None: return None, 0    # Form doesn't exists.

        template = cv2.imread(template, cv2.IMREAD_GRAYSCALE)
        width, height = template.shape[::-1]

        if scale != 1.0:
            template = cv2.resize(template, (round(width * scale), round(height * scale)))

        res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        pt = np.unravel_index(np.argmax(res), res.shape)[::-1]
        probability = res[pt[1]][pt[0]]
        
        s = 1 / scale
        return Area(pt[0] * s, pt[1] * s, width, height) if probability >= threshold else None, probability

    @classmethod
    def _detect(cls, haar_cascade: HaarCascade, image: "Image", scale: float, **kwargs) -> List[Area]:
        """
        Detect something.

        Parameters
        ----------
        haar_cascade: Haar cascade classifier.
        image: Image.
        scale: Scale.
        kwargs: Args for detectMultiScale.

        Returns
        -------
        areas: Areas.
        """
        path = str(Path(cv2.__path__[0]).joinpath("data", haar_cascade.value))
        detected = cv2.CascadeClassifier(path).detectMultiScale(image, **kwargs)

        s = 1 / scale
        return [Area(x * s, y * s, w * s, h * s) for x, y, w, h in detected]

    @classmethod
    def _detect_area(cls, haar_cascade: HaarCascade, area: Area, scale: float, **kwargs) -> List[Area]:
        """
        Detect something in an area.
        
        Parameters
        ----------
        haar_cascade: Haar cascade classifier.
        area: Area.
        scale: Scale.
        kwargs: Args for detectMultiScale.
        
        Returns
        -------
        areas: Areas.
        """
        image = FormController.capture(area=area, scale=scale, grayscale=True, as_array=True)
        return cls._detect(haar_cascade, image, scale, **kwargs)

    @classmethod
    def _detect_window(cls, haar_cascade: HaarCascade,
        form_class: str, form_title: str, client_only: bool, scale: float, **kwargs) -> List[Area]:
        """
        Detect something in a window.

        Parameters
        ----------
        haar_cascade: Haar cascade classifier.
        form_class: Form class.
        form_title: Form title.
        client_only: Only the client area or not.
        scale: Scale.
        kwargs: Args for detectMultiScale.
        
        Returns
        -------
        areas: Areas.
        """
        image = FormController.capture_window(form_class=form_class, form_title=form_title, client_only=client_only, scale=scale, grayscale=True, as_array=True)
        return cls._detect(haar_cascade, image, scale, **kwargs) if image is not None else []

    @classmethod
    def detect_frontalfaces(cls, area: Area=None, scale: float=1.0, **kwargs) -> List[Area]:
        """
        Detect frontal faces.

        Parameters
        ----------
        area: Area.
        scale: Scale.
        kwargs: Args for detectMultiScale.

        Returns
        -------
        areas: Areas.
        """
        return cls._detect_area(HaarCascade.Frontalface, area, scale, **kwargs)
    
    @classmethod
    def detect_frontalfaces_window(cls, form_class: str=None, form_title: str=None, client_only: bool=False,
        scale: float=1.0, **kwargs) -> List[Area]:
        """
        Detect frontal faces in a window.

        Parameters
        ----------
        form_class: Form class.
        form_title: Form title.
        client_only: Only the client area or not.
        scale: Scale.
        kwargs: Args for detectMultiScale.

        Returns
        -------
        areas: Areas.
        """
        return cls._detect_window(HaarCascade.Frontalface, form_class, form_title, client_only, scale, **kwargs)

    @classmethod
    def detect_upperbodies(cls, area: Area=None, scale: float=1.0, **kwargs) -> List[Area]:
        """
        Detect upper bodies.

        Parameters
        ----------
        area: Area.
        scale: Scale.
        kwargs: Args for detectMultiScale.

        Returns
        -------
        areas: Areas.
        """
        return cls._detect_area(HaarCascade.Upperbody, area, scale, **kwargs)
    
    @classmethod
    def detect_upperbodies_window(cls, form_class: str=None, form_title: str=None, client_only: bool=False,
        scale: float=1.0, **kwargs) -> List[Area]:
        """
        Detect upper bodies in a window.

        Parameters
        ----------
        form_class: Form class.
        form_title: Form title.
        client_only: Only the client area or not.
        scale: Scale.
        kwargs: Args for detectMultiScale.

        Returns
        -------
        areas: Areas.
        """
        return cls._detect_window(HaarCascade.Upperbody, form_class, form_title, client_only, scale, **kwargs)

    @classmethod
    def detect_lowerbodies(cls, area: Area=None, scale: float=1.0, **kwargs) -> List[Area]:
        """
        Detect lower bodies.

        Parameters
        ----------
        area: Area.
        scale: Scale.
        kwargs: Args for detectMultiScale.

        Returns
        -------
        areas: Areas.
        """
        return cls._detect_area(HaarCascade.Lower_body, area, scale, **kwargs)
    
    @classmethod
    def detect_lowerbodies_window(cls, form_class: str=None, form_title: str=None, client_only: bool=False,
        scale: float=1.0, **kwargs) -> List[Area]:
        """
        Detect lower bodies in a window.

        Parameters
        ----------
        form_class: Form class.
        form_title: Form title.
        client_only: Only the client area or not.
        scale: Scale.
        kwargs: Args for detectMultiScale.

        Returns
        -------
        areas: Areas.
        """
        return cls._detect_window(HaarCascade.Lower_body, form_class, form_title, client_only, scale, **kwargs)

    @classmethod
    def detect_fullbodies(cls, area: Area=None, scale: float=1.0, **kwargs) -> List[Area]:
        """
        Detect full bodies.

        Parameters
        ----------
        area: Area.
        scale: Scale.
        kwargs: Args for detectMultiScale.

        Returns
        -------
        areas: Areas.
        """
        return cls._detect_area(HaarCascade.Fullbody, area, scale, **kwargs)
    
    @classmethod
    def detect_fullbodies_window(cls, form_class: str=None, form_title: str=None, client_only: bool=False,
        scale: float=1.0, **kwargs) -> List[Area]:
        """
        Detect full bodies in a window.

        Parameters
        ----------
        form_class: Form class.
        form_title: Form title.
        client_only: Only the client area or not.
        scale: Scale.
        kwargs: Args for detectMultiScale.

        Returns
        -------
        areas: Areas.
        """
        return cls._detect_window(HaarCascade.Fullbody, form_class, form_title, client_only, scale, **kwargs)