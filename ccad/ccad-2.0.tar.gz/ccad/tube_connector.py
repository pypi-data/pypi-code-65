#!/usr/bin/python
# coding: utf-8

import solid as s
import solid.utils as su
from typing import Dict

from . import constants as cst
from .exceptions import *
from .reactor import ReactorCAD
from .connector import ConnectorCAD
from .in_out import InputOutput


class TubeConnectorCAD(ConnectorCAD):
    def __init__(
        self,
        obj_in: ReactorCAD,
        in_io: InputOutput,
        obj_out: ReactorCAD,
        out_io: InputOutput,
        conflicts: str = "move_out_io",
        offsets_type: str = "minimal",
        drill_mark: bool = False,
    ) -> None:

        """
        Linear tubular connector object. Will connect in_io port of obj_in
        to out_io port of obj_out. This connector might apply z translations
        on obj_in or modify the output object.

        drill_mark will add a small mark where to drill to place 
        to inser a plug.

        'conflicts' defines how the connector will handle height conflicts,
        if input and output are not at the same height:
        - lift_in_obj: will lift input object to align input and output
        - lift_out_obj: will lift output object to align input and output
        - move_out_io: will move the input of the output object to align
          input and output

        Offsets_type defines how the connector connects to the object:
        - minimal: minimal offset, the tube barely touches the objects
        - optimal: try to minimize tube's length: it's embedded in the
                   objects walls

        NOTE: optimal is not implemented yet

        Arguments:
            ConnectorCAD {[type]} -- [description]
            obj_in {ReactorCAD} -- [description]
            in_io {InputOutput} -- [description]
            obj_out {ReactorCAD} -- [description]
            out_io {InputOutput} -- [description]
            drill_mark {bool} -- [description]

        Keyword Arguments:
            conflicts {str} -- [description] (default: {"move_out_io"})
            offsets_type {str} -- [description] (default: {"minimal"})

        Returns:
            None
        """

        # Name/module type, used by GUI to connect slot and signals
        self.module_type = "Tube connector"
        self.module_type_short = "TC"

        # Check input and output are valid
        self.checkConnectivity(in_io, out_io)

        self.drill_mark = drill_mark

        # in_io and out_io are properties; santity checks performed here
        self.in_io = in_io
        self.out_io = out_io

        self.obj_in = obj_in
        self.obj_out = obj_out

        # If _checkInputOutput didn't crash, diameters are the same,
        # just take one
        self.diameter = self.in_io.diameter

        self.conflicts = conflicts

        # Find and width for connector
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

        # Find where the connector should be translated to
        self._calXYAngleTransformationsValues()
        self._calZTransformationValues()

        # Apply transformations once calculated
        self._applyXYTransformations()
        self._applyAngleTransformations()
        self._applyZTransformations()

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

    def _findMinWidth(self) -> float:

        """
        Find the minimum width of connector based on design constraints,
        i.e thickness of walls, diameter, etc

        Returns:
            float -- [description]
        """

        # Width of tube (equals height because it's a tube)
        return self.diameter + 2 * cst.WALLS

    def _findMinHeight(self) -> float:

        """
        Find the minimum height of connector based on design constraints,
        i.e thickness of walls, diameter, etc

        Because it's a tube, return width

        Returns:
            float -- [description]
        """

        return self._findMinWidth()

    def _findMinLength(self) -> float:

        """
        Find the minimum length of connector based on design constraints,
        i.e thickness of walls, diameter, etc

        Returns:
            float -- [description]
        """

        return self.offset_in + self.offset_out

    def _checkInputOutput(self, in_io: InputOutput, out_io: InputOutput) -> None:

        """
        Does nothing for tube connector. Implement because ConnectorCAD base
        class calls this method during refresh. Other connectors implement
        several sanity checks here

        Arguments:
            in_io {InputOutput} -- [description]
            out_io {InputOutput} -- [description]

        Returns:
            None
        """

        return

    def _checkConflictsValue(self, conflicts: str) -> None:

        """
        Check user provided a valid value for conflicts

        Arguments:
            conflicts {str} -- [description]

        Raises:
            ValueError -- [description]

        Returns:
            None
        """

        possible_values = ["lift_in_obj", "lift_out_obj", "move_out_io"]

        if conflicts not in possible_values:
            raise ValueError("invalid value for conflicts")

    def _calZTransformationValues(self) -> None:

        """
        Find out what kind of Z calculations the connector should perform,
        and calculate the transformations

        Returns:
            None
        """

        self._checkConflictsValue(self.conflicts)

        # Find out what kind of z translation to apply: on input object or
        # output object input
        if self.conflicts == "lift_in_obj":
            self._z_obj_in = abs(self.in_io.height - self.out_io.height)
        elif self.conflicts == "lift_out_obj":
            self._z_obj_out = abs(self.in_io.height - self.out_io.height)
        elif self.conflicts == "move_out_io":
            self._dout_io = self.in_io.height - self.out_io.height

    def _applyZTransformations(self) -> None:

        """
        Apply the Z transformations (lift objects)

        Returns:
            None
        """

        self._checkConflictsValue(self.conflicts)

        if self.conflicts == "lift_in_obj":
            self.obj_in.liftReactor(self._z_obj_in)
        elif self.conflicts == "lift_out_obj":
            self.obj_out.liftReactor(self._z_obj_out)
        elif self.conflicts == "move_out_io":
            # TODO: check if it's possible to move the output
            self.out_io.height = self.in_io.height

    def refresh(self) -> None:

        """
        Refresh method. Will check the I/O, re-do the calculations and
        will apply them. Same stuff as base class, but also re-do Z
        calculations/translations

        Returns:
            None
        """

        super().refresh()

        self._calZTransformationValues()
        self._applyZTransformations()

    def _buildCadCode(self) -> s.objects.translate:

        """
        Build the CAD code w/ SolidPython

        Returns:
            s.objects.translate -- [description]
        """

        # Build outer cylinder
        outer = s.cylinder(r=self.diameter / 2 + cst.WALLS, h=self._length + 2 * cst.F)
        outer = su.down(cst.F)(outer)

        # Build inner cylinder
        inner = s.cylinder(r=self.diameter / 2, h=self._length + 4 * cst.F)
        inner = su.down(2 * cst.F)(inner)

        # Assemble tube
        total = outer - inner

        # Rotate the tube, and translate it
        total = su.rotate([0, 90, 0])(total)
        total = su.rotate([0, 0, self.coo["angle"]])(total)
        total = su.translate([self.coo["x"], self.coo["y"], self.out_io.height])(total)
        total = s.color(su.Red)(total)

        return total


if __name__ == "__main__":

    # from reactor import ReactorCAD

    r_a = ReactorCAD(20, ReactorCAD.T_OPEN, ReactorCAD.B_FLAT_IN_O)
    r_b = ReactorCAD(20, ReactorCAD.T_OPEN, ReactorCAD.B_FLAT_IN_O)

    # Create 2 inputs with different diameters
    r_a.addInputPercentage("test", 100)
    r_b.addInputPercentage("test", 50)

    c = TubeConnectorCAD(
        r_a, r_a.outputs["default"], r_b, r_b.inputs["test"], conflicts="lift_in_obj"
    )
    # c = TubeConnectorCAD(r_a, r_a.inputs['test'], r_b, r_b.inputs['test'], conflicts='lift_in_obj')

    # TODO: changing length makes it stop working
    c.length = 10

    # su.scad_render_to_file(c.cad, 'test.scad')
    su.scad_render_to_file(c.cad + r_a.cad + r_b.cad, "test.scad")

    # r_b.addInputPercentage('test')

    # c = SiphonCAD(r_a, r_a.outputs['default'], r_b, r_b.inputs['test'])

    # su.scad_render_to_file(c.cad, "test.scad")

    # import trimesh

    # mesh = trimesh.load('test.stl')
    # print(mesh.is_watertight)
    # trimesh.repair.broken_faces(mesh, color=[255,0,0,255])
    # mesh.show(smooth=False)
    pass
