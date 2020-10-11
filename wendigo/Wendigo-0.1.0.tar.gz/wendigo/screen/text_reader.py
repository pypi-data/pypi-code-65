from pathlib import Path
from pytesseract import image_to_string
from wendigo import Area
from wendigo.core import TemporaryDirectory
from wendigo.screen.form_controller import FormController

class TextReader:
    """
    Text reader.
    """
    @classmethod
    def _read(cls, image: "Image", lang: str) -> str:
        """
        Read text from an image by Tesseract.

        Parameters
        ----------
        image: Image.
        lang: language such as eng, jpn, jpn_vert. Run "tesseract --list-langs" to check.

        Returns
        -------
        text: Text.
        """
        with TemporaryDirectory() as tmpdir:
            path = str(Path(tmpdir).joinpath("image_to_string.png"))
            image.save(path)
            return image_to_string(path, lang=lang)

    @classmethod
    def read(cls, area: Area=None, scale: float=1.0, lang: str=None) -> str:
        """
        Read text by Tesseract.

        Parameters
        ----------
        area: Area.
        scale: Scale.
        lang: language such as eng, jpn, jpn_vert. Run "tesseract --list-langs" to check.

        Returns
        -------
        text: Text.
        """
        image = FormController.capture(area=area, scale=scale, grayscale=True)
        return cls._read(image, lang)

    @classmethod
    def read_window(cls, form_class: str=None, form_title: str=None, client_only: bool=False,
        scale: float=1.0, lang: str=None) -> str:
        """
        Read text by Tesseract.

        Parameters
        ----------
        form_class: Form class.
        form_title: Form title.
        client_only: Only the client area or not.
        scale: Scale.
        lang: language such as eng, jpn, jpn_vert. Run "tesseract --list-langs" to check.

        Returns
        -------
        text: Text.
        """
        image = FormController.capture_window(form_class=form_class, form_title=form_title, client_only=client_only, scale=scale, grayscale=True)
        return cls._read(image, lang) if image is not None else ""