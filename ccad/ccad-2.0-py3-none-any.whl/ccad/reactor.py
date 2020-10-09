# #!/usr/bin/python
# coding: utf-8

import solid as s
import solid.utils as su
import numpy as np
from typing import Tuple, Optional, Dict, Union, List
import warnings

from . import constants as cst
from . import misc
from .exceptions import *
from .object import ObjectCAD
from .pipe import BentPipeCAD
from .in_out import InputOutput
from .top_in import TopInlet
from .tops_placement import get_positions

# TODO: add more logging
# TODO: tests


class ReactorCAD(ObjectCAD):

    """Base class for reactors. Will be inherited by specialized reactors"""

    # Top types
    T_OPEN = "Open"
    T_2_QUA_INCH = "Threaded cap 1/2 inch"
    T_3_QUA_INCH = "Threaded cap 3/4 inch"
    T_4_QUA_INCH = "Threaded cap 1 inch"
    T_CLOSED_ROUND = "Closed round"
    T_CLOSED_ROUND_O = "Closed round with outlet"
    T_CUSTOM = "Closed round with custom outlet(s)"

    # Bottom types
    B_ROUND = "Round"
    B_ROUND_EX_O = "Round with external outlet"
    B_ROUND_IN_O = "Round with internal outlet"
    B_FLAT = "Flat"
    B_FLAT_EX_O = "Flat with external outlet"
    B_FLAT_IN_O = "Flat with internal outlet"

    # List of all possible bottoms
    BOTTOMS = [B_ROUND, B_ROUND_EX_O, B_ROUND_IN_O, B_FLAT, B_FLAT_EX_O, B_FLAT_IN_O]

    # List bottoms with pipe
    BOTTOMS_PIPE = [B_ROUND_EX_O, B_ROUND_IN_O, B_FLAT_EX_O, B_FLAT_IN_O]

    # All possible tops
    TOPS = [
        T_OPEN,
        T_2_QUA_INCH,
        T_3_QUA_INCH,
        T_4_QUA_INCH,
        T_CLOSED_ROUND,
        T_CLOSED_ROUND_O,
        T_CUSTOM,
    ]

    # Make lists to group similar types of tops/bottoms
    ROUND_BOTS = BOTTOMS[:3]
    FLAT_BOTS = BOTTOMS[3:]
    OPEN_TOPS = TOPS[:4]
    CLOSED_TOPS = TOPS[4:]
    THREADED_TOPS = TOPS[1:4]

    # How to align the top
    ALIGN_TOP_STRATEGIES = ["Expand body", "Lift reactor"]

    def __init__(
        self,
        volume: float,
        type_top: str,
        type_bottom: str,
        def_out_angle: float = 0,
        *args,
        **kwargs,
    ) -> None:

        """
        Args:
            volume (float): volume of the reactor, in mL. Will be converted to mm3
            type_top (str): type of top (round, round w outle, open, etc)
            type_bottom (str): type of bottom (round, round w internal outlet, etc)
            def_out_angle (float): angle for the default output (at the bottom).
                                   Anti-clockwise
            *args:
            **kwargs: named arguments

        Returns:
            None
        """

        # Name/module type, used by GUI to connect slot and signals
        self.module_type = "Reactor"
        self.module_type_short = "R"

        # Bool to check if r is constrained
        self.r_constrained = False

        # Bool to check if top is aligned
        self.top_aligned = False

        # Types for top and bottom
        self._type_top = type_top
        self._type_bottom = type_bottom

        # Handle threaded tops (r is constrained)
        self._handleThreadedTops()

        # Check input volume is valid
        self._checkVolume(volume)

        # Don't use the volume property, instead assign internal attribute
        # Do that to explicitely declare _h and _r in init
        self._volume = volume * 1000

        # Find reactor's dimensions
        self._h, self._r = self._findHeightRadius()

        # Handle extra args passed to init
        self._handleExtraArgs(kwargs)

        self.inputs: Dict[str, InputOutput] = dict()
        self.outputs: Dict[str, InputOutput] = dict()
        self.top_inlets: Dict[str, TopInlet] = dict()

        # Angle for the output, starting from x axis, clockwise
        self._def_out_angle = misc.simplifyAngle(def_out_angle)

        # Coordinates of the reactor. Will be modified by connectors
        self.coo: Dict[str, float] = {"x": 0, "y": 0, "z": 0, "angle": 0}

        self._buildDefOutput()

    def _handleExtraArgs(self, kwargs: dict) -> None:

        """
        Handles named extra arguments passed to the init function
        For now, works for:

        align_top_strategy (str): how to align the top of the reactor:
            - "expand": will expand the body to match target height
            - "lift": will lift the reactor to match target height

        walls (float): thickness of the walls. Default to cst.WALLS (should be 3 mm)
        d_can (float): diameter of internal pipes. Default to cst.D_CAN (should be 3 mm)
        r (float): internal radius of the reactor. If set, radius is constrained and
                   won't be calculated automatically

        Args:
            kwargs (dict):

        Returns:
            None
        """

        # Strategy to align the top of the cartridge
        # possible values for align_top_strategy:
        # - expand (will expand the body of the reactor)
        # - lift (will lift the reactor)
        self.align_top_strategy: str
        if "align_top_strategy" in kwargs:
            self.align_top_strategy = kwargs["align_top_strategy"]
        else:
            self.align_top_strategy = "expand"

        # wall thickness
        self._walls: float
        if "walls" in kwargs:
            self._walls = self._getMinWalls(kwargs["walls"])
        else:
            self._walls = cst.WALLS

        # Diameter for canula
        self._d_can: float
        if "d_can" in kwargs:
            self._d_can = kwargs["d_can"]
        else:
            self._d_can = cst.D_CAN

        # User provided radius, try to build reactor with it
        # Use property here
        if "r" in kwargs:
            self.r = kwargs["r"]

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
        Infos include:
            - r_ex (float): external radius
            - r (float): internal radius
            - height (float): total height for reactor (top inlets included)
            - height_wo_inlet (float): height for reactor (top inlets excluded)
            - height_body (float): height of the body
            - height_bottom (float): height of the bottom
            - inputs (float): number of inputs
            - outputs (float): number of outputs
            - walls (float): thickness of walls (mm)
            - type_top (str): type of top
            - type_bottom (str): type of bottom
            - volume (float): volume of reactor (mL)
            - d_can (float): diameter of internal pipes (mm)
            - align_top_strategy (str): strategy to align top

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

        infos["type_top"] = self.type_top
        infos["type_bottom"] = self.type_bottom
        infos["volume"] = self.volume
        infos["d_can"] = self._d_can
        infos["align_top_strategy"] = self.align_top_strategy
        infos["walls"] = self.walls

        # Add number of I/Os
        infos["inputs"] = len(self.inputs)
        infos["outputs"] = len(self.outputs)

        # External radius (including wall)
        infos["r_ex"] = self.r + self._walls

        # Internal radius
        infos["r"] = self.r

        # Calculate total height
        h_bottom = self._calculateHBottom()[0]

        total_height = (
            self.coo["z"] + h_bottom + self._h + self._calculateHTop(inlet=True)
        )

        infos["height"] = total_height

        # Calculate height without inlet
        height_wo_inlet = (
            self.coo["z"] + h_bottom + self._h + self._calculateHTop(inlet=False)
        )

        infos["height_wo_inlet"] = height_wo_inlet

        # Height of the body
        infos["height_body"] = self._h

        # Height of the bottom
        infos["height_bottom"] = h_bottom

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
        self._h, self._r = self._findHeightRadius()

    @property
    def type_bottom(self) -> str:

        """
        Returns:
            str: type of bottom
        """

        return self._type_bottom

    @type_bottom.setter
    def type_bottom(self, type_bottom: str) -> None:

        """
        Change bottom type, call volume setter to recalculate dimensions
        to match the volume

        Args:
            type_bottom (str): new type of bottom

        Returns:
            None
        """

        # Store h_bottom before change
        h_bottom = self._calculateHBottom()[0]

        self._type_bottom = type_bottom

        # Setting the volume will trigger calculation of dimensions
        self.volume = self._volume / 1000

        # Try to build the default output
        # Will do nothing if the new type of bottom has no pipe
        self._buildDefOutput()

        # Store h_bottom after bottom changed
        new_h_bottom = self._calculateHBottom()[0]

        # Calculate difference between old and current bottom's height
        offset = new_h_bottom - h_bottom

        # Offset all inputs
        for in_io in self.inputs.values():
            in_io.height += offset

        # Offset all outputs except default
        for name, out_io in self.outputs.items():
            if name == "default":
                continue
            out_io.height += offset

    @property
    def type_top(self) -> str:

        """
        [summary]

        Returns:
            str: type of top
        """

        return self._type_top

    @type_top.setter
    def type_top(self, type_top: str) -> None:

        """
        Change top type, call volume setter to recalculate dimensions to
        match the volume

        Args:
            type_top (str): new type of top

        Returns:
            None
        """

        # Save old top type
        old_type_top = self.type_top

        # Assing new top type
        self._type_top = type_top

        self._handleThreadedTops()

        # If switching from threaded tops to non-threaded top, disable
        # constraint on radius
        if (
            old_type_top in self.THREADED_TOPS
            and self._type_top not in self.THREADED_TOPS
        ):
            self.r_constrained = False

        # Setting the volume will trigger calculation of dimensions
        self.volume = self._volume / 1000

    @property
    def walls(self) -> float:

        """
        Get the thickness of the walls

        Returns:
            float: thickness of walls
        """

        return self._walls

    @walls.setter
    def walls(self, value: float) -> None:

        """
        Set the thickness of the walls

        Args:
            value (float): thickness of walls (mm)

        Returns:
            None
        """

        # Get a suitable value for the wall thickness
        self._walls = self._getMinWalls(value)

        # Rebuild default output
        self._buildDefOutput()

    def _getMinWalls(self, value: float) -> float:

        """
        'value' is provided by the user. Check if it is high enough to be
        used as wall thickness, depending on the design of the reactor. If
        it's not, return a suitable value.
        Called each time thickness of walls is about to be set.

        Args:
            value (float): desired value for walls' thickness (mm)

        Returns:
            float: 'value' if 'value' is high enough, or suitable value otherwise
                   (depends on types of top and bottom)
        """

        # minimum value for walls
        min_value: float = -1

        # If external outlet for default output, make sure the bottom wall
        # is high enough to screw the external adaptor and its cap
        if (
            self._type_bottom in [self.B_ROUND_EX_O, self.B_FLAT_EX_O]
            and value < cst.WALL_BOT_MIN
        ):

            # min_value for walls must be WALL_BOT_MIN
            min_value = cst.WALL_BOT_MIN

            warnings.warn(f"Ext outlet, walls must be >= {cst.WALL_BOT_MIN} mm")

        # If threaded tops, walls must be at least WALL_THREAD_MIN
        if self._type_top in self.THREADED_TOPS:

            # If min_value was assigned in previous block, take the max
            # if it wasn't assigned, take the max anyway
            min_value = max([min_value, cst.WALL_THREAD_MIN])

            warnings.warn(f"Threaded top, walls must be >= {cst.WALL_THREAD_MIN} mm")

        if value > min_value:
            walls = value
        else:
            walls = min_value

        return walls

    @property
    def d_can(self) -> float:

        """
        Return the diameter of the internal pipes

        Returns:
            float: diameter of internal pipes (mm)
        """

        return self._d_can

    @d_can.setter
    def d_can(self, value: float) -> None:

        """Set the diameter of the canula (internal pipe used for inlets)"""

        self._d_can = value
        self._buildDefOutput()

    @property
    def r(self) -> float:

        """
        Return the internal radius of the reactor

        Returns:
            float: internal radius for reactor (mm)
        """

        return self._r

    @r.setter
    def r(self, value: float) -> None:

        """
        Set the internal radius of the reactor.
        Radius will be constrained. Constraining radius is not possible with
        threaded tops

        Args:
            value (float): new value for internal radius of the reactor

        Returns:
            None

        Raises:
            ImpossibleAction: if trying to set r with threaded tops
            ValueError: if value <= 0
        """

        # User can't set r if top is threaded (threaded tops already have
        # constrained r)
        if self._type_top in self.THREADED_TOPS:
            raise ImpossibleAction("Threaded top, can't set r")

        self.r_constrained = True

        # Crash if r is negative or null
        if value <= 0:
            raise ValueError("r must be > 0")

        self._r = value
        self._h, self._r = self._findHeightRadius()

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

    def _handleThreadedTops(self) -> None:

        """
        Constrain r to known dimensions if threaded top, switch r_constrained to True
        Called during init and when changing type of top

        Returns:
            None
        """

        # Exit if top is not threaded top
        if self._type_top not in self.THREADED_TOPS:
            return

        # r is constrained
        self.r_constrained = True

        # Set r properly from constants
        if self._type_top == self.T_2_QUA_INCH:
            self._r = cst.R_2_QUA_INCH
        elif self._type_top == self.T_3_QUA_INCH:
            self._r = cst.R_3_QUA_INCH
        elif self._type_top == self.T_4_QUA_INCH:
            self._r = cst.R_4_QUA_INCH

    def _findHeightRadius(self) -> Tuple[float, float]:

        """
        Find the radius and the height (of the straight part of the body) of the
        reactor. h and r are related by golden ratio.

        Will call specialized methods depending on the state of r: constrained
        or unconstrained

        NOTE: volume of pipes is neglected

        Returns:
            Tuple[float, float]: height, radius
        """

        if self.r_constrained:
            h, r = self._calHeightRadiusRConstrained()
        else:
            h, r = self._calHeightRadiusRNotConstrained()

        return h, r

    def _calHeightRadiusRNotConstrained(self) -> Tuple[float, float]:

        """
        Calculate r and h when r is NOT constrained

        Returns:
            Tuple[float, float]: height, radius
        """

        # No top, flat bottom, V= V of body only
        if self._type_bottom in self.FLAT_BOTS and self._type_top == self.T_OPEN:
            r = (self._volume / (2 * np.pi * cst.PHI)) ** (1 / 3)

        # Both top and bottom are round, add volume of sphere
        elif (
            self._type_bottom in self.ROUND_BOTS and self._type_top in self.CLOSED_TOPS
        ):

            r = (3 ** (1 / 3) * self._volume ** (1 / 3)) / (
                2 ** (1 / 3) * (3 * cst.PHI + 2) ** (1 / 3) * np.pi ** (1 / 3)
            )

        # Only top OR bottom is round, add hemisphere to volume
        else:
            r = (3 ** (1 / 3) * self._volume ** (1 / 3)) / (
                2 ** (1 / 3) * (3 * cst.PHI + 1) ** (1 / 3) * np.pi ** (1 / 3)
            )

        h = 2 * r * cst.PHI

        return h, r

    def _calHeightRadiusRConstrained(self) -> Tuple[float, float]:

        """
        Calculate r and h when r IS constrained

        Returns:
            Tuple[float, float]: height, radius

        Raises:
            ConstraintError: when h <= 0 (r is too big)
        """

        # No top, flat bottom, V= V of body only
        if self._type_bottom in self.FLAT_BOTS and self._type_top in self.OPEN_TOPS:
            h = self._volume / (np.pi * self._r ** 2)

        # Both top and bottom are round, add volume of sphere
        elif (
            self._type_bottom in self.ROUND_BOTS and self._type_top in self.CLOSED_TOPS
        ):

            h = (self._volume - 4 / 3 * np.pi * self._r ** 3) / (np.pi * self._r ** 2)

        # Only top OR bottom is round, add hemisphere to volume
        else:
            h = (self._volume - 2 / 3 * np.pi * self._r ** 3) / (np.pi * self._r ** 2)

        if h <= 0:
            raise ConstraintError("Constrained r too big")

        # If ratio too far from golden ratio, raise warning, the reactor
        # probably has inappropriate dimensions
        ratio = h / (2 * self._r)
        if ratio < 1 / 2 * cst.PHI:
            warnings.warn("h of reactor seems too small. Decrease R ?")
        if ratio > 2 * cst.PHI:
            warnings.warn("h of reactor seems too big. Increase R ?")

        return h, self._r

    def _calculateHTop(self, inlet: bool = True) -> float:

        """
        Calculate height of the top. If inlet=True, returns height including inlet.
        If False, doesn't count inlets

        Args:
            inlet (bool): include top inlets or not

        Returns:
            float: height of the top part of the reactor
        """

        # Round closed top
        if self._type_top == self.T_CLOSED_ROUND:

            height_top = self._r + self._walls

        # Round closed top with inlet
        elif self._type_top == self.T_CLOSED_ROUND_O:

            if inlet:
                shortened_l = cst.L_EXT_INLET - self._walls
            else:
                shortened_l = 0

            height_top = self._r + self._walls + shortened_l

        # Threaded tops
        elif self._type_top in self.THREADED_TOPS:
            height_top = cst.H_THREADED_TOP

        # No top, return None
        # Keep this block, explicit is better than implicit
        elif self._type_top == self.T_OPEN:
            height_top = 0

        # Custom inlet(s)
        elif self._type_top in self.T_CUSTOM:

            # Get all the TopInlet objects
            all_inlets = list(self.top_inlets.values())

            if inlet and all_inlets:
                # Get max length among all TopInlet objects
                max_l = max([i.length for i in all_inlets])

                shortened_l = max_l - self._walls
            else:
                shortened_l = 0

            height_top = self._r + self._walls + shortened_l

        return height_top

    def _calculateHBottom(self) -> Tuple[float, float]:

        """
        Calculate height of the bottom, and the vertical offset in case
        there is an external adaptor

        Returns:
            Tuple[float, float]: height of the bottom
        """

        h_bottom: float = 0
        offset_ext_inlet: float = 0

        # Round bottom
        if self._type_bottom == self.B_ROUND:

            # Offset equals to radius of sphere + thickness of walls
            h_bottom = self._r + self._walls

        # Round bottom, internal outlet
        elif self._type_bottom == self.B_ROUND_IN_O:

            h_bottom = self._r + self._d_can + 2 * self._walls

        # Round bottom with external inlet (adaptor)
        elif self._type_bottom == self.B_ROUND_EX_O:

            # Difference between B_ROUND_EX_O and B_ROUND_IN_O is external
            # inlet. Parts have to be offseted vertically.
            # Calculate this offset
            offset_ext_inlet = (cst.D_EXT_INLET - self._d_can) / 2

            h_bottom = self._r + self._d_can + 2 * self._walls + offset_ext_inlet

        # Simple flat bottom
        elif self._type_bottom == self.B_FLAT:

            h_bottom = self._walls

        # Flat bottom w/ internal inlet
        elif self._type_bottom == self.B_FLAT_IN_O:

            h_bottom = self._d_can + 2 * self._walls

        # Flat bottom w/ external inlet
        elif self._type_bottom == self.B_FLAT_EX_O:

            # Difference between B_ROUND_EX_O and B_ROUND_IN_O is external
            # inlet. Parts have to be offseted vertically.
            # Calculate this offset
            offset_ext_inlet = (cst.D_EXT_INLET - self._d_can) / 2

            h_bottom = self._d_can + 2 * self._walls + offset_ext_inlet

        return h_bottom, offset_ext_inlet

    def getHeightPercentage(self, entry: InputOutput) -> float:

        """
        Return the height percentage of an InputOutput.
        entry must belong to this reactor.
        The height percentage is related to the body part of the reactor (EXCLUDING
        top and bottom parts).

        Percentage = 0 -> Very bottom of the body (just above the bottom part)
        Percentage = 100 -> Very top of the body (just below the top)

        Args:
            entry (InputOutput): InputOutput object, calculate its height as
                                 a percentage

        Returns:
            float: percentage height for 'entry'
        """

        h_bottom = self._calculateHBottom()[0]

        # Calculate minimum and maximum heights
        min_h = h_bottom + entry.diameter / 2

        # max height depends on type of reactor
        if self._type_top in self.CLOSED_TOPS:
            max_h = h_bottom + self._h - entry.diameter / 2
        else:
            max_h = h_bottom + self._h - entry.diameter / 2 - self._walls

        height_per = (entry.height - min_h) * 100 / (max_h - min_h)

        return height_per

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

        # Get the height of the bottom
        h_bottom = self._calculateHBottom()[0]

        # Inputed diameter can be a float or None. If None, use defaults.
        # Store value in diameter_nbr
        diameter_nbr: float

        # If diameter is none, set diameter according to external/internal I/O
        if diameter is None and not external:
            diameter_nbr = self._d_can
        elif diameter is None and external:
            diameter_nbr = cst.D_EXT_INLET
        else:
            diameter_nbr = diameter

        # Calculate minimum and maximum heights
        min_h = h_bottom + diameter_nbr / 2

        # max height depends on type of reactor
        if self._type_top in self.CLOSED_TOPS:
            max_h = h_bottom + self._h - diameter_nbr / 2
        else:
            max_h = h_bottom + self._h - diameter_nbr / 2 - self._walls

        # Convert the height from percentage to mm
        real_h = height_per * (max_h - min_h) / 100 + min_h

        # If height is out of range, set it to limit
        # Avoids rounding errors
        if real_h < min_h:
            real_h = min_h
        elif real_h > max_h:
            real_h = max_h

        # Pass the converted parameters to _addInput
        # Create an InputObject and put it in the dic of inputs
        self._addInput(name, real_h, diameter_nbr, simple_angle, external)

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

        # Get the height of the bottom
        h_bottom = self._calculateHBottom()[0]

        # Inputed diameter can be a float or None. If None, use defaults.
        # Store value in diameter_nbr
        diameter_nbr: float

        # If diameter is none, set diameter according to external/internal I/O
        if diameter is None and not external:
            diameter_nbr = self._d_can
        elif diameter is None and external:
            diameter_nbr = cst.D_EXT_INLET
        else:
            diameter_nbr = diameter

        # Calculate minimum and maximum heights
        min_h = h_bottom + diameter_nbr / 2

        # max height depends on type of reactor
        if self._type_top in self.CLOSED_TOPS:
            max_h = h_bottom + self._h - diameter_nbr / 2
        else:
            max_h = h_bottom + self._h - diameter_nbr / 2 - self._walls

        # Convert the height from percentage to mm
        real_h = height_per * (max_h - min_h) / 100 + min_h

        # If height is out of range, set it to limit
        # Avoids rounding errors
        if real_h < min_h:
            real_h = min_h
        elif real_h > max_h:
            real_h = max_h

        # Pass the converted parameters to _addInput
        # Create an InputObject and put it in the dic of inputs
        self._addOutput(name, real_h, diameter_nbr, simple_angle, external)

    def addLuerTopInlet(self, name: str, x: float = 0, y: float = 0) -> None:

        """
        Will create a top inlet, Luer type, so diameter, length and walls are known,
        the user doesn't need to provide them

        Args:
            name (str): name of the inlet
            x (float): position in x, if user wants to manually place the I/O
            y (float): position in y, if user wants to manually place the I/O

        Returns:
            None
        """

        # Get parameters defined in constants
        diameter = cst.D_EXT_INLET
        length = cst.L_EXT_INLET
        walls = cst.WALLS
        type_io = "luer"

        # Call createCustomTopInlet with known parameters
        self.addCustomTopInlet(name, diameter, length, walls, type_io, x, y)

    def addCustomTopInlet(
        self,
        name: str,
        diameter: float,
        length: Optional[float],
        walls: Optional[float],
        type_io: str = "custom",
        x: float = 0,
        y: float = 0,
    ) -> None:

        """
        Will create a top inlet object with custom parameters. Can be also called
        from higher level methods like createLuerTopInlet, with predefined values.

        Args:
            name (str):
            diameter (float): diameter for I/O (mm)
            length (Optional[float]): length of connector (mm).
                                      Default to cst.L_EXT_INLET
            walls (Optional[float]): thickness of walls for I/O (mm).
                                     Default to reactor's wall thickness
            x (float): position in x, if user wants to manually place the I/O
            y (float): position in y, if user wants to manually place the I/O

        Returns:
            None

        Raises:
            IncompatibilityError: when top is not custom
        """

        if self._type_top != self.T_CUSTOM:
            mes = "Can't create top inlet if top is not custom"
            raise IncompatibilityError(mes)

        # If walls is not provided, use reactor's wall thicknes
        if walls is None:
            walls = self._walls

        # If no length is provided, use default length for external adaptors
        if length is None:
            length = cst.L_EXT_INLET

        # Create TopInlet object
        inlet = TopInlet(diameter, length, walls, type_io, x, y)

        # Add the inlet object to dict
        self.top_inlets[name] = inlet

    def autoPlaceTopInlets(self) -> None:

        """
        Method to auto-place the top inlets. These inlets must have been created
        before callin this method

        Returns:
            None
        """

        # Get all the TopInlet objects
        all_inlets = list(self.top_inlets.values())
        positions = get_positions(self._r, all_inlets)

        # Modify position of each inlet w/ positions returned by get_positions
        for inlet, pos in zip(all_inlets, positions):
            inlet.x = pos[0]
            inlet.y = pos[1]

    def liftReactor(self, value: float) -> None:

        """
        Set height for reactor's bottom. This will build a support circle under the
        reactor. Actually does nothing except setting reactor'z to value

        Args:
            value (float): target height for reactor's bottom

        Returns:
            None

        Raises:
            ValueError: if 'value' is negative
        """

        if value < 0:
            raise ValueError("Value for liftReactor() must be > 0")

        # Update the height of each InputOutput for obj_output
        for out_io in self.outputs.values():
            diff = out_io.height - self.coo["z"]
            out_io.height = value + diff
        for in_io in self.inputs.values():
            diff = in_io.height - self.coo["z"]
            in_io.height = value + diff

        self.coo["z"] = value

    def expandVertically(self, value: float) -> None:

        """
        Expand the reactor's body by 'value' (mm). Will modify _h and recalculate the
        volume. This method can be used to align the top of the reactor to another
        reactor top.

        If negative values are used, it will shorten the reactor's body

        Args:
            value (float): increase (or decrease) length of reactor's body by 'value'

        Returns:
            None
        """

        # Get old percentage heights just before expanding
        old_in_per = [self.getHeightPercentage(io) for io in self.inputs.values()]

        old_out_per = [self.getHeightPercentage(io) for io in self.outputs.values()]

        # Backup the state of r_constrained, to be restored later.
        # Allows temporary constraint on radius
        old_state_r_constrained = self.r_constrained

        # Constrain the radius temporarily
        self.r_constrained = True

        # Update volume. Will trigger calculation of _r and _h, but _r
        # is constrained. Volume will be checked during this calculation
        self.volume += (np.pi * self._r ** 2 * value) / 1000

        # Restore state for r_constrained (r is adaptable and not constrained,
        # it will adapt if user changes volume again)
        self.r_constrained = old_state_r_constrained

        # I/Os were created with % of height. Height just changed, so get
        # old percentages and replace input to same percentages of new height
        for old_per, dict_data in zip(old_in_per, self.inputs.items()):
            name, io = dict_data
            self.addInputPercentage(
                name,
                height_per=old_per,
                angle=io.angle,
                diameter=io.diameter,
                external=io.external,
            )

        # I/Os were created with % of height. Height just changed, so get
        # old percentages and replace input to same percentages of new height
        for old_per, dict_data in zip(old_out_per, self.outputs.items()):
            name, io = dict_data

            if name == "default":
                continue

            self.addOutputPercentage(
                name,
                height_per=old_per,
                angle=io.angle,
                diameter=io.diameter,
                external=io.external,
            )

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

    def _buildInputOutputTube(self, entry: InputOutput) -> s.objects.rotate:

        """
        Build the tube for an input or output from an InputOutput object, if
        it's external.

        Args:
            entry (InputOutput): I/O for which the external cylinder must be built

        Returns:
            s.objects.rotate: external cylinder (cad object) for 'entry'
        """

        # Outside radius
        r_ex = self._r + self._walls

        # Width of tube
        width = entry.diameter + 2 * self._walls

        # Calculate offset to correctly merge tube with reactor
        offset = r_ex - np.sqrt(r_ex ** 2 - (width / 2) ** 2)

        # Tube is merged into the wall, so it doesn't need to be L_EXT_INLET
        # long
        length = cst.L_EXT_INLET - self._walls + offset

        # Create the cylinder and apply transformations
        inner = s.cylinder(r=entry.diameter / 2, h=length + 2 * cst.F)
        inner = su.down(cst.F)(inner)
        outer = s.cylinder(r=width / 2, h=length)

        # Substract inner tube to outer shell
        tube = outer - inner

        # Apply translations
        tube = su.rotate([0, 90, 0])(tube)
        tube = su.right(r_ex - offset)(tube)
        tube = su.up(entry.height)(tube)
        tube = su.rotate([0, 0, entry.angle])(tube)

        return tube

    def _buildDefOutput(self) -> None:

        """
        Build the default output InputOutput object.

        Returns:
            None
        """  

        # If bottom has no pipe, try to delete the default output, then exit
        if self._type_bottom not in self.BOTTOMS_PIPE:
            try:
                del self.outputs["default"]
            except KeyError:
                pass
            return

        # Default output when internal outlet
        if self._type_bottom in [self.B_ROUND_IN_O, self.B_FLAT_IN_O]:

            # Calculate coordinates of center of output
            # Don't forget to add the actual z of the reactor. _buildDefOutput
            # is called each time type_bottom is changed(it's called when OK
            # button is clicked in GUI dialog box)
            h = self._walls + self._d_can / 2 + self.coo["z"]

            external = False

        # Default output when external outlet
        elif self._type_bottom in [self.B_ROUND_EX_O, self.B_FLAT_EX_O]:

            # Calculate coordinates of center of output
            # Don't forget to add the actual z of the reactor. _buildDefOutput
            # is called each time type_bottom is changed(it's called when OK
            # button is clicked in GUI dialog box)
            h = self._walls + cst.D_EXT_INLET / 2 + self.coo["z"]

            external = True

        # Try to update the IO object if it exists, or
        # Create an InputObject and put it in the dic of outputs
        try:
            self.outputs["default"].height = h
            self.outputs["default"].diameter = self._d_can
            self.outputs["default"].angle = self._def_out_angle
            self.outputs["default"].external = external
        except KeyError:
            self.outputs["default"] = InputOutput(
                h, self._d_can, self._def_out_angle, external
            )

    def _buildSupport(self) -> s.objects.difference:

        """
        Build support underneath the reactor when it's lifted

        Returns:
            s.objects.difference: the support (vertical tube, cad object)
        """

        z = self.coo["z"]

        outer = s.cylinder(r=self._r + self._walls, h=z + 2 * cst.F)
        outer = su.down(cst.F)(outer)

        # Maker inner cylinder taller by 2 * cst.F to avoid display bug in
        # openscad
        inner = s.cylinder(r=self._r + self._walls - cst.WALLS_S, h=z + 4 * cst.F)
        inner = su.down(2 * cst.F)(inner)

        support = outer - inner

        return support

    def _buildBody(self) -> s.objects.difference:

        """
        Build the body of the reactor

        Returns:
            s.objects.difference: the cad object for the body
        """     

        # Build the body: a simple pipe
        # cst.F to avoid non-manifold surfaces with the top and the bottom
        outer = s.cylinder(r=self._r + self._walls, h=self._h + 2 * cst.F)
        outer = su.down(cst.F)(outer)

        # Maker inner cylinder taller by 2 * cst.F to avoid display bug in
        # openscad
        inner = s.cylinder(r=self._r, h=self._h + 4 * cst.F)
        inner = su.down(2 * cst.F)(inner)

        body = outer - inner

        return body

    def _buildTop(self) -> Optional[s.objects.difference]:

        """
        Build the top of the reactor

        Returns:
            Optional[s.objects.difference]: cad object for the top of the body. None
                                            if top is open
        """

        # Round closed top
        if self._type_top == self.T_CLOSED_ROUND:

            height_top = self._calculateHTop(inlet=False)

            # Base cylinder
            base = s.cylinder(r=self._r + self._walls, h=height_top)

            # Sphere to make the top round
            sphere = s.sphere(r=self._r)

            top = base - sphere

            return top

        # Round closed top with inlet
        elif self._type_top == self.T_CLOSED_ROUND_O:

            height_top = self._calculateHTop(inlet=False)
            tot_height_top = self._calculateHTop()

            # Base cylinder
            base = s.cylinder(r=self._r + self._walls, h=height_top)

            # Sphere to make the top round
            sphere = s.sphere(r=self._r)

            # Hole for the inlet. Will also go through the adaptor's cylinder
            hole = s.cylinder(r=cst.D_EXT_INLET / 2, h=tot_height_top + cst.F)

            # An external inlet needs to be L_EXT_INLET long, but the thickness
            # of the wall contributes to this length -> re-calculate length
            # that needs to be added after the wall
            shortened_l = cst.L_EXT_INLET - self._walls

            # Cylinder for adaptor
            outer = s.cylinder(r=cst.D_EXT_INLET / 2 + self._walls, h=shortened_l)
            outer = su.up(height_top)(outer)

            top = base - sphere + outer - hole

            return top

        # Threaded tops
        elif self._type_top in self.THREADED_TOPS:

            height_top = self._calculateHTop(inlet=False)

            # Outer cylinder
            outer = s.cylinder(r=self._r + self._walls, h=height_top)

            # Inner cylinder
            inner = s.cylinder(r=self._r, h=height_top + 2 * cst.F)
            inner = su.down(cst.F)(inner)

            top = outer - inner

            return top

        # Custom top with custom inlets
        elif self._type_top == self.T_CUSTOM:

            height_top = self._calculateHTop(inlet=False)
            tot_height_top = self._calculateHTop()

            # Base cylinder
            base = s.cylinder(r=self._r + self._walls, h=height_top)

            # Sphere to make the top round
            sphere = s.sphere(r=self._r)

            top = base - sphere

            for inlet in self.top_inlets.values():

                # Hole for the inlet. Will also go through the adaptor's
                # cylinder
                hole = s.cylinder(r=inlet.diameter / 2, h=tot_height_top + cst.F)

                # An external inlet needs to be L_EXT_INLET long, but
                # the thickness of the wall contributes to this length ->
                # re-calculate length that needs to be added after the wall
                shortened_l = inlet.length - self._walls

                # Cylinder for adaptor
                outer = s.cylinder(r=inlet.diameter / 2 + inlet.walls, h=shortened_l)
                outer = su.up(height_top)(outer)

                hole = su.forward(inlet.y)(hole)
                hole = su.right(inlet.x)(hole)

                outer = su.forward(inlet.y)(outer)
                outer = su.right(inlet.x)(outer)

                outer -= hole
                top -= hole
                top += outer

            return top

        # No top, return None
        else:
            return None

    def _buildBottom(self) -> s.objects.difference:

        """
        Build the bottom of the reactor (pipe, outlets and everything).
        Will call more specialized sub-methods depending on the type of bottom

        Returns:
            s.objects.difference: the cad object for the bottom
        """

        # Round bottom
        if self._type_bottom == self.B_ROUND:
            bottom = self._buildRoundBottom()

        # Round bottom, internal outlet
        elif self._type_bottom == self.B_ROUND_IN_O:
            bottom = self._buildRoundBottomInO()

        # Round bottom with external inlet (adaptor)
        elif self._type_bottom == self.B_ROUND_EX_O:
            bottom = self._buildRoundBottomExO()

        # Simple flat bottom
        elif self._type_bottom == self.B_FLAT:
            bottom = self._buildFlatBottom()

        # Flat bottom w/ internal inlet
        elif self._type_bottom == self.B_FLAT_IN_O:
            bottom = self._buildFlatBottomInO()

        # Flat bottom w/ external inlet
        elif self._type_bottom == self.B_FLAT_EX_O:
            bottom = self._buildFlatBottomExO()

        return bottom

    def _buildRoundBottom(self) -> s.objects.difference:

        """
        Build a simple round bottom. Called from _buildBottom

        Returns:
            s.objects.difference: the cad object for the bottom
        """

        # Calculate the height of the bottom, to offset the body and the top,
        # so very bottom of reactor starts at z=0
        h_bottom, offset_ext_inlet = self._calculateHBottom()

        # Main bottom cylinder
        bottom = s.cylinder(r=self._r + self._walls, h=h_bottom)

        # Substract sphere to create round bottom
        bottom -= su.up(self._walls + self._r)(s.sphere(r=self._r))

        return bottom

    def _buildRoundBottomInO(self) -> s.objects.difference:

        """
        Build a round bottom with internal outlet.
        Called from _buildBottom

        Returns:
            s.objects.difference: the cad object for the bottom
        """

        # Calculate the height of the bottom, to offset the body and the top,
        # so very bottom of reactor starts at z=0
        h_bottom, offset_ext_inlet = self._calculateHBottom()

        # Main bottom cylinder
        base = s.cylinder(r=self._r + self._walls, h=h_bottom)

        sphere = s.sphere(r=self._r)
        sphere = su.up(self._r + 2 * self._walls + self._d_can)(sphere)

        # Joint between bottom of chamber and bent pipe
        # Double length of joint so it pierces the sphere. Add cst.F to
        # length, and up -cst.F to avoid non manifold surfac
        joint = s.cylinder(r=self._d_can / 2, h=self._d_can + cst.F)
        joint = su.up(2 * self._walls + self._d_can / 2 - cst.F)(joint)

        # Bent pipe for siphon. Turns pipe from vertical to horizontal
        pipe = BentPipeCAD(self._d_can, 0, self._walls).cad
        pipe = su.rotate([-90, 0, 180])(pipe)
        pipe = su.up(2 * self._walls + self._d_can / 2)(pipe)
        pipe = su.right(self._walls)(pipe)

        # Horizontal pipe between the bent pipe and the outside of the
        # reactor. Add cst.F to avoid non manifold surface
        h_tube = s.cylinder(r=self._d_can / 2, h=self._r + cst.F)
        h_tube = su.rotate([0, 90, 0])(h_tube)
        h_tube = su.right(self._walls - cst.F)(h_tube)
        h_tube = su.up(self._walls + self._d_can / 2)(h_tube)

        # Rotate the entire output pipe if an angle is provided for
        # the output
        pipe = su.rotate([0, 0, self._def_out_angle])(pipe)
        h_tube = su.rotate([0, 0, self._def_out_angle])(h_tube)

        bottom = base - sphere - pipe - joint - h_tube

        return bottom

    def _buildRoundBottomExO(self) -> s.objects.difference:

        """
        Build a round bottom with external outlet.
        Called from _buildBottom

        Returns:
            s.objects.difference: the cad object for the bottom
        """

        # Calculate the height of the bottom, to offset the body and the top,
        # so very bottom of reactor starts at z=0
        h_bottom, offset_ext_inlet = self._calculateHBottom()

        # Main bottom cylinder
        base = s.cylinder(r=self._r + self._walls, h=h_bottom)

        # Sphere to make the inside chamber w/ a round bottom
        sphere = s.sphere(r=self._r)
        sphere = su.up(self._r + 2 * self._walls + self._d_can + offset_ext_inlet)(
            sphere
        )

        # Joint between bottom of chamber and bent pipe
        # Double length of joint so it pierces the sphere, add cst.F
        # length and up the joint by -cst.F to aovid non manifold surface
        joint = s.cylinder(r=self._d_can / 2, h=self._d_can + cst.F)
        joint = su.up(2 * self._walls + self._d_can / 2 + offset_ext_inlet - cst.F)(
            joint
        )

        # Bent pipe for siphon. Turns pipe from vertical to horizontal
        pipe = BentPipeCAD(self._d_can, 0, self._walls).cad
        pipe = su.rotate([-90, 0, 180])(pipe)
        pipe = su.up(2 * self._walls + self._d_can / 2 + offset_ext_inlet)(pipe)

        pipe = su.right(self._walls)(pipe)

        # Horizontal pipe between the bent pipe and the outside of the
        # reactor. cst.F to avoid non-manifold surface
        h_tube = s.cylinder(r=self._d_can / 2, h=self._r + 2 * cst.F)
        h_tube = su.rotate([0, 90, 0])(h_tube)
        h_tube = su.right(self._walls - cst.F)(h_tube)
        h_tube = su.up(self._walls + self._d_can / 2 + offset_ext_inlet)(h_tube)

        # Calculate dimensions for small cylinder used to make a flat surface
        # for the external outlet. Allows better tightening of Luer adaptors
        r_ex: float = self.infos["r_ex"]
        w_flat_surf = cst.D_EXT_INLET + 2 * self._walls
        offset = r_ex - np.sqrt(r_ex ** 2 - (w_flat_surf / 2) ** 2) + cst.ADD_TAP_BOTTOM

        # Horizontal pipe for external inlet
        ex_inlet = s.cylinder(
            r=cst.D_EXT_INLET / 2, h=cst.L_EXT_INLET + cst.ADD_TAP_BOTTOM + cst.F
        )
        ex_inlet = su.rotate([0, 90, 0])(ex_inlet)
        ex_inlet = su.right(self._walls + self._r - cst.L_EXT_INLET)(ex_inlet)
        ex_inlet = su.up(self._walls + self._d_can / 2 + offset_ext_inlet)(ex_inlet)

        # Create flat surface (simple cylinder)
        flat_surf = s.cylinder(r=w_flat_surf / 2, h=offset)
        flat_surf = su.rotate([0, 90, 0])(flat_surf)
        flat_surf = su.right(r_ex - offset + cst.ADD_TAP_BOTTOM)(flat_surf)
        flat_surf = su.up(self._walls + self._d_can / 2 + offset_ext_inlet)(flat_surf)

        # Rotate the entire output pipe if an angle is provided for
        # the output
        pipe = su.rotate([0, 0, self._def_out_angle])(pipe)
        h_tube = su.rotate([0, 0, self._def_out_angle])(h_tube)
        ex_inlet = su.rotate([0, 0, self._def_out_angle])(ex_inlet)
        flat_surf = su.rotate([0, 0, self._def_out_angle])(flat_surf)

        bottom = base + flat_surf - pipe - joint - h_tube - sphere - ex_inlet

        return bottom

    def _buildFlatBottom(self) -> s.objects.difference:

        """
        Build a flat bottom.
        Called from _buildBottom

        Returns:
            s.objects.difference: the cad object for the bottom
        """

        # Calculate the height of the bottom, to offset the body and the top,
        # so very bottom of reactor starts at z=0
        h_bottom, offset_ext_inlet = self._calculateHBottom()

        # Main bottom cylinder
        bottom = s.cylinder(r=self._r + self._walls, h=h_bottom)

        return bottom

    def _buildFlatBottomInO(self) -> s.objects.difference:

        """
        Build a flat bottom with internal outlet
        Called from _buildBottom

        Returns:
            s.objects.difference: the cad object for the bottom
        """

        # Calculate the height of the bottom, to offset the body and the top,
        # so very bottom of reactor starts at z=0
        h_bottom, offset_ext_inlet = self._calculateHBottom()

        # Main bottom cylinder
        base = s.cylinder(r=self._r + self._walls, h=h_bottom)

        # Joint between bottom of chamber and bent pipe
        # Double length of joint so it pierces the sphere
        # cst.F to avoid non-manifold surface
        joint = s.cylinder(r=self._d_can / 2, h=self._d_can + cst.F)
        joint = su.up(2 * self._walls + self._d_can / 2 - cst.F)(joint)

        # Bent pipe for siphon. Turns pipe from vertical to horizontal
        pipe = BentPipeCAD(self._d_can, 0, self._walls).cad
        pipe = su.rotate([-90, 0, 180])(pipe)
        pipe = su.up(2 * self._walls + self._d_can / 2)(pipe)
        pipe = su.right(self._walls)(pipe)

        # Horizontal pipe between the bent pipe and the outside of the
        # reactor
        h_tube = s.cylinder(r=self._d_can / 2, h=self._r + cst.F)
        h_tube = su.rotate([0, 90, 0])(h_tube)
        h_tube = su.right(self._walls - cst.F)(h_tube)
        h_tube = su.up(self._walls + self._d_can / 2)(h_tube)

        # Rotate the entire output pipe if an angle is provided for
        # the output
        pipe = su.rotate([0, 0, self._def_out_angle])(pipe)
        h_tube = su.rotate([0, 0, self._def_out_angle])(h_tube)

        bottom = base - joint - pipe - h_tube

        return bottom

    def _buildFlatBottomExO(self) -> s.objects.difference:

        """
        Build a flat bottom with external outlet.
        Called from _buildBottom

        Returns:
            s.objects.difference: the cad object for the bottom
        """

        # Calculate the height of the bottom, to offset the body and the top,
        # so very bottom of reactor starts at z=0
        h_bottom, offset_ext_inlet = self._calculateHBottom()

        # Main bottom cylinder
        base = s.cylinder(r=self._r + self._walls, h=h_bottom)

        # Joint between bottom of chamber and bent pipe
        # Double length of joint so it pierces the sphere. cst.F to avoid
        # non-manifold surface
        joint = s.cylinder(r=self._d_can / 2, h=self._d_can + cst.F)
        joint = su.up(2 * self._walls + self._d_can / 2 + offset_ext_inlet - cst.F)(
            joint
        )

        # Bent pipe for siphon. Turns pipe from vertical to horizontal
        pipe = BentPipeCAD(self._d_can, 0, self._walls).cad
        pipe = su.rotate([-90, 0, 180])(pipe)
        pipe = su.up(2 * self._walls + self._d_can / 2 + offset_ext_inlet)(pipe)
        pipe = su.right(self._walls)(pipe)

        # Horizontal pipe between the bent pipe and the outside of the
        # reactor. cst.F to avoid non manifold surface
        h_tube = s.cylinder(r=self._d_can / 2, h=self._r + 2 * cst.F)
        h_tube = su.rotate([0, 90, 0])(h_tube)
        h_tube = su.right(self._walls - cst.F)(h_tube)
        h_tube = su.up(self._walls + self._d_can / 2 + offset_ext_inlet)(h_tube)

        # Calculate dimensions for small cylinder used to make a flat surface
        # for the external outlet. Allows better tightening of Luer adaptors
        r_ex: float = self.infos["r_ex"]
        w_flat_surf = cst.D_EXT_INLET + 2 * self._walls
        offset = r_ex - np.sqrt(r_ex ** 2 - (w_flat_surf / 2) ** 2) + cst.ADD_TAP_BOTTOM

        # Horizontal pipe for external inlet
        ex_inlet = s.cylinder(
            r=cst.D_EXT_INLET / 2, h=cst.L_EXT_INLET + cst.F + cst.ADD_TAP_BOTTOM
        )
        ex_inlet = su.rotate([0, 90, 0])(ex_inlet)
        ex_inlet = su.right(self._walls + self._r - cst.L_EXT_INLET)(ex_inlet)
        ex_inlet = su.up(self._walls + self._d_can / 2 + offset_ext_inlet)(ex_inlet)

        # Create flat surface (simple cylinder)
        flat_surf = s.cylinder(r=w_flat_surf / 2, h=offset)
        flat_surf = su.rotate([0, 90, 0])(flat_surf)
        flat_surf = su.right(r_ex - offset + cst.ADD_TAP_BOTTOM)(flat_surf)
        flat_surf = su.up(self._walls + self._d_can / 2 + offset_ext_inlet)(flat_surf)

        # Rotate the entire output pipe if an angle is provided for
        # the output
        pipe = su.rotate([0, 0, self._def_out_angle])(pipe)
        h_tube = su.rotate([0, 0, self._def_out_angle])(h_tube)
        ex_inlet = su.rotate([0, 0, self._def_out_angle])(ex_inlet)
        flat_surf = su.rotate([0, 0, self._def_out_angle])(flat_surf)

        bottom = base + flat_surf - pipe - joint - h_tube - ex_inlet

        return bottom

    def _buildCadCode(self) -> s.objects.translate:

        """
        Build the CAD code w/ SolidPython.
        Call methods to generate bottom, body and top and assemble them.

        Returns:
            s.objects.translate: the cad object for the entire reactor
        """

        # Calculate the height of the bottom, to offset the body and the top,
        # so very bottom of reactor starts at z=0
        h_bottom = self._calculateHBottom()[0]

        # Generate the bottom, and get the height of the bottom to offset body
        # and top
        bottom = self._buildBottom()
        body = self._buildBody()
        top = self._buildTop()

        # If liftReactor was called, lift the reactor with support
        if self.coo["z"] != 0:
            support = self._buildSupport()
            bottom = su.up(self.coo["z"])(bottom)
            bottom = support + bottom
            h_bottom += self.coo["z"]

        # Assemble bottom and body. No need for cst.F, already done in
        # _buildBody
        total = bottom + su.up(h_bottom)(body)

        # Add the top
        if top is not None:
            total += su.up(h_bottom + self._h)(top)

        # Simplify rotation angle for reactor, and use it to rotate reactor
        simple_angle = misc.simplifyAngle(self.coo["angle"])
        self.coo["angle"] = simple_angle

        total = su.rotate([0, 0, simple_angle])(total)

        # Build the inputs
        for entry in self.inputs.values():
            new_in = self._buildInputOutputHole(entry)
            total -= new_in

            if entry.external:
                new_in = self._buildInputOutputTube(entry)
                total += new_in

        # Build the outputs, except the default one if bottom has pipe
        for key, entry in self.outputs.items():
            if key == "default" and self._type_bottom in self.BOTTOMS_PIPE:
                continue
            new_out = self._buildInputOutputHole(entry)
            total -= new_out

            if entry.external:
                new_out = self._buildInputOutputTube(entry)
                total += new_out

        # Move the entire reactor, inputs included
        total = su.right(self.coo["x"])(total)
        total = su.forward(self.coo["y"])(total)

        return total


if __name__ == "__main__":

    import numpy as np
    import trimesh
    import collections
    import trimesh

    # r = ReactorCAD(20, ReactorCAD.T_2_QUA_INCH, ReactorCAD.B_ROUND_EX_O, d_can=5)
    r = ReactorCAD(60, ReactorCAD.T_4_QUA_INCH, ReactorCAD.B_FLAT_EX_O)
    r.addInputPercentage("test")
    # r = ReactorCAD(20, ReactorCAD.T_CLOSED_ROUND_O, ReactorCAD.B_ROUND_EX_O)

    # r.walls = 4

    print(repr(r.describe()))

    # print(r.d_can)

    # r.type_bottom = ReactorCAD.B_FLAT_EX_O
    # r.addInputPercentage('test')

    # r.createLuerTopInlet('test')
    # r.createLuerTopInlet('in2')
    # r.createLuerTopInlet('in3')
    # r.createLuerTopInlet('in4')
    # r.createLuerTopInlet('in5')

    # print(r.inputs['test'])
    # print(r._calculateHBottom())

    # r.autoPlaceTopInlets()
    # print(r.top_inlets['test'])
    # r.type_bottom = ReactorCAD.B_FLAT_IN_O

    # print(r.inputs['test'])
    # print(r._calculateHBottom())

    # r.volume = 30
    # r.r = 14
    # print(r._r, r._h)
    # print(r.volume)
    # print(r.outputs['default'])
    # r.d_can = 5
    # print(r.outputs['default'])

    # print(r.outputs['default'])

    # r.walls = 4
    # print(r.outputs['default'])

    # print(r._h)
    # print(r._r)

    # 36.143031501221586
    # 11.168810962106537

    # r.type_top = ReactorCAD.T_OPEN
    # r.type_bottom = ReactorCAD.B_FLAT_EX_O
    # r.volume = 30

    # print(r._h)
    # print(r._r)

    # 38.093832603499514
    # 11.771641655355797

    # r.renderToFile("test.scad")

    # print(r)

    pass
