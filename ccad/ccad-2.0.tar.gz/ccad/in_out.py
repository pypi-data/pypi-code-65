#!/usr/bin/python
# coding: utf-8

from typing import Optional


class InputOutput:

    """
    An output is a circle in the 3D space.
    It is defined with:

    - Height of the input/output from the bottom of the object
    - Diameter of the circle
    - Angle of the input, starting from x axis, rotating in the trigonometric
    direction
    """

    def __init__(
        self,
        height: float,
        diameter: float,
        angle: float,
        external: bool = False,
        chamber: Optional[str] = None,
    ) -> None:

        """
        Arguments:
            height {float} -- [description]
            diameter {float} -- [description]
            angle {float} -- [description]

        Keyword Arguments:
            external {bool} -- [description] (default: {False})
            chamber {Optional[str]} -- [description] (default: {None})

        Returns:
            None
        """

        self.height = height
        self.diameter = diameter
        self.angle = angle

        # Bool, if external is true, it's an external IO
        self.external = external

        # Identify to which chamber the InputOutput belongs (used in
        # FloatingFilterReactor)
        self.chamber = chamber

        # Boolean: I/O is connected or not
        self.connected = False

        # ConnectorCAD: I/O it is connected to
        self.connectedTo = None

    @property
    def infos(self) -> dict:

        """
        [summary]

        Returns:
            dict -- [description]
        """

        dico = {}
        dico["height"] = self.height
        dico["diameter"] = self.diameter
        dico["angle"] = self.angle
        dico["external"] = self.external
        dico["chamber"] = self.chamber

        return dico

    def __str__(self):

        output = repr(self) + " " + str(self.infos)

        return output


if __name__ == "__main__":
    out = InputOutput(50, 3, 180, False, "top")
    print(out)
    pass
