#!/usr/bin/python
# coding: utf-8

import solid as s
import solid.utils as su
from typing import Dict

from . import constants as cst
from .exceptions import *
from .object import ObjectCAD
from .connector import ConnectorCAD
from .pipe import BentPipeCAD
from .in_out import InputOutput


class SiphonCAD(ConnectorCAD):
    def __init__(
        self,
        obj_in: ObjectCAD,
        in_io: InputOutput,
        obj_out: ObjectCAD,
        out_io: InputOutput,
        width: float,
        drill_mark: bool = False,
        reverse_siphon: bool = False, #HPD: adding a check box to reverse the siphon, when connected to an INPUT and OUTPUT on same reactor
        offsets_type: str = "minimal",
    ) -> None:

        """
        Siphon object. Will connect in_io port of obj_in to out_io port of
        obj_out. drill_mark will add a small mark where to drill to place
        to inser a plug.
        reverse_siphon ll reverse the siphon to be continous on same reactor (HPD)
        Offsets_type defines how the siphon connects to the object:
        - minimal: minimal offset, the siphon barely touches the objects
        - optimal: try to minimize siphon's length: it's embedded in the
                   objects walls

        NOTE: optimal is not implemented yet

        Arguments:
            ConnectorCAD {[type]} -- [description]
            obj_in {ObjectCAD} -- [description]
            in_io {InputOutput} -- [description]
            obj_out {ObjectCAD} -- [description]
            out_io {InputOutput} -- [description]
            width {float} -- [description]
            drill_mark {bool} -- [description]
            reverse_siphon {bool} -- [description]

        Keyword Arguments:
            offsets_type {str} -- [description] (default: {"minimal"})

        Returns:
            None
        """

        # Name/module type, used by GUI to connect slot and signals
        self.module_type = "S connector"
        self.module_type_short = "S"

        # Check input and output are valid
        self.checkConnectivity(in_io, out_io)
        self._checkInputOutput(in_io, out_io)

        self.drill_mark = drill_mark
        self.reverse_siphon = reverse_siphon

        self.obj_in = obj_in
        self.obj_out = obj_out

        # in_io and out_io are properties; santity checks performed here
        self.in_io = in_io
        self.out_io = out_io

        # If _checkInputOutput didn't crash, diameters are the same,
        # just take one
        self.diameter = self.in_io.diameter

        # Find length and width for the siphon
        self._width = self._findMinWidth()
        self._height = self._findMinHeight()

        # Define attributes with type of offset
        self.offset_in_type = offsets_type
        self.offset_out_type = offsets_type

        # Calculate offsets
        self.offset_in = offsets_type
        self.offset_out = offsets_type

        # Calculate length after calculating offsets
        self._length = self._findMinLength()

        # Coordinates. Will be modified by _cal* methods
        self.coo: Dict[str, float] = {"x": 0, "y": 0, "z": 0, "angle": 0}

        # Find where the siphon should be translated to
        self._calXYAngleTransformationsValues()

        # Apply transformations on siphon once calculated
        self._applyXYTransformations()
        self._applyAngleTransformations()

    def reconnectIOs(self, in_io: InputOutput,
        out_io: InputOutput,) -> None:
        """
        This method will reconnect the IOs. This method is needed because
        when we are redoing a connector, after an undo, the IOs were
        not set

        Arguments:
            in_io {InputOutput} -- [description]
            out_io {InputOutput} -- [description]

        Returns:
            None
        """

        self.in_io = in_io
        self.out_io = out_io

    def _findMinLength(self) -> float:

        """
        Find the minimum length of connector based on design constraints,
        i.e thickness of walls, diameter, etc

        Returns:
            float -- [description]
        """

        return self.diameter + 2 * cst.WALLS + self.offset_in + self.offset_out

    def _findMinWidth(self) -> float:

        """
        Find the minimum width of connector based on design constraints,
        i.e thickness of walls, diameter, etc

        Returns:
            float -- [description]
        """

        return self.diameter + 3 * cst.WALLS

    def _findMinHeight(self) -> float:

        """
        Find the minimum height of connector based on design constraints,
        i.e thickness of walls, diameter, etc

        Returns:
            float -- [description]
        """

        # Calculate height
        h = abs(self.out_io.height - self.in_io.height) + self.diameter + 2 * cst.WALLS

        return h

    def _checkInputOutput(self, in_io: InputOutput, out_io: InputOutput):

        """
        Make sure the diameters of the input and output objects are the same.
        Check that input and ouput are vertically distant enough

        Arguments:
            in_io {InputOutput} -- [description]
            out_io {InputOutput} -- [description]

        Raises:
            ConstraintError -- [description]
        """

        # Check that the 2 centers are distant enough in z and x
        if abs(in_io.height - out_io.height) < cst.WALLS:
            mes = "Input and output not distant enough in z to use a siphon"
            raise ConstraintError(mes)

    def _buildCadCode(self) -> s.objects.translate:

        """
        Build the CAD code w SolidPython

        Returns:
            s.objects.translate -- [description]
        """

        min_length = self._findMinLength()
        diff = self._length - min_length

        # Calculate length of horizontal tubes joining the bent pipes to the
        # outside. Add diff/2 to stretch the horizontzal tubes if user set
        # the length > min_length
        l_h_tube1 = self.diameter / 2 + self.offset_in + diff / 2 + 2 * cst.F
        l_h_tube2 = self.diameter / 2 + self.offset_out + diff / 2 + 2 * cst.F

        # Vertical tube of the siphon, calculate its length
        l_v_tube = (
            abs(self.out_io.height - self.in_io.height) - 2 * cst.WALLS + 2 * cst.F
        )

        # Vertial tube of the drill mark, calculate its length
        l_drill_m = (self.height - l_v_tube + cst.WALLS) / 2

        # Build the two horizontal pipes joining the bent pipe and the
        # input/output
        h_pipe_in = s.cylinder(r=self.diameter / 2, h=l_h_tube1)
        h_pipe_in = su.rotate([0, -90, 0])(h_pipe_in)
        h_pipe_in = su.right(l_h_tube1 - cst.F)(h_pipe_in)

        h_pipe_out = s.cylinder(r=self.diameter / 2, h=l_h_tube2)
        h_pipe_out = su.rotate([0, -90, 0])(h_pipe_out)
        h_pipe_out = su.right(self._length + cst.F)(h_pipe_out)

        # Output is higher than input
        if self.out_io.height > self.in_io.height and self.reverse_siphon is False:

            # Build the body, a simple brick
            body = s.cube([self._length, self._width, self.height])
            body = su.back(self._width / 2)(body)
            body = su.up(self.in_io.height - self.diameter / 2 - cst.WALLS)(body)

            # Translate horizontal pipe from input to bent pipe
            h_pipe_in = su.up(self.in_io.height)(h_pipe_in)

            # Bent pipe for input
            bent_pipe_in = BentPipeCAD(self.diameter, 0, cst.WALLS).cad
            bent_pipe_in = su.rotate([-90, 0, 0])(bent_pipe_in)
            bent_pipe_in = su.right(self._length / 2 - cst.WALLS)(bent_pipe_in)
            bent_pipe_in = su.up(cst.WALLS + self.in_io.height)(bent_pipe_in)

            # Build the vertical tube
            v_tube = s.cylinder(r=self.diameter / 2, h=l_v_tube)
            v_tube = su.right(self._length / 2)(v_tube)
            v_tube = su.up(self.in_io.height + cst.WALLS - cst.F)(v_tube)

            # Build the drill tube mark
            drill_m = s.cylinder(r=1.5, h=l_drill_m)
            drill_m = su.right(self._length / 2)(drill_m)
            drill_m = su.up(self.out_io.height - l_drill_m/2 + 1)(drill_m)

            # Bent pipe for output
            bent_pipe_out = BentPipeCAD(self.diameter, 0, cst.WALLS).cad
            bent_pipe_out = su.rotate([0, 0, 90])(bent_pipe_out)
            bent_pipe_out = su.rotate([90, 0, 0])(bent_pipe_out)
            bent_pipe_out = su.right(cst.WALLS + self._length / 2)(bent_pipe_out)
            bent_pipe_out = su.up(self.out_io.height - cst.WALLS)(bent_pipe_out)

            # Translate horizontal pipe from bent pipe to output
            h_pipe_out = su.up(self.out_io.height)(h_pipe_out)

            if self.reverse_siphon is True:
                print('When checked, this will allow you to reverse the siphon to xconnect back to an input/output on the same reactor...')
            else:
                print('not clicked')

        elif self.out_io.height > self.in_io.height and self.reverse_siphon is True:
            print('output higher than input, doing this function...')

            # Build the body, a simple brick
            body = s.cube([self._length, self._width, self.height])
            body = su.back(self._width / 2)(body)
            body = su.up(self.in_io.height - self.diameter / 2 - cst.WALLS)(body)

            # Translate horizontal pipe from input to bent pipe
            h_pipe_in = su.up(self.in_io.height)(h_pipe_in)

            # Bent pipe for input
            bent_pipe_in = BentPipeCAD(self.diameter, 0, cst.WALLS).cad
            bent_pipe_in = su.rotate([0, 0, 180])(bent_pipe_in) #HPD
            bent_pipe_in = su.rotate([90, 0, 0])(bent_pipe_in) #HPD
            bent_pipe_in = su.up(cst.WALLS + self.in_io.height)(bent_pipe_in)
            bent_pipe_in = su.right(self._length / 2 + cst.WALLS)(bent_pipe_in) #HPD - bent pipe in position


            #h_pipe_in = su.right(self.in_io.height + cst.WALLS / 2 + l_h_tube1)(h_pipe_in)
            h_pipe_in = su.left(l_h_tube1 - cst.F)(h_pipe_in)
            h_pipe_in = su.right(self._length + cst.F)(h_pipe_in)



            # Build the vertical tube
            v_tube = s.cylinder(r=self.diameter / 2, h=l_v_tube)
            v_tube = su.right(self._length / 2)(v_tube)
            v_tube = su.up(self.in_io.height + cst.WALLS - cst.F)(v_tube)

            # Build the drill tube mark
            drill_m = s.cylinder(r=1.5, h=l_drill_m)
            drill_m = su.right(self._length / 2)(drill_m)
            drill_m = su.up(self.out_io.height - l_drill_m/2 + 1)(drill_m)

            # Bent pipe for output
            bent_pipe_out = BentPipeCAD(self.diameter, 0, cst.WALLS).cad
            bent_pipe_out = su.rotate([0, 0, 90])(bent_pipe_out)
            bent_pipe_out = su.rotate([90, 0, 0])(bent_pipe_out)
            bent_pipe_out = su.right(cst.WALLS + self._length / 2)(bent_pipe_out)
            bent_pipe_out = su.up(self.out_io.height - cst.WALLS)(bent_pipe_out)

            # Translate horizontal pipe from bent pipe to output
            h_pipe_out = su.up(self.out_io.height)(h_pipe_out)

        # Input is higher than output
        if self.out_io.height < self.in_io.height and self.reverse_siphon is False:

            # Build the body, a simple brick
            body = s.cube([self._length, self._width, self.height])
            body = su.back(self._width / 2)(body)
            body = su.up(self.out_io.height - self.diameter / 2 - cst.WALLS)(body)

            # Translate horizontal pipe from input to bent pipe
            h_pipe_in = su.up(self.in_io.height)(h_pipe_in)

            # Bent pipe for input
            bent_pipe_in = BentPipeCAD(self.diameter, 0, cst.WALLS).cad
            bent_pipe_in = su.rotate([90, 0, 0])(bent_pipe_in)
            bent_pipe_in = su.right(self._length / 2 - cst.WALLS)(bent_pipe_in)
            bent_pipe_in = su.up(self.in_io.height - cst.WALLS)(bent_pipe_in)

            # Build the vertical tube
            v_tube = s.cylinder(r=self.diameter / 2, h=l_v_tube)
            v_tube = su.right(self._length / 2)(v_tube)
            v_tube = su.up(self.out_io.height + cst.WALLS - cst.F)(v_tube)

            # Build the drill tube mark
            drill_m = s.cylinder(r=1.5, h=l_drill_m)
            drill_m = su.right(self._length / 2)(drill_m)
            drill_m = su.up(self.in_io.height - l_drill_m/2 + 1)(drill_m)

            # Bent pipe for output
            bent_pipe_out = BentPipeCAD(self.diameter, 0, cst.WALLS).cad
            bent_pipe_out = su.rotate([-90, 0, 0])(bent_pipe_out)
            bent_pipe_out = su.rotate([0, 0, 180])(bent_pipe_out)
            bent_pipe_out = su.right(cst.WALLS + self._length / 2)(bent_pipe_out)
            bent_pipe_out = su.up(cst.WALLS + self.out_io.height)(bent_pipe_out)

            # Translate the horizontal tubes joining the bent pipes and the
            # output/input
            h_pipe_out = su.up(self.out_io.height)(h_pipe_out)

        elif self.out_io.height < self.in_io.height and self.reverse_siphon is True:

            # Build the body, a simple brick
            body = s.cube([self._length, self._width, self.height])
            body = su.back(self._width / 2)(body)
            body = su.up(self.out_io.height - self.diameter / 2 - cst.WALLS)(body)

            # Translate horizontal pipe from input to bent pipe
            h_pipe_in = su.up(self.in_io.height)(h_pipe_in)

            # Bent pipe for input
            bent_pipe_in = BentPipeCAD(self.diameter, 0, cst.WALLS).cad
            bent_pipe_in = su.rotate([90, 0, 0])(bent_pipe_in)
            bent_pipe_in = su.right(self._length / 2 - cst.WALLS)(bent_pipe_in)
            bent_pipe_in = su.up(self.in_io.height - cst.WALLS)(bent_pipe_in)

            # Build the vertical tube
            v_tube = s.cylinder(r=self.diameter / 2, h=l_v_tube)
            v_tube = su.right(self._length / 2)(v_tube)
            v_tube = su.up(self.out_io.height + cst.WALLS - cst.F)(v_tube)

            # Build the drill tube mark
            drill_m = s.cylinder(r=1.5, h=l_drill_m)
            drill_m = su.right(self._length / 2)(drill_m)
            drill_m = su.up(self.in_io.height - l_drill_m/2 + 1)(drill_m)

            # Bent pipe for output
            bent_pipe_out = BentPipeCAD(self.diameter, 0, cst.WALLS).cad
            bent_pipe_out = su.rotate([180, 0, 0])(bent_pipe_out)
            bent_pipe_out = su.rotate([0, 0, 90])(bent_pipe_out)
            bent_pipe_out = su.right(cst.WALLS + self._length / 2)(bent_pipe_out)
            bent_pipe_out = su.up(cst.WALLS + self.out_io.height)(bent_pipe_out)

            # Translate the horizontal tubes joining the bent pipes and the
            # output/input
            h_pipe_out = su.up(self.out_io.height)(h_pipe_out)


        total = body - bent_pipe_in - v_tube - bent_pipe_out - h_pipe_in - h_pipe_out

        if self.drill_mark is True:
            total = total - drill_m


        # # Uncomment to debug pipes
        # total = bent_pipe_in + v_tube + bent_pipe_out + h_pipe_in + h_pipe_out

        # Rotate the siphon, and translate it
        total = su.rotate([0, 0, self.coo["angle"]])(total)
        total = su.translate([self.coo["x"], self.coo["y"], 0])(total)
        total = s.color(su.Red)(total)

        return total


if __name__ == "__main__":

    from .reactor import ReactorCAD as rea
    from .floating_filter_reactor import FloatingFilterReactorCAD as ff_rea
    from .filter_reactor import FilterReactorCAD as f_rea

    # r1 = rea(20, rea.T_OPEN, rea.B_ROUND_IN_O)
    # r1.addInputPercentage('test')
    # r2 = rea(20, rea.T_OPEN, rea.B_ROUND_IN_O)
    # r2.addInputPercentage('test')

    # r1.type_bottom = ff_rea.B_ROUND_IN_O

    # c = SiphonCAD(r1, r1.outputs['default'], r2, r2.inputs['test'])
    # c = SiphonCAD(r1, r1.inputs['test'], r2, r2.outputs['default'])

    # su.scad_render_to_file(r1.cad + r2.cad + c.cad, "test.scad")
    # su.scad_render_to_file(c.cad, "test.scad")
    # r_a = rea(100, rea.T_OPEN, rea.B_FLAT_IN_O, 30)
    # r_b = ff_rea(20, 20, rea.T_OPEN, rea.B_FLAT_IN_O, 20, 3)
    # r_b = f_rea(50, rea.T_OPEN, rea.B_FLAT_IN_O, 20, 3)

    r_a = rea(20, rea.T_OPEN, rea.B_FLAT_IN_O)
    r_b = rea(20, rea.T_OPEN, rea.B_FLAT_IN_O)

    # Create 2 inputs with different diameters
    r_a.addInputPercentage("test", height_per=20)
    r_b.addInputPercentage("test")

    c = SiphonCAD(r_a, r_a.inputs["test"], r_b, r_b.inputs["test"])

    c.length = 20

    print(c.height)
    print(r_b.coo["x"])

    # r_b.addInputPercentage('test', angle=-30)
    # r_b.addInputPercentageTop('test', angle=-30)
    # r_b.fn = 50

    # print(r_b)

    # c = SiphonCAD(r_a, r_a.outputs['default'], r_b, r_b.inputs['test'])

    # print(r_a.coo)
    su.scad_render_to_file(r_a.cad + r_b.cad + c.cad, "test.scad")
    # su.scad_render_to_file(r1.cad + r2.cad + c.cad, "test.scad", file_header='$fn = 25;')
    # su.scad_render_to_file(c.cad, "test.scad", file_header='$fn = 25;')
    # su.scad_render_to_file(c.cad, "test.scad")
