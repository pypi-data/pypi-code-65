#!/usr/bin/python
# coding: utf-8

import solid as s
import solid.utils as su
from typing import Union, Dict
import warnings

from . import constants as cst
from .exceptions import *
from .reactor import ReactorCAD
from .pipe import BentPipeCAD
from .in_out import InputOutput
from .connector import ConnectorCAD


class DoubleSiphonCAD(ConnectorCAD):
    def __init__(
        self,
        obj_in: ReactorCAD,
        in_io: InputOutput,
        obj_out: ReactorCAD,
        out_io: InputOutput,
        height_like: Union[str, float] = "1st",
        drill_mark: bool = False,
        offsets_type: str = "minimal",
    ) -> None:

        """
        DoubleSiphon object. Based on Siphon object. Will connect in_io port of
        obj_in to out_io port of obj_out. drill_mark will add a small mark where to drill to place 
        to inser a plug.

        Arguments:
            obj_in (ReactorCAD): Reactor input object
            in_io (InputOutput): I/O used as input for the connector
            obj_out (ReactorCAD): Reactor output object
            out_io (InputOutput): I/O used as output for the connector
            height_like (Union[str, float]): defines what height the siphon should be
                                             '1st': height of the input object,
                                             '2nd': height of the output object,
                                             float: custom height (default: ("1st"))
            drill_mark {bool} -- [description]
            offsets_type (str): defines how the siphon connects to the object
                                'minimal': minimal offset, the siphon barely touches the
                                objects,
                                'optimal': not implemented yet.
                                Defaults to "minimal"

        Returns:
            None
        """

        # Name/module type, used by GUI to connect slot and signals
        self.module_type = "Siphon connector"
        self.module_type_short = "DS"

        # Check input and output can be connected
        self.checkConnectivity(in_io, out_io)

        self.drill_mark = drill_mark

        # In this connector, assign the connected objects early
        self.obj_in = obj_in
        self.obj_out = obj_out

        # in_io and out_io are properties; sanity checks performed here
        self.in_io = in_io
        self.out_io = out_io

        # Calculate height of siphon before checking I/O # connected objects need
        # to be assigned
        # Property, see setter
        self.height_like = height_like
        self._height = self._findMinHeight()

        # If checkConnectivity didn't crash, diameters are the same, # just take one
        self.diameter = self.in_io.diameter

        # Find length and width for the siphon
        self._width = self._findMinWidth()

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

    @property
    def height_like(self) -> Union[float, str]:

        """
        Get the type of height: height like input object, or like output object,
        or custom value

        Returns:
            Union[float, str]: "1st", or "2nd" or discrete value in mm
        """

        return self._height_like

    @height_like.setter
    def height_like(self, height_like: Union[str, float]):

        """
        Set the type of height:
        height like input object, or like output object:
        - '1st': height like input object
        - '2nd': height like output object
        - value: value in mm

        Arguments:
            height_like (Union[str, float]): '1st': height of the input object,
                                             '2nd': height of the output object,
                                             float: custom height
        """

        # Get a number for height w/ height_like parameter
        if height_like == "1st":
            self._height = self.obj_in.infos["height_wo_inlet"]
        elif height_like == "2nd":
            self._height = self.obj_out.infos["height_wo_inlet"]
        else:
            self._height = height_like

        # Check input and output are valid, after assigning objects and finding #
        # the height
        self._checkInputOutput(self.in_io, self.out_io)

        self._height_like = height_like

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
            float: minimum length fof connector
        """

        return 4 * cst.WALLS + self.diameter + self.offset_in + self.offset_out

    def _findMinWidth(self) -> float:

        """
        Find the minimum width of connector based on design constraints,
        i.e thickness of walls, diameter, etc

        Returns:
            float: minimum width for connector
        """

        return self.diameter + 2 * cst.WALLS

    def _findMinHeight(self) -> float:

        """
        Find the minimum height of connector based on design constraints,
        i.e thickness of walls, diameter, etc

        Returns:
            float: minimum height for connector
        """

        # Get a number for height w/ height_like parameter
        if self._height_like == "1st":
            h = self.obj_in.infos["height_wo_inlet"]
        elif self._height_like == "2nd":
            h = self.obj_out.infos["height_wo_inlet"]
        else:
            h = self._height_like

        return h

    def _checkInputOutput(self, in_io: InputOutput, out_io: InputOutput):

        """
        Make sure the output is not too close to the top

        Arguments:
            in_io (InputOutput): input I/O for the connector
            out_io (InputOutput): output I/O for the connector
        """

        needed_space = 3 * cst.WALLS + cst.D_CAN / 2
        max_h_out = self._height - needed_space

        # If output is too close to the top, change strategy to custom and
        # set height to proper value
        if out_io.height > max_h_out:
            mes = "Output too close to the top of double siphon."
            mes += " Changing height_like to custom"
            warnings.warn(mes)
            self.height_like = out_io.height + needed_space

    def _buildCadCode(self) -> s.objects.translate:

        """
        Build the CAD code w SolidPython

        Returns:
            s.objects.translate: the connector's cad object
        """

        # Build the body, a simple brick
        body = s.cube([self._length, self._width, self._height])
        body = su.back(self._width / 2)(body)

        # Calculate length of horizontal tubes joining the bent pipes to the
        # outside
        # TODO: check this number
        # TODO: offsets probably don't need to be accounted for
        l_h_tube1 = self.diameter / 2 + self.offset_in + 2 * cst.F
        l_h_tube2 = self.diameter / 2 + self.offset_out + 2 * cst.F

        # calculate length of the joint pipe between the two 90° bent pipes
        l_h_pipe_u_turn = self._length - 4 * cst.WALLS - self.diameter + 2 * cst.F

        # First vertical tube of the siphon
        # First calculate its length
        l_v_tube1 = (
            self._height
            - self.diameter / 2
            - 3 * cst.WALLS
            - self.in_io.height
            + 2 * cst.F
        )

        # Second vertical tube of the siphon
        # calculate its length
        l_v_tube2 = (
            self._height
            - self.diameter / 2
            - 3 * cst.WALLS
            - self.out_io.height
            + 2 * cst.F
        )

        # Vertial tube of the drill mark, calculate its length
        l_drill_m = (self.height - l_v_tube1 + cst.WALLS) / 2

        # Horizontal pipe joining the bent pipe and the input
        h_pipe_in = s.cylinder(r=self.diameter / 2, h=l_h_tube1)
        h_pipe_in = su.rotate([0, -90, 0])(h_pipe_in)
        h_pipe_in = su.right(l_h_tube1 - cst.F)(h_pipe_in)
        h_pipe_in = su.up(self.in_io.height)(h_pipe_in)

        # Bent pipe for input
        bent_pipe_in = BentPipeCAD(self.diameter, 0, cst.WALLS).cad
        bent_pipe_in = su.rotate([-90, 0, 0])(bent_pipe_in)
        bent_pipe_in = su.right(l_h_tube1 - 2 * cst.F)(bent_pipe_in)
        bent_pipe_in = su.up(cst.WALLS + self.in_io.height)(bent_pipe_in)

        # Build the vertical tube
        v_tube1 = s.cylinder(r=self.diameter / 2, h=l_v_tube1)
        v_tube1 = su.right(l_h_tube1 + cst.WALLS - 2 * cst.F)(v_tube1)
        v_tube1 = su.up(cst.WALLS + self.in_io.height - cst.F)(v_tube1)

        # Build the drill tube mark
        drill_m = s.cylinder(r=1.5, h=l_drill_m)
        drill_m = su.right(l_h_tube1 + cst.WALLS - 2 * cst.F)(drill_m)
        drill_m = su.up(self._height - l_drill_m + 1)(drill_m)

        # Bent pipe for first part of U turn
        bent_pipe_u_turn1 = BentPipeCAD(self.diameter, 0, cst.WALLS).cad
        bent_pipe_u_turn1 = su.rotate([0, 0, 90])(bent_pipe_u_turn1)
        bent_pipe_u_turn1 = su.rotate([90, 0, 0])(bent_pipe_u_turn1)
        bent_pipe_u_turn1 = su.right(l_h_tube1 + 2 * cst.WALLS - 2 * cst.F)(
            bent_pipe_u_turn1
        )
        bent_pipe_u_turn1 = su.up(self._height - self.diameter / 2 - 2 * cst.WALLS)(
            bent_pipe_u_turn1
        )

        # Build the joint pipe between the two 90° bent pipes
        h_pipe_u_turn = s.cylinder(r=self.diameter / 2, h=l_h_pipe_u_turn)
        h_pipe_u_turn = su.rotate([0, -90, 0])(h_pipe_u_turn)
        h_pipe_u_turn = su.right(
            l_h_tube1 + 2 * cst.WALLS + l_h_pipe_u_turn - 3 * cst.F
        )(h_pipe_u_turn)
        h_pipe_u_turn = su.up(self._height - self.diameter / 2 - cst.WALLS)(
            h_pipe_u_turn
        )

        # Bent pipe for second part of U turn
        bent_pipe_u_turn2 = BentPipeCAD(self.diameter, 0, cst.WALLS).cad
        bent_pipe_u_turn2 = su.rotate([90, 0, 0])(bent_pipe_u_turn2)
        bent_pipe_u_turn2 = su.right(
            l_h_tube1 + 2 * cst.WALLS + l_h_pipe_u_turn - 4 * cst.F
        )(bent_pipe_u_turn2)
        bent_pipe_u_turn2 = su.up(self._height - self.diameter / 2 - 2 * cst.WALLS)(
            bent_pipe_u_turn2
        )

        # Build the vertical tube
        v_tube2 = s.cylinder(r=self.diameter / 2, h=l_v_tube2)
        v_tube2 = su.right(
            l_h_tube1 + 2 * cst.WALLS + l_h_pipe_u_turn + cst.WALLS - 4 * cst.F
        )(v_tube2)
        v_tube2 = su.up(self.out_io.height + cst.WALLS - cst.F)(v_tube2)

        # Bent pipe for output
        bent_pipe_out = BentPipeCAD(self.diameter, 0, cst.WALLS).cad
        bent_pipe_out = su.rotate([-90, 0, 0])(bent_pipe_out)
        bent_pipe_out = su.rotate([0, 0, 180])(bent_pipe_out)
        bent_pipe_out = su.right(
            l_h_tube1 + 2 * cst.WALLS + l_h_pipe_u_turn + 2 * cst.WALLS - 4 * cst.F
        )(bent_pipe_out)
        bent_pipe_out = su.up(cst.WALLS + self.out_io.height)(bent_pipe_out)

        # Horizontal pipe joining the bent pipe and the output
        h_pipe_out = s.cylinder(r=self.diameter / 2, h=l_h_tube2)
        h_pipe_out = su.rotate([0, -90, 0])(h_pipe_out)
        h_pipe_out = su.right(
            l_h_tube1
            + 2 * cst.WALLS
            + l_h_pipe_u_turn
            + 2 * cst.WALLS
            + l_h_tube2
            - 5 * cst.F
        )(h_pipe_out)
        h_pipe_out = su.up(self.out_io.height)(h_pipe_out)

        total = (
            body
            - bent_pipe_in
            - v_tube1
            - h_pipe_in
            - bent_pipe_u_turn1
            - h_pipe_u_turn
            - bent_pipe_u_turn2
            - v_tube2
            - bent_pipe_out
            - h_pipe_out
        )

        if self.drill_mark is True:
            total = total - drill_m

        # # Uncomment when debugging pipes
        # total = bent_pipe_in + v_tube1 + h_pipe_in + bent_pipe_u_turn1 + \
        # h_pipe_u_turn + bent_pipe_u_turn2 + v_tube2 + bent_pipe_out + h_pipe_out

        # Rotate the siphon, and translate it
        total = su.rotate([0, 0, self.coo["angle"]])(total)
        total = su.translate([self.coo["x"], self.coo["y"], 0])(total)
        total = s.color(su.Red)(total)

        return total


if __name__ == "__main__":

    from .reactor import ReactorCAD as rea
    from .filter_reactor import FilterReactorCAD as f_rea

    # r_a = ReactorCAD(40, ReactorCAD.T_OPEN, ReactorCAD.B_FLAT_IN_O)
    # r_b = ReactorCAD(20, ReactorCAD.T_OPEN, ReactorCAD.B_FLAT_IN_O)

    # r_a.addInputPercentage('test')
    # r_b.addInputPercentage('test', height_per=20)

    # c = DoubleSiphonCAD(r_a, r_a.inputs['test'], r_b, r_b.outputs['default'])
    # c = DoubleSiphonCAD(r_a, r_a.outputs['default'], r_b, r_b.inputs['test'])
    # c = DoubleSiphonCAD(r_a, r_a.outputs['default'], r_b, r_b.inputs['test'], height_like='2nd')
    # print(c)

    # r_b.inputs['test'].height = 30
    # c.length = 30

    # c.refresh()

    # su.scad_render_to_file(c.cad, 'test2.scad')
    # su.scad_render_to_file(r_a.cad + r_b.cad + c.cad, 'test2.scad', file_header='$fn = 50;')
    # su.scad_render_to_file(c.cad, 'test2.scad', file_header='$fn = 10;')
    # su.scad_render_to_file(c.cad, 'test2.scad')
    r_1 = rea(20, rea.T_OPEN, rea.B_ROUND_IN_O)
    # r_1.addLuerTopInlet('i1')
    # r_1.addCustomTopInlet('i2', diameter=8)
    # r_1.addInputPercentage("entry", 100, external=True)

    r_2 = rea(20, rea.T_OPEN, rea.B_ROUND_EX_O)
    r_2.addInputPercentage("def")

    # First connector, from 1st to 2nd module
    con1 = DoubleSiphonCAD(
        r_1, r_1.outputs["default"], r_2, r_2.inputs["def"], height_like=10
    )

    su.scad_render_to_file(r_1.cad + r_2.cad + con1.cad, "test2.scad")
    # su.scad_render_to_file(r_1.cad + r_2.cad + con1.cad, 'test2.scad', file_header='$fn = 25;')
    # su.scad_render_to_file(con1.cad, 'test2.scad', file_header='$fn = 25;')

    # import trimesh

    # mesh = trimesh.load('test2.stl')
    # trimesh.repair.broken_faces(mesh, color=[255,0,0,255])
    # print(mesh.is_watertight)
    # mesh.show()
    pass
