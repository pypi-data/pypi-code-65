#!/usr/bin/python
# coding: utf-8

import solid as s
import solid.utils as su

from .object import ObjectCAD


class BentPipeCAD(ObjectCAD):

    """Class to produce a bent pipe. Can only produce quarters of a donut"""

    def __init__(self, ext_d: float, int_d: float, r: float, quarters: int = 1) -> None:

        """
        ext_d: external diameter of the pipe
        int_d: internal diameter of the pipe. If 0, the pipe becomes a bent
               cylinder
        r: radius of the pipe: from the origin to the middle of the pipe
        quarters: number of quarter. 1 yields a 90° turn, 2 yields a U-turn

        Arguments:
            ext_d {float} -- [description]
            int_d {float} -- [description]
            r {float} -- [description]

        Keyword Arguments:
            quarters {int} -- [description] (default: {1})

        Raises:
            ValueError -- [description]

        Returns:
            None
        """

        # Raise an error if quarters is aberrant
        if quarters < 1 or quarters > 4:
            raise ValueError("quarters should be between 1 and 4")

        self.ext_d = ext_d
        self.int_d = int_d
        self.r = r
        self.quarters = quarters

        self._buildCadCode()

    def _buildCadCode(self) -> None:

        """
        Build the CAD code w SolidPython. Store the code in self.code, store
        the CAD object in self.cad

        Returns:
            None
        """

        # Produce the outer bent cylinder
        outer = s.rotate_extrude(convexity=5)(
            su.right(self.r + self.int_d / 2)(s.circle(r=self.ext_d / 2))
        )

        # if int_d=0, don't subtract the inner tube. Avoids a bug in FreeCAD
        if self.int_d > 0:
            # Produce the inner bent cylinder
            inner = s.rotate_extrude(convexity=5)(
                su.right(self.r + self.int_d / 2)(s.circle(r=self.int_d / 2))
            )

            # Substract inner tube from outer tube, make the pipe hollow
            total = outer - inner
        else:
            total = outer

        # Select self.quarters quarters of the donut
        if self.quarters == 1:
            c = su.down(self.r)(s.cube(2 * self.r))
            total *= c
        elif self.quarters == 2:
            c = su.down(self.r)(su.left(2 * self.r)(s.cube(4 * self.r)))
            total *= c
        elif self.quarters == 3:
            c = su.down(self.r)(s.cube(2 * self.r))
            total -= c

        return total


if __name__ == "__main__":
    # p = BentPipe(20, 15, 30, quarters=2)

    pipe_in = BentPipeCAD(2, 0, 3).cad
    pipe_in = su.rotate([-90, 0, 0])(pipe_in)
    pipe_in = su.up(3)(pipe_in)
    su.scad_render_to_file(pipe_in)
    pass
