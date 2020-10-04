"""Provides Images class.

Synopsis:
# Assumes path_to_images directory has arrow.tif file:

root = tkinter.Tk()  # Must be created before load_dir is called.
image_bank = ImageBank(root)
ImageBank.load_dir(path_to_images, "*.tif")

assert "arrow" in ImageBank
assert Images.arrow

tkinter.Label(root, image=Images.arrow)


"""
import tkinter
from typing import Union, Iterable, Optional
from tkinter import PhotoImage

from pathlib import Path


from tk_oddbox.const import CharSet


class _Images:
    """Class for accessing images loaded into ImageLoader.

    Do not import this class, import its object called
    Images which is constructed at bottom of file. This
    object gives access to the images loaded by the Loader
    as attributes and a couple dict like special methods.

    """

    def __iter__(self) -> Iterable[str]:
        for name in ImageLoader.images.keys():
            yield name

    def __getitem__(self, name: str) -> PhotoImage:
        return ImageLoader.images[name]

    def __len__(self) -> int:
        return len(ImageLoader.images)

    def __contains__(self, name: str) -> bool:
        return name in ImageLoader.images


class ImageLoader:
    """This is for loading images, use Images to access them."""

    images = {}

    def __init__(self, root: tkinter.Tk):
        self.root = root

    @staticmethod
    def _name_ok(name: str) -> bool:
        """Helper to see if name should be used as attr.

        Args:
            name: image name to evaluate
        Returns:
            True iff name starts with letter and only has
                letters and underscores.
        """
        if not name:
            return False
        if name[0] not in CharSet.LETTER:
            return False
        for char in name[1:]:
            if char not in CharSet.IDENTIFIER:
                return False
        return True

    def set_image(self, name: str, image: tkinter.PhotoImage):
        """Set an image under specified name.

        Args:
            name: attribute name, e.g. "foo" means image available as Images.foo
            image: tkinter photo image to be stored
        """
        self.images[name] = image
        setattr(Images, name, image)

    def load_dir(self, directory: Union[Path, str], glob: str) -> int:
        """Load files within directory with specified suffix.

        Depending on glob argument, the load will recursively
        walk sub directories. See pathlib.Path.glob() doc.

        Files are named after the stem part of file name. for
        example image in "/some/path/foo.jpg" is named "foo".
        Multiple images with the same name will result in only
        the last one stored being remembered.

        For images whose names start with a letter and have
        only letters, digits and underscores, a class attribute
        is added to the Images object. For example Images.foo
        for "/some/path/foo.jpg". If there is already such an
        image it is overwritten.

        Args:
            directory: directory to find files directly under.
            glob: file extension including . for example: ".gif"
        Returns:
            number of images loaded (including overwrites)
        """
        count = 0
        # If directory arg is a string, make it a Path
        if isinstance(directory, str):
            directory = Path(directory)
        # find images and load them.
        for path in directory.glob(glob):
            name = path.stem
            image = PhotoImage(file=path)
            self.images[name] = image
            if self._name_ok(name):
                setattr(Images, name, image)
                self.images[name] = image
            count += 1
        return count


# This will be initialized with no images available.
# To add some construct an ImageLoader (which requires
# a tkinter.Tk object as an argument) and then load
# some image directories into it.
Images = _Images()
