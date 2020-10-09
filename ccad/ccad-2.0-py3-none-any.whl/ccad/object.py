#!/usr/bin/python
# coding: utf-8

import solid as s

from . import app_constants


class ObjectCAD:

    """
    Base class for all the CAD objects (reactor, siphon, etc). Implement
    basic methods. _buildCadCode must be re-implemented in all new CAD class
    """

    # Type of module, short and long versions
    module_type: str
    module_type_short: str

    # Internal ID to identify each module. Will be initialized by Assembly
    internal_id: str

    # Module name, so the user can change modules' name
    # Will be initialized with value of internal_id
    module_name: str

    header = "$fn = {};$fs = {};"

    @property
    def fn(self) -> float:

        """
        return OpenSCAD rendering setting fn

        Returns:
            float -- [description]
        """

        try:
            return self._fn
        except AttributeError:
            return app_constants.fn

    @fn.setter
    def fn(self, value: float) -> None:

        """
        Set OpenSCAD rendering setting fn

        Arguments:
            value {float} -- [description]

        Returns:
            None
        """

        self._fn = value

    @property
    def fs(self) -> float:

        """
        return OpenSCAD rendering setting fs

        Returns:
            float -- [description]
        """

        try:
            return self._fs
        except AttributeError:
            return app_constants.fs

    @fs.setter
    def fs(self, value: float):

        """
        Set OpenSCAD rendering setting fs

        Arguments:
            value {float} -- [description]
        """

        self._fs = value

    @property
    def cad(self) -> s.objects:

        """
        Return the reactor as a CAD object (proper object to work on)

        Returns:
            s.objects -- [description]
        """

        return self._buildCadCode()

    @property
    def code(self) -> str:

        """
        Return the OpenSCAD code for the current reactor

        Returns:
            str -- [description]
        """

        header = self.header.format(self.fn, self.fs)

        return s.scad_render(self.cad, file_header=header)

    def isConnected(self) -> bool:

        """
        Check if the object is connected to another one.
        To be subclassed

        Returns:
            bool: True if connected, False otherwise
        """

    def renderToFile(self, file_path: str) -> None:

        """
        Render the object into a scad file
        https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Other_Language_Features#$fa,_$fs_and_$fn

        Arguments:
            file_path (str): path for destination file
        """

        header = self.header.format(self.fn, self.fs)

        s.scad_render_to_file(
            self.cad, file_path, file_header=header, include_orig_code=False
        )

    def _buildCadCode(self):

        """To be sub-classed"""

        pass

    def __str__(self):

        if hasattr(self, "infos"):
            # Reactor-like objects have an 'infos' dict
            return repr(self) + " " + repr(self.infos)
        else:
            return self.code


if __name__ == "__main__":
    pass
