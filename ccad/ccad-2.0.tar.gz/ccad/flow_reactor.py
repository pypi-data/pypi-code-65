# #!/usr/bin/python
# coding: utf-8

import solid as s
import solid.utils as su
import numpy as np
from typing import Tuple, Optional, Dict, Union, List
import warnings, math

from . import constants as cst
from . import misc
from .exceptions import *
from .object import ObjectCAD
from .pipe import BentPipeCAD
from .in_out import InputOutput


class FlowReactorCAD(ObjectCAD):

    def __init__(
        self,
        npipes: int,
        ninputs: int,
        width: float,
        radius: float,
        spacing: float,
        def_out_angle: float = 0,
        volume: float = 1,
        length: float = 1,
        *args,
        **kwargs,
    ) -> None:

        """
        Args:
            npipes (int): number of horizontal pipes, not counting in and out
            width (float): width of the horizontal pipes
            radius (float): radius of the pipe
            spacing (float): space in mm between the horizontal pipes
            def_out_angle (float): angle for the default output. Anti-clockwise
            volume (float): Volume of the internal pipes. Not used yet
            length (float): Length of the internal pipes. Not used yet
            *args:
            **kwargs: named arguments

        Returns:
            None
        """

        # Name/module type, used by GUI to connect slot and signals
        self.module_type = "Flow reactor"
        self.module_type_short = "FW"

        # read above, just assign all these variables
        self._npipes = npipes
        self._ninputs = ninputs
        self._width = width
        self._radius = radius
        self._spacing = spacing
        self._length = length

        # Check input volume is valid
        self._checkVolume(volume)

        # Don't use the volume property, instead assign internal attribute
        # Do that to explicitely declare _h and _r in init
        self._volume = volume * 1000

        self.inputs: Dict[str, InputOutput] = dict()
        self.outputs: Dict[str, InputOutput] = dict()

        # Angle for the output, starting from x axis, clockwise
        self._def_out_angle = misc.simplifyAngle(def_out_angle)

        # Coordinates of the reactor. Will be modified by connectors
        self.coo: Dict[str, float] = {"x": 0, "y": 0, "z": 0, "angle": 0}

        # Find reactor's dimensions
        self._h, self._w, self._l = self._findHeightWidthLength()

        # self._buildDefOutput()

    @property
    def def_out_angle(self) -> float:

        """
        Property for default output angle

        Returns:
            float: angle of default output (at the bottom of the reactor)
        """

        return self._def_out_angle

    @def_out_angle.setter
    def def_out_angle(self, value: float) -> None:

        """
        Set the angle of default output (at the bottom of the reactor)
        The angle will be simplified.

        Args:
            value (float): new value of default output angle. Angle, in degree

        Returns:
            None
        """

        simple_value = misc.simplifyAngle(value)
        self._def_out_angle = simple_value
        self.outputs["default"].angle = simple_value

    @property
    def infos(self) -> Dict[str, Union[float, str]]:

        """
        Return infos for the reactor, as a dict.

        Returns:
            Dict[str, Union[float,str]]
        """

        return self._getInfos()

    def _getInfos(self) -> Dict[str, Union[float, str]]:

        """
        Return infos for the reactor. This is a separate method so sub-classes
        can use it in their 'infos' property without trouble.
        See infos property

        Returns:
            Dict[str, Union[float,str]]
        """

        infos: Dict[str, Union[float, str]] = dict()

        infos["npipes"] = self._npipes
        infos["ninputs"] = self._ninputs
        infos["width"] = self._width
        infos["volume"] = self.volume
        infos["radius"] = self._radius
        infos["spacing"] = self.spacing
        infos["volume"] = self.volume
        infos["length"] = self._length

        # Add number of I/Os
        infos["inputs"] = len(self.inputs)
        infos["outputs"] = len(self.outputs)

        # External width or max rad (including wall)
        # at the moment we use width, later on I will calculate proper size
        infos["r_ex"] = self.width


        return infos

    def describe(self) -> str:

        """
        Describe the reactor and its I/Os with text

        Returns:
            str: the text description of the reactor and its infos
        """

        description = ""

        # Print all values in infos dict
        for key, value in self._getInfos().items():
            description += f"{key}: {value}"
            description += "\n"

        description += "----- Input(s) -----"
        description += "\n"

        if self.inputs:
            for name, io in self.inputs.items():
                description += f"{name}: {io.infos}"
                description += "\n"
        else:
            description += "No input"

        description += "----- Output(s) ----"
        description += "\n"

        if self.outputs:
            for name, io in self.outputs.items():
                description += f"{name}: {io.infos}"

                # if last io in the dict, don't add new line
                if io is not list(self.outputs.values())[-1]:
                    description += "\n"
        else:
            description += "No output"

        return description

    def _checkVolume(self, value: float) -> None:

        """
        Check that volume of the reactor is valid

        Args:
            value (float): new value for reactor's volume, to be tested

        Returns:
            None

        Raises:
            ValueError: if value is <= 0
        """

        if value <= 0:
            raise ValueError("Volume must be > 0")

    @property
    def volume(self) -> float:

        """
        Return volume in mL, not mm3

        Returns:
            float
        """

        return self._volume / 1000

    @volume.setter
    def volume(self, value: float) -> None:

        """
        Check validity of value, must be positive.
        Trigger calculation of _h and _r

        Args:
            value (float): new value for volume (mL)

        Returns:
            None
        """

        # Will crash if incorrect value
        self._checkVolume(value)
        self._volume = value * 1000

    @property
    def npipes(self) -> int:

        """
        Returns:
            int: number of horizontal pipes
        """

        return self._npipes

    @npipes.setter
    def npipes(self, value: int) -> None:

        """
        Sets the number of horizontal pipes

        Args:
            npipes (int): new number of horizontal pipes

        Returns:
            None
        """

        self._npipes = value

    @property
    def ninputs(self) -> int:

        """
        Returns:
            int: number of inputs
        """

        return self._ninputs

    @ninputs.setter
    def ninputs(self, value: int) -> None:

        """
        Sets the number of inputs

        Args:
            ninputs (int): sets the number of inputs, 1,2 or 3

        Returns:
            None
        """

        if value not in [1,2,3]:
            raise ValueError("Number of inputs must be 1,2 or 3")

        self._ninputs = value

    @property
    def width(self) -> float:

        """
        [summary]

        Returns:
            float: width of the horizontal pipes
        """

        return self._width

    @width.setter
    def width(self, value: float) -> None:

        """
        Changes the width of the horizontal pipes

        Args:
            value (float): new width value

        Returns:
            None
        """

        # Assing new width
        self._width = value


    @property
    def radius(self) -> float:

        """
        Get the radius of the pipes

        Returns:
            float: radius of pipes
        """

        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:

        """
        Set the radius of the pipes

        Args:
            value (float): width of pipes (mm)

        Returns:
            None
        """

        self._radius = value

    @property
    def spacing(self) -> float:

        """
        Return the spacing between pipes

        Returns:
            float: spacing between pipes (mm)
        """

        return self._spacing

    @spacing.setter
    def spacing(self, value: float) -> None:

        """Set the spacing between pipes"""

        self._spacing = value

    @property
    def length(self) -> float:

        """
        Return the total length of the pipes, from in to out

        Returns:
            float: total length of pipes (mm)
        """

        return self._length

    @length.setter
    def length(self, value: float) -> None:

        """
        Set the total length of the pipes. At the moment this does nothing
        In future based on this length it will re-calculate specs of whole
        reactor

        Args:
            value (float): new value for length of reactor

        Returns:
            None

        """

        self._length = value

    def isConnected(self) -> bool:

        """
        Test if the reactor is connected.
        Check if there is at least one I/O with the 'connected' attribute set to True

        Returns:
            bool: True if reactor is connected, False otherwise
        """

        # For each io of cad_obj, check if io.connected is True
        ios = [
            io.connected
            for io in list(self.inputs.values()) + list(self.outputs.values())
        ]

        if True in ios:
            return True
        else:
            return False

    def hasConnectedInternalInput(self) -> bool:

        """
        Check if the reactor has a connected internal input. Mainly used by Assembly
        to check if the reactor is the first in the assembly.

        Returns:
            bool: True if reactor has a connected internal input, False otherwise
        """

        if not self.inputs:
            return False

        for io in self.inputs.values():
            if not io.external and io.connected:
                return True

        return False

    def hasInternalConnectedOutput(self) -> bool:

        """
        Check if the reactor has an internal, connected output. Mainly used by
        Assembly to check if the reactor is the first in the assembly.

        Returns:
            bool: True if reactor has a connected, internal output. False otherwise
        """

        if not self.outputs:
            return False

        for io in self.outputs.values():
            if not io.external and io.connected:
                return True

        return False

    def _addInput(
        self,
        name: str,
        height: float,
        diameter: float,
        angle: float = 180,
        external: bool = False,
    ) -> None:

        """
        Add an input to the reactor. The user should never call it directly. The user
        can only add I/O through percentage height. Functions like expandVertically
        will always assume an I/O was added trhough percentage, and will always try
        to move the I/O to the right percentage.

        No sanity checks performed here.

        Args:
            name (str): name of the I/O
            height (float): height (mm)
            diameter (float): diameter of I/O (mm)
            angle (float): angle of I/O (degree)
            external (bool): True for external I/O, False for internal

        Returns:
            None
        """

        # Try to update the IO object if it exists, or
        # Create an InputObject and put it in the dic of inputs
        try:
            self.inputs[name].height = height
            self.inputs[name].diameter = diameter
            self.inputs[name].angle = angle
            self.inputs[name].external = external
        except KeyError:
            self.inputs[name] = InputOutput(height, diameter, angle, external)

    def addInputPercentage(
        self,
        name: str,
        height_per: float = 100,
        angle: float = 180,
        diameter: Optional[float] = None,
        external: bool = False,
    ) -> None:

        """
        Add an input to the reactor, through a percentage of the available height.
        Should be the only way to add an input.
        See also getHeightPercentage

        Args:
            name (str): name of the I/O
            height_per (float): percentage height for I/O. Default to 100
            angle (float): angle for the I/O Default to 180
            diameter (Optional[float]): diameter (mm) of the I/O. If None, will
                                        default to a certain value, depending on
                                        'external' state
            external (bool): if True, I/O is external (can't be connected). If False,
                             I/O is internal and can be connected

        Returns:
            None

        Raises:
            ValueError: when percentage height < 0% or > 100%
        """

        simple_angle = misc.simplifyAngle(angle)

        # Crash if invalid value for input's height
        if height_per < 0 or height_per > 100:
            raise ValueError(f"Height % must be >=0 and <=100. Received: {height_per}")


        # Pass the converted parameters to _addInput
        # Create an InputObject and put it in the dic of inputs
        self._addInput(name, height_per, diameter, simple_angle, external)

    def _addOutput(
        self,
        name: str,
        height: float,
        diameter: float,
        angle: float = 180,
        external: bool = False,
    ) -> None:

        """
        Add an output to the reactor. The user should never call it directly. The user
        can only add I/O through percentage height. Functions like expandVertically
        will always assume an I/O was added trhough percentage, and will always try
        to move the I/O to the right percentage.

        No sanity checks performed here.

        Args:
            name (str): name of the I/O
            height (float): height (mm)
            diameter (float): diameter of I/O (mm)
            angle (float): angle of I/O (degree)
            external (bool): True for external I/O, False for internal

        Returns:
            None

        Raises:
            ValueError: when I/O's name is 'default' (reserved name)
        """

        # User can't create an output called default
        if name == "default":
            mes = "Name 'default' for output is reserved, choose another name"
            raise ValueError(mes)

        # Try to update the IO object if it exists, or
        # Create an OutputObject and put it in the dic of inputs
        try:
            self.outputs[name].height = height
            self.outputs[name].diameter = diameter
            self.outputs[name].angle = angle
            self.outputs[name].external = external
        except KeyError:
            self.outputs[name] = InputOutput(height, diameter, angle, external)

    def addOutputPercentage(
        self,
        name: str,
        height_per: float = 100,
        angle: float = 180,
        diameter: Optional[float] = None,
        external: bool = False,
    ) -> None:

        """
        Add an output to the reactor, through a percentage of the available height.
        Should be the only way to add an output.
        See also getHeightPercentage

        Args:
            name (str): name of the I/O
            height_per (float): percentage height for I/O. Default to 100
            angle (float): angle for the I/O Default to 180
            diameter (Optional[float]): diameter (mm) of the I/O. If None, will
                                        default to a certain value, depending on
                                        'external' state
            external (bool): if True, I/O is external (can't be connected). If False,
                             I/O is internal and can be connected

        Returns:
            None

        Raises:
            ValueError: when percentage height < 0% or > 100%
        """

        simple_angle = misc.simplifyAngle(angle)

        # Crash if invalid value for input's height
        if height_per < 0 or height_per > 100:
            raise ValueError("Height % must be >=0 and <=100")

        # Pass the converted parameters to _addInput
        # Create an InputObject and put it in the dic of inputs
        self._addOutput(name, real_h, diameter_nbr, simple_angle, external)


    def _buildInputOutputHole(self, entry: InputOutput) -> s.objects.rotate:

        """
        Build an input or output from an InputOutput object.
        Basically create a cylinder and apply transformations to perforate the
        reactor at the right place

        Args:
            entry (InputOutput): I/O for which the hole must be built

        Returns:
            s.objects.rotate: cad object for entry's hole
        """

        # Create the cylinder and apply transformations
        hole = s.cylinder(r=entry.diameter / 2, h=2 * self._r)
        hole = su.rotate([0, 90, 0])(hole)
        hole = su.translate([0, 0, entry.height])(hole)
        hole = su.rotate([0, 0, entry.angle])(hole)

        return hole

    def _buildDefOutput(self) -> None:

        """
        Build the default output InputOutput object.

        Returns:
            None
        """  

        # Try to update the IO object if it exists, or
        # Create an InputObject and put it in the dic of outputs
        try:
            self.outputs["default"].height = 0
            self.outputs["default"].diameter = self._radius
            self.outputs["default"].angle = self._def_out_angle
            self.outputs["default"].external = True
        except KeyError:
            self.outputs["default"] = InputOutput(
                0, self._radius, self._def_out_angle, True
            )

    def _findHeightWidthLength(self) -> Tuple[float, float, float]:

        """
        Find the width, lengh and the height of the reactor

        Returns:
            Tuple[float, float, float]: height, width, length
        """

        # height is equal to diameter of pipe plus 3x the walls
        height = self._radius * 2 + cst.WALLS * 3
        # inout pipes have 3 mm radius, so we need to compare to it
        inouth = 6 + cst.WALLS * 2
        height = min(height, inouth)

        # width is the width of the horizontal pipes plus curved pipes
        # plus the walls 3x
        # to calculate the width, first we need to see if _width is shorter
        # that the distance between the 3 inlets (distpipes=20)
        maxwidth = max(self._width, 20)
        width = maxwidth + cst.WALLS * 4
        arcradius = self._spacing/2 + self._radius
        # adding both ends
        width += arcradius * 2
        # The inlets can also impact the max width if the device
        # has a low width
        winlets = 10 # the horizontal pipe to split inlets has h=10
        winlets +=  self._spacing # bit of curved pipe, both ends
        winlets += 6 # 6mm diameter inlet, 3mm both ends equals 6
        winlets += cst.WALLS * 2
        if self._ninputs in [2,3]:
            width = max(width, winlets)

        # length is calculated with the spacing plus npipes 
        length = (self._npipes+1)*self._spacing
        length += 10*2 # in and out outlets are fixed to 10
        length += self.spacing # the last half arcs connecting to in/out
        length += self.spacing # last bit of pipe besides outlet
        length += self.spacing*2 # last bit of pipe besides inlet

        return height, width, length

    def _buildBody(self) -> s.objects.difference:

        """
        Build the body of the reactor

        Returns:
            s.objects.difference: the cad object for the body
        """     

        # Find reactor's dimensions
        self._h, self._w, self._l = self._findHeightWidthLength()

        case = s.cube([self._l, self._w, self._h], center=True)
        case = su.right(self._l/2)(case) # position at x=0
        case = su.left(self._spacing*3+self._spacing/2+10)(case)
        piping = self._buildPiping()

        return case - piping


    def _buildInlets(self, ninlets) -> s.objects.union:
        """
        Build the inlets for the reactor. They have a diameter of 6 mm

        Args:
            ninlets (int): Number of inlets. 1,2 or 3.

        Returns:
            s.objects.difference: the cad object for the inlets
        """
        iot = self._spacing/2

        if ninlets == 1 or ninlets == 3:
            # last pipe connecting to 6mm outlet
            inlet = s.cylinder(r=self._radius, h=self._spacing*1.5, center=True)
            inlet = su.rotate([90,0,90])(inlet)
            inlet = su.left(self._spacing*2+iot*1.5)(inlet)
            # 6mm diameter connector where they will put the plastic tube
            connector = s.cylinder(r=3, h=10)
            connector = su.rotate([90,0,-90])(connector)
            connector = su.left(self._spacing*3+iot)(connector)
            inlet += connector

        if ninlets == 2 or ninlets == 3:
            # horizontal pipe to create 2 new inlets
            distpipes = 20 # distance between pipes 1 and 3
            hpipe = s.cylinder(r=self._radius, h=distpipes, center=True)
            hpipe = su.rotate([90,0,0])(hpipe)
            hpipe = su.left(2*self._spacing)(hpipe)
            # if we are coming from 2 inlets, we need to create it
            # because it never went through the first if
            if ninlets == 2:
                inlet = hpipe
            else: # we are coming from 3 inlets, then inlet already exists
                inlet += hpipe

            # curved pipes to go from horizontal to vertical 
            cpipe1 = s.rotate_extrude(convexity=10, angle=-90)(
                su.right(iot)(s.circle(r=self._radius))    
            )
            cpipe1 = su.left(2*self._spacing+iot)(cpipe1)
            cpipe1 = su.back(distpipes/2)(cpipe1)
            cpipe2 = s.rotate_extrude(convexity=10, angle=90)(
                su.right(iot)(s.circle(r=self._radius))    
            )
            cpipe2 = su.left(2*self._spacing+iot)(cpipe2)
            cpipe2 = su.forward(distpipes/2)(cpipe2)
            inlet += cpipe1 + cpipe2

            # last 2 vertical pipes with radius user-defined
            vpipe = s.cylinder(r=self._radius, h=self._spacing)
            vpipe = su.rotate([90,0,-90])(vpipe)
            vpipe = su.left(self._spacing*2+iot)(vpipe)
            vpipe1 = su.forward(distpipes/2+iot)(vpipe)
            vpipe2 = su.back(distpipes/2+iot)(vpipe)
            inlet += vpipe1 + vpipe2

            # last 2 6mm diameter inlets
            vpipe = s.cylinder(r=3, h=10)
            vpipe = su.rotate([90,0,-90])(vpipe)
            vpipe = su.left(self._spacing*3+iot)(vpipe)
            vpipe1 = su.forward(distpipes/2+iot)(vpipe)
            vpipe2 = su.back(distpipes/2+iot)(vpipe)
            inlet += vpipe1 + vpipe2

        return inlet


    def _buildPiping(self) -> s.objects.union:

        """
        Build the internal piping of the reactor

        Returns:
            s.objects.difference: the cad object for the body
        """

        # IN piping
        halfpipe = self._width/2 - self._spacing/2
        # first the last horizontal bit before curve
        body = s.cylinder(r=self._radius, h=halfpipe, center=True)
        body = su.rotate([90,0,0])(body)
        body = su.left(self._spacing)(body)
        body = su.back(self._width/4+self._spacing/4)(body)
        # now curved pipe to conect with perpendicular pipe
        pipe = s.rotate_extrude(convexity=10, angle=90)(
                su.right(self._spacing/2)(s.circle(r=self._radius))    
        )
        pipe = su.left(self._spacing+self._spacing/2)(pipe)
        pipe = su.back(self._spacing/2)(pipe)
        body += pipe
        # last the perpendicular pipe going out
        pipe = s.cylinder(r=self._radius, h=self._spacing/2, center=True)
        pipe = su.rotate([90,0,90])(pipe)
        pipe = su.left(self._spacing+self._spacing/2+self._spacing/4)(pipe)
        body += pipe

        # main horizontal pipes
        for i in range(0, int(self._npipes)):
            pipe = s.cylinder(r=self._radius, h=self._width, center=True)
            pipe = su.right(i*self._spacing)(
                su.rotate([90,0,0])(pipe)
            )
            body += pipe

        # left hand curved pipes connecting big horizontal pipes
        if (self._npipes%2==0):
            lfcp = math.ceil(self._npipes/2)+1
        else:
            lfcp = math.ceil(self._npipes/2)
        for i in range(lfcp):
            pipe = s.rotate_extrude(convexity=10, angle=-180)(
                su.right(self._spacing/2)(s.circle(r=self._radius))    
            )
            pipe = su.right(-self._spacing/2+i*self._spacing*2)(pipe)
            pipe = su.back(self._width/2)(pipe)
            body += pipe

        # right hand curved pipes connecting big horizontal pipes
        rhcp = math.ceil(self._npipes/2)
        for i in range(rhcp):
            pipe = s.rotate_extrude(convexity=10, angle=180)(
                su.right(self._spacing/2)(s.circle(r=self._radius))    
            )
            pipe = su.right(self._spacing/2+i*self._spacing*2)(pipe)
            pipe = su.forward(self._width/2)(pipe)
            body += pipe

        # OUT pipe, see IN pipe, this is very similar, just other side
        if (self._npipes%2==1):
            pipe = s.cylinder(r=self._radius, h=halfpipe, center=True)
            pipe = su.rotate([90,0,0])(pipe)
            pipe = su.right(self._spacing*self._npipes)(pipe)
            pipe = su.forward(self._width/4+self._spacing/4)(pipe)
            body += pipe
            pipe = s.rotate_extrude(convexity=10, angle=-90)(
                su.right(self._spacing/2)(s.circle(r=self._radius))    
            )
            pipe = su.rotate([0,180,0])(pipe)
            pipe = su.right(self._spacing*self._npipes+self._spacing/2)(pipe)
            pipe = su.forward(self._spacing/2)(pipe)
            body += pipe
        else:
            pipe = s.cylinder(r=self._radius, h=halfpipe, center=True)
            pipe = su.rotate([90,0,0])(pipe)
            pipe = su.right(self._spacing*self._npipes)(pipe)
            pipe = su.back(self._width/4+self._spacing/4)(pipe)
            body += pipe
            pipe = s.rotate_extrude(convexity=10, angle=90)(
                su.right(self._spacing/2)(s.circle(r=self._radius))    
            )
            pipe = su.rotate([0,180,0])(pipe)
            pipe = su.right(self._spacing*self._npipes+self._spacing/2)(pipe)
            pipe = su.back(self._spacing/2)(pipe)
            body += pipe

        # last pipe before outlet
        pipe = s.cylinder(r=self._radius, h=self._spacing, center=True)
        pipe = su.rotate([90,0,90])(pipe)
        pipe = su.right(self._spacing*self._npipes+self._spacing)(pipe)
        body += pipe
        # outlet with 6mm diameter
        pipe = s.cylinder(r=3, h=10, center=True)
        pipe = su.rotate([90,0,90])(pipe)
        # displace last thick pipe to the edge of the other pipes
        pipe = su.right(self._spacing*self._npipes+self._spacing*1.5)(pipe)
        # displace last thick pipe half its body so it concatenates
        pipe = su.right(10/2)(pipe)
        body += pipe

        inlets = self._buildInlets(self._ninputs)

        return body + inlets


    def _buildCadCode(self) -> s.objects.translate:

        """
        Build the CAD code w/ SolidPython.
        Call methods to generate the body and assemble them.

        Returns:
            s.objects.translate: the cad object for the entire reactor
        """

        body = self._buildBody()

        # Assemble  body. No need for cst.F, already done in
        # _buildBody. this is from reactor, perhaps in the future
        # flow reactor will have more parts
        total = body

        # Simplify rotation angle for reactor, and use it to rotate reactor
        simple_angle = misc.simplifyAngle(self.coo["angle"])
        self.coo["angle"] = simple_angle

        total = su.rotate([0, 0, simple_angle])(total)

        # Build the inputs
        for entry in self.inputs.values():
            new_in = self._buildInputOutputHole(entry)
            total -= new_in

        # Build the outputs, except the default one if bottom has pipe
        for key, entry in self.outputs.items():
            if key == "default":
                continue
            new_out = self._buildInputOutputHole(entry)
            total -= new_out

        # Move the entire reactor, inputs included
        total = su.right(self.coo["x"])(total)
        total = su.forward(self.coo["y"])(total)

        return total
