#!/usr/bin/python
# coding: utf-8


class TopInlet:

    """
    A top inlet is an inlet on the top of the reactor. It can't be connected.
    It is defined with:

    - Diameter of the inlet (he hole)
    - length: (vertical) length of the inlet, to adjust the length for thread
    - Walls of the inlet (around the hole)
    - type_io: Type for I/O (luer, custom, maybe more in the future)
    - x: position of the center in x, reference center of top of reactor
    - y: position of the center in y, reference center of top of reactor
    """

    def __init__(
        self,
        diameter: float,
        length: float,
        walls: float,
        type_io: str,
        x: float = 0,
        y: float = 0,
    ) -> None:

        """
        Arguments:
            diameter {float} -- [description]
            length {float} -- [description]
            walls {float} -- [description]
            type_io {str} -- [description]

        Keyword Arguments:
            x {float} -- [description] (default: {0})
            y {float} -- [description] (default: {0})

        Returns:
            None
        """

        self.diameter = diameter
        self.length = length
        self.walls = walls
        self.type_io = type_io
        self.x = x
        self.y = y

    def __str__(self):

        dico = {}
        dico["diameter"] = self.diameter
        dico["length"] = self.length
        dico["walls"] = self.walls
        dico["type_io"] = self.type_io
        dico["x"] = self.x
        dico["y"] = self.y

        output = repr(self) + " " + str(dico)

        return output


if __name__ == "__main__":
    out = TopInlet(5, 3, 0, "luer")
    print(out)
    pass
