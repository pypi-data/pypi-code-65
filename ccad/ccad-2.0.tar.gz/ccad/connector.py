#!/usr/bin/python
# coding: utf-8

import numpy as np
import warnings
from typing import Dict, Union

from . import misc
from .object import ObjectCAD
from .reactor import ReactorCAD
from .exceptions import *
from .in_out import InputOutput


class ConnectorCAD(ObjectCAD):

    """Base class for connectors"""

    coo: Dict[str, float]
    obj_in: ReactorCAD
    obj_out: ReactorCAD
    _length: float
    _in_io: InputOutput
    _out_io: InputOutput
    _old_in_io: InputOutput
    _old_out_io: InputOutput
    _drill_mark: bool
    _reverse_siphon: bool
    _offset_in: float
    _offset_out: float

    @property
    def infos(self) -> Dict[str, Union[str, float]]:

        """
        Return infos for the connector

        Returns:
            dict -- [description]
        """

        infos = {}

        # External radius (including wall)
        infos["length"] = self.length
        infos["width"] = self.width
        infos["height"] = self.height
        infos["drill_mark"] = self.drill_mark
        infos["reverse_siphon"] = self.reverse_siphon

        return infos

    @property
    def width(self) -> float:

        """
        Return width of connector

        Returns:
            float
        """

        #return self._findMinWidth()
        return self._width

    @width.setter
    def width(self, value: float) -> None:

        """
        Set the width of the connector

        Arguments:
            value {float} -- desired width for connector

        Returns:
            None
        """

        # Find min length
        min_w = self._findMinWidth()

        # If for whatever reason the width set by the user becomes smaller
        # during the refresh process, set it to min_w
        if self._width < min_w:
            self._width = min_w

        # Make sure the connector is of minimum width
        if value < min_w:
            warnings.warn(f"Value set by user too small, using min_w {min_w}")
            self._width = min_w

        # If user chooses radius bigger than diameter of reactor, we use default min
        elif value > 1.2 * self.obj_in.infos["r_ex"] or value > 1.2 * self.obj_out.infos["r_ex"]:
            smallest_radius = min(self.obj_in.infos["r_ex"], self.obj_out.infos["r_ex"])
            warnings.warn(f"Value set by user too big, using max_w {smallest_radius*1.2}")
            self._width = smallest_radius*1.2
        else:
            self._width = value

    @property
    def height(self) -> float:

        """
        Return height of connector

        Returns:
            float
        """

        return self._findMinHeight()

    @property
    def length(self) -> float:

        """
        Get the length of the connector, relates to distance between
        two objects

        Returns:
            float
        """

        return self._length

    @length.setter
    def length(self, value: float) -> None:

        """
        Set the length of the connector, relates to distance between
        two objects

        Arguments:
            value {float} -- desired length for connector

        Returns:
            None
        """

        # Find min length
        min_l = self._findMinLength()

        # If for whatever reason the length set by the user becomes smaller
        # during the refresh process, set it to min_l
        if self._length < min_l:
            self._length = min_l

        # Make sure the connector is of minimum length
        if value < min_l:
            warnings.warn(f"Value set by user too small, using min_l {min_l}")

        self._length = value

        # Recalculate transformations values and apply them
        self._calXYAngleTransformationsValues()
        self._applyXYTransformations()

    @property
    def drill_mark(self) -> bool:

        """
        Returns the value of the drill_mark toggle menu option

        Returns:
            bool
        """

        # We need to catch this exception because old ccad projects
        # did not have drill marks
        try:
            return self._drill_mark 
        except AttributeError:
            return False

    @drill_mark.setter
    def drill_mark(self, value: bool) -> None:

        """
        Sets the option to create a drill mark on top of the
        siphon case

        Arguments:
            value {bool} -- value of the toggle option

        Returns:
            None
        """
        self._drill_mark = value

    @property
    def reverse_siphon(self) -> bool:

        """
        Returns the value of the reverse_siphon toggle menu option

        Returns:
            bool
        """

        # We need to catch this exception because old ccad projects
        # did not have reverse siphon option
        try:
            return self._reverse_siphon 
        except AttributeError:
            return False

    @reverse_siphon.setter
    def reverse_siphon(self, value: bool) -> None:

        """
        Sets the option to create a reverse siphon on top of the
        siphon case

        Arguments:
            value {bool} -- value of the toggle option

        Returns:
            None
        """
        self._reverse_siphon = value

    @property
    def offset_in(self) -> float:

        """
        Retun the offset between the connector and the input object

        Returns:
            float
        """

        return self._offset_in

    @offset_in.setter
    def offset_in(self, type_offset: str) -> None:

        """
        Set the offset between connector and input object
        defines how the connector connects to the object:
        - minimal: minimal offset, the connector barely touches the objects
        - optimal: try to minimize connector's length: it's embedded in the
                   objects walls

        NOTE: optimal is not implemented yet

        Arguments:
            type_offset {str} -- desired type of offset

        Raises:
            NotImplementedError -- when type is set to optimal
            ValueError -- when offset type is not recognize

        Returns:
            None
        """

        if type_offset == "minimal":
            radius_obj_in: float = self.obj_in.infos["r_ex"]
            self._offset_in = radius_obj_in - np.sqrt(
                radius_obj_in ** 2 - (self._width / 2) ** 2
            )
            self.offset_in_type = type_offset

        elif type_offset == "optimal":
            # TODO: Recalculate length of connector after changing offset
            raise NotImplementedError("Optimal offset not implemented yet")

        else:
            raise ValueError("Wrong type of offset")

    @property
    def offset_out(self) -> float:

        """
        Return the offset between the connector and the output object

        Returns:
            float -- [description]
        """

        return self._offset_out

    @offset_out.setter
    def offset_out(self, type_offset: str) -> None:

        """
        Set the offset between connector and output object
        defines how the connector connects to the object:
        - minimal: minimal offset, the connector barely touches the objects
        - optimal: try to minimize connector's length: it's embedded in the
                   objects walls

        NOTE: optimal is not implemented yet

        Arguments:
            type_offset {str} -- desired type of offset

        Raises:
            NotImplementedError -- when offset type is set to optimal
            ValueError -- when offset type is not recognized

        Returns:
            None
        """

        if type_offset == "minimal":
            radius_obj_out: float = self.obj_out.infos["r_ex"]
            self._offset_out = radius_obj_out - np.sqrt(
                radius_obj_out ** 2 - (self._width / 2) ** 2
            )
            self.offset_out_type = type_offset

        elif type_offset == "optimal":
            # TODO: Recalculate length of connector after changing offset
            raise NotImplementedError("Optimal offset not implemented yet")

        else:
            raise ValueError("Wrong type of input")

    @property
    def in_io(self) -> InputOutput:

        """
        Return input InputOutput object

        Returns:
            InputOutput
        """

        # Do some magic here: compare the internal attribute _in_io to
        # the I/O of the inputs object. Return the match. This way calling
        # self.in_io return an up to date I/O, not the static/internal
        # variable _in_io.
        for io in self.obj_in.outputs.values():
            if self._in_io is io:
                return io

    @in_io.setter
    def in_io(self, in_io: InputOutput) -> None:

        """
        Check if new in_io can be connected. If so, assign it, connect it,
        and disconnect old in_io. 
        If in_io is None, it means we are deleting it.

        Arguments:
            in_io {InputOutput} -- the new input

        Raises:
            ImpossibleConnection -- when new io is already connected
            ImpossibleConnection -- when new io is external

        Returns:
            None
        """

        # if it is None it means we are removing. disconnect and return
        if in_io is  None:
            # We are removing it. First save it in case user will undo
            self._old_in_io = self._in_io
            # Then disconnect it
            self._in_io.connected = False
            self._in_io = None
            return

        # Exit if re-assigning same I/O (avoids crash in GUI)
        try:
            if in_io is self._in_io:
                return
        except AttributeError:
            pass

        if in_io.connected:
            raise ImpossibleConnection("New in_io already connected")

        if in_io.external:
            raise ImpossibleConnection("New in_io is external")

        try:
            # Disconnect old in_io
            self._in_io.connected = False
        except AttributeError:
            pass

        if in_io is not None:
            # Assign new in_io and connect it
            self._in_io = in_io
            self._in_io.connected = True
            self._in_io.connectedTo = self

    @property
    def out_io(self) -> InputOutput:

        """
        Return output InputOutput object

        Returns:
            InputOutput
        """

        # Do some magic here: compare the internal attribute _out_io to
        # the I/O of the output object. Return the match. This way calling
        # self.out_io return an up to date I/O, not the static/internal
        # variable _out_io.
        for io in self.obj_out.inputs.values():
            if self._out_io is io:
                return io

    @out_io.setter
    def out_io(self, out_io: InputOutput) -> None:

        """
        Check if new out_io can be connected. If so, assign it, connect it,
        and disconnect old out_io

        Arguments:
            out_io {InputOutput} -- the new output

        Raises:
            ImpossibleConnection -- when new io is already connected
            ImpossibleConnection -- when new io is external

        Returns:
            None
        """

        # if it is None it means we are removing. disconnect and return
        if out_io is None:
            # We are removing it. First save it in case user will undo
            self._old_out_io = self._out_io
            # Disconnect it
            self._out_io.connected = False
            self._out_io = None
            return

        # Exit if re-assigning same I/O (avoids crash in GUI)
        try:
            if out_io is self._out_io:
                return
        except AttributeError:
            pass

        if out_io.connected:
            raise ImpossibleConnection("New out_io already connected")

        if out_io.external:
            raise ImpossibleConnection("New out_io is external")

        try:
            # Disconnect old out_io
            self._out_io.connected = False
        except AttributeError:
            pass

        if out_io is not None:
            # Assign new out_io and connect it
            self._out_io = out_io
            self._out_io.connected = True
            self._out_io.connectedTo = self

    def _findMinLength(self) -> float:

        """
        To be subclassed

        Raises:
            NotImplementedError: when called directly from this class
        """

        raise NotImplementedError

    def _findMinWidth(self) -> float:

        """
        To be subclassed

        Raises:
            NotImplementedError: when called directly from this class
        """

        raise NotImplementedError

    def _findMinHeight(self) -> float:

        """
        To be subclassed

        Raises:
            NotImplementedError: when called directly from this class
        """

        raise NotImplementedError

    def isConnected(self) -> bool:

        """
        Check if the object is connected. Since it's a connector, simply
        return True

        Returns:
            bool -- always return True
        """

        return True

    def checkConnectivity(self, in_io: InputOutput, out_io: InputOutput) -> None:

        """
        Check if input and output can be connected. Check if I/Os are of type
        'internal' and have the same diameter

        Arguments:
            in_io {InputOutput} -- input for connector
            out_io {InputOutput} -- output for connector

        Raises:
            ImpossibleConnection -- when input is external
            ImpossibleConnection -- when output is external
            IncompatibilityError -- when diameter for input and output are different

        Returns:
            None
        """

        if in_io.external:
            raise ImpossibleConnection("Input I/O is external, can't connect")

        if out_io.external:
            raise ImpossibleConnection("Ouput I/O is external, can't connect")

        # Check input and output have same diameter
        if in_io.diameter != out_io.diameter:
            raise IncompatibilityError("Diam of input and output not equal")

    def _checkInputOutput(self, in_io: InputOutput, out_io: InputOutput):

        """
        To be subclassed

        Raises:
            NotImplementedError: when called directly from this class
        """

        raise NotImplementedError


    def refresh(self) -> None:

        """
        Refresh method. Will check the I/O, re-do the calculations and will
        apply them

        Returns:
            None
        """

        # Check input and output are valid
        self._checkInputOutput(self.in_io, self.out_io)

        # Find min length, width and height for the connector
        # Don't assign min length&width returned by _findDimensions 
        # to _length and width, otherwiser refresh would wipe the user 
        # setting for length of the connector
        self._height = self._findMinHeight()

        # Recalculate offsets
        self.offset_in = self.offset_in_type
        self.offset_out = self.offset_out_type

        min_l = self._findMinLength()

        # If for whatever reason the length set by the user becomes smaller
        # during the refresh process, set it to min_l
        if self._length < min_l:
            self._length = min_l

        min_w = self._findMinWidth()

        # If for whatever reason the width set by the user becomes smaller
        # during the refresh process, set it to min_w
        if self._width < min_w:
            self._width = min_w

        # Find where the connector should be translated to
        self._calXYAngleTransformationsValues()

        # Apply transformations on connector once calculated
        self._applyXYTransformations()
        self._applyAngleTransformations()

    def _calXYAngleTransformationsValues(self) -> None:

        """
        Calculate (x, y) coordinates of the connector and its angle.
        Calculate (x, y) coordinates for output object

        Returns:
            None
        """

        # TODO: check type of object ?

        # Get the rotation angle for the connector
        self.coo["angle"] = self.in_io.angle

        # Get radius of input object
        radius_obj_in = self.obj_in.infos["r_ex"]

        # Calculate (x, y) for input of input object
        x = self.obj_in.coo["x"] + np.cos(np.deg2rad(self.coo["angle"])) * radius_obj_in
        y = self.obj_in.coo["y"] + np.sin(np.deg2rad(self.coo["angle"])) * radius_obj_in

        # Calculate (x, y) position for connector
        self.coo["x"] = x - np.cos(np.deg2rad(self.coo["angle"])) * self._offset_in
        self.coo["y"] = y - np.sin(np.deg2rad(self.coo["angle"])) * self._offset_in

        # Radius of the second object being connected
        radius_obj_out = self.obj_out.infos["r_ex"]

        # Calculate (x, y) position for output object
        self._x_obj_out = self.coo["x"] + np.cos(np.deg2rad(self.coo["angle"])) * (
            self._length + radius_obj_out - self._offset_out
        )

        self._y_obj_out = self.coo["y"] + np.sin(np.deg2rad(self.coo["angle"])) * (
            self._length + radius_obj_out - self.offset_out
        )

    def _applyXYTransformations(self) -> None:

        """
        Apply transformations (rotations, translations) on the output object

        Returns:
            None
        """

        # Add translation offset to the second object. The object will render
        # its CAD code accordingly
        self.obj_out.coo["x"] = self._x_obj_out
        self.obj_out.coo["y"] = self._y_obj_out

    def _applyAngleTransformations(self) -> None:

        """
        Apply transformations (rotations, translations) on the output object

        Returns:
            None
        """

        # Calculate rotation angle for output object
        diff_angle = misc.simplifyAngle(self.in_io.angle - self.out_io.angle + 180)

        self.obj_out.coo["angle"] = diff_angle

        # Update the angle of each InputOutput for obj_out
        for out_io in self.obj_out.outputs.values():
            out_io.angle += diff_angle
            out_io.angle = misc.simplifyAngle(out_io.angle)
        for in_io in self.obj_out.inputs.values():
            in_io.angle += diff_angle
            in_io.angle = misc.simplifyAngle(in_io.angle)


if __name__ == "__main__":
    pass
