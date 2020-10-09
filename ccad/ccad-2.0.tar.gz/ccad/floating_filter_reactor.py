#!/usr/bin/python
# coding: utf-8

import solid as s
import solid.utils as su
import numpy as np
from typing import Tuple, Union, Optional, Dict
import warnings

from . import misc
from .exceptions import *
from . import constants as cst
from .in_out import InputOutput
from .top_in import TopInlet
from .filter_like_reactors import FilterLikeReactor


class FloatingFilterReactorCAD(FilterLikeReactor):

    """
    Class for reactor with a 'floating' filter (the filter space is in the
    body of the reactor)
    """

    ALIGN_FILTER_STRATEGIES = ["Lift reactor", "Move filter"]
    EXPAND_STRATEGIES = ["Expand top chamber", "Expand bottom chamber"]

    def __init__(
        self,
        volume_bottom: float,
        volume_top: float,
        type_top: str,
        type_bottom: str,
        d_filter: float,
        h_filter: float,
        def_out_angle: float = 0,
        *args,
        **kwargs,
    ) -> None:

        """
        Volumes are in mL, and will be converted to mm3. type_top and
        type_bottom should be strings enumerated in reactor.py. d_filter
        and h_filter are the diameter and height of the filter, respectively.
        def_out_angle is the angle for the default output (trigonometric
        direction)

        Arguments:
            volume_bottom {float} -- [description]
            volume_top {float} -- [description]
            type_top {str} -- [description]
            type_bottom {str} -- [description]
            d_filter {float} -- [description]
            h_filter {float} -- [description]

        Keyword Arguments:
            def_out_angle {float} -- [description] (default: {0})

        Raises:
            NotImplementedError -- [description]

        Returns:
            None
        """

        # Name/module type, used by GUI to connect slot and signals
        self.module_type = "Floating filter reactor"
        self.module_type_short = "FFR"

        # Bool to check if r is constrained
        self.r_constrained = False

        # Bool to check if top is aligned
        self.top_aligned = False

        self._type_top = type_top
        self._type_bottom = type_bottom

        # Crash if user tries to set a threaded top for this reactor
        if self._type_top in self.THREADED_TOPS:
            mes = "FloatingFilterReactor can't have a threaded top (yet)"
            raise NotImplementedError(mes)

        # Convert volumes to mm3
        self._volume_bottom = volume_bottom * 1000
        self._volume_top = volume_top * 1000

        # Filter's dimensions
        self._d_filter = d_filter
        self._h_filter = h_filter

        # Translations to apply before generating CAD code
        # Will be modified by connectors
        self.coo: Dict[str, float] = {"x": 0, "y": 0, "z": 0, "angle": 0}

        # Find some dimensions
        # Initially we set internal r to 0
        # If not constrained it will be calculated later
        # If constrained, it will be set by user
        self._r_int = 0
        # r is the calculation based on the filter, r_int is set by user
        # if user doesnt set r_int, then r=r_int
        self._h, self._r = self._findHeightRadius()

        # Additional checks on top and bottom values. Done here bc self._r is
        # required to perform these checks
        self._checkVolumeBottom(volume_bottom)
        self._checkVolumeTop(volume_top)

        self._handleExtraArgs(kwargs)

        # Find z for filter
        self._z_filter = self._findZFilter()

        self.inputs: Dict[str, InputOutput] = dict()
        self.outputs: Dict[str, InputOutput] = dict()
        self.top_inlets: Dict[str, TopInlet] = dict()

        # Angle for the output, starting from x axis, clockwise
        self._def_out_angle = misc.simplifyAngle(def_out_angle)

        self._buildDefOutput()

    def _handleExtraArgs(self, kwargs: dict) -> None:

        """
        [summary]

        Arguments:
            kwargs {dict} -- [description]

        Returns:
            None
        """

        super()._handleExtraArgs(kwargs)

        # wall thickness, done in super already but redo here, wall thickness should
        # be WALLS_F here
        self._walls: float
        if "walls" in kwargs:
            self._walls = self._getMinWalls(kwargs["walls"])
        else:
            self._walls = cst.WALLS_F

        # Strategy to align the top of the cartridge
        # possible values for align_top_strategy (difference w base class):
        # - expand (will expand the body of the reactor. See expand_strategy)
        # - lift (will lift the reactor)
        self.align_top_strategy: str
        if "align_top_strategy" in kwargs:
            self.align_top_strategy = kwargs["align_top_strategy"]
        else:
            self.align_top_strategy = "expand"

        # What expand strategy should be used if 'align_top_strategy'
        # is set to 'expand'
        # Possible values:
        # - expand_top: expand the top chamber
        # - expand_bottom: expand the bottom chamber
        self.expand_strategy: str
        if "expand_strategy" in kwargs:
            self.expand_strategy = kwargs["expand_strategy"]

            # Display warning if the user sets the expand_strategy while
            # align_top_strategy is not expand
            if self.align_top_strategy != "expand":
                mes = "Expand strategy is set but align_top_strategy"
                mes = mes + " is not expand"
                warnings.warn(mes)
        else:
            self.expand_strategy = "expand_top"

        # Strategy to align the top of the filter
        # possible values for align_filter_strategy:
        # - lift: valid only if top is not aligned. Lift the entire reactor
        # to align filter
        # - move_filter: move the filter. If filter goes down, reduce bottom
        #                chamber. If filter goes up, reduce top chamber
        self.align_filter_strategy: str
        if "align_filter_strategy" in kwargs:
            self.align_filter_strategy = kwargs["align_filter_strategy"]
        else:
            self.align_filter_strategy = "lift"

    def _checkVolumeTop(self, volume_top: float) -> None:

        """
        Isolate checks for volume_top in this function.
        Return True if volume_top is valid, False otherwise

        Arguments:
            volume_top {float} -- [description]

        Raises:
            ConstraintError -- [description]

        Returns:
            None
        """

        if self.type_top in self.CLOSED_TOPS:
            v_min = 2 / 3 * np.pi * self._r ** 3

            # Convert to mL
            v_min /= 1000
        else:
            v_min = 0

        # Check that volume > minimum volume. Ensures that filter won't be in
        # the bottom or top part
        if volume_top < v_min:
            raise ConstraintError(f"V top must be > {v_min} with this type of top")

    def _checkVolumeBottom(self, volume_bottom: float) -> None:

        """
        Isolate checks for volume_bottom in this function.
        Return True if volume_bottom is valid, False otherwise

        Arguments:
            volume_bottom {float} -- [description]

        Raises:
            ConstraintError -- [description]

        Returns:
            None
        """

        # Check that volume > minimum volume. Ensures that filter won't be in
        # the bottom or top part
        if self.type_bottom in self.ROUND_BOTS:
            v_min = 2 / 3 * np.pi * self._r ** 3

            # Convert to mL
            v_min /= 1000
        else:
            v_min = 0

        if volume_bottom < v_min:
            mes = f"Volume bottom must be > {v_min} with this type of bottom"
            raise ConstraintError(mes)

    @FilterLikeReactor.type_top.setter
    def type_top(self, type_top: str) -> None:

        """
        Change top type, call volume setter to recalculate dimensions to match the
        volume. Re-implemented from base class since r is calculated based on the
        filter in this class, and can't vary.

        Arguments:
            type_top: The new type of top

        Returns:
            None
        """

        self._type_top = type_top

        # Setting the volume will trigger calculation of dimensions
        self.volume_top = self._volume_top / 1000

    @FilterLikeReactor.type_bottom.setter
    def type_bottom(self, type_bottom: str) -> None:

        """
        Change bottom type, call volume setter to recalculate dimensions to
        match the volume

        Arguments:
            type_bottom {str} -- [description]

        Returns:
            None
        """

        # Store h_bottom before change
        h_bottom, _ = self._calculateHBottom()

        self._type_bottom = type_bottom

        # Setting the volume will trigger calculation of dimensions
        self.volume_bottom = self._volume_bottom / 1000

        # Try to build the default output
        # Will do nothing if the new type of bottom has no pipe
        self._buildDefOutput()

        # Store h_bottom after bottom changed
        new_h_bottom, _ = self._calculateHBottom()

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
    def volume(self) -> float:

        """
        Return volume in mL, not mm3.
        Volume returned = volume_top + volume_bottom
        Setter is not defined bc user must set volume_top or volume_bottom,
        not directly total volume

        Returns:
            float -- [description]
        """

        return (self._volume_top + self._volume_bottom) / 1000

    @property
    def volume_bottom(self) -> float:

        """
        Return volume in mL, not mm3

        Returns:
            float -- [description]
        """

        return self._volume_bottom / 1000

    @volume_bottom.setter
    def volume_bottom(self, value: float) -> None:

        """
        Check validity of value, must be positive.
        Trigger calculation of _h and _r

        Arguments:
            value {float} -- [description]

        Returns:
            None
        """

        # Check the volume is valid
        self._checkVolumeBottom(value)

        self._volume_bottom = value * 1000

        # Refresh dimensions
        self._h, self._r = self._findHeightRadius()

    @property
    def volume_top(self) -> float:

        """
        Return volume in mL, not mm3

        Returns:
            float -- [description]
        """

        return self._volume_top / 1000

    @volume_top.setter
    def volume_top(self, value: float) -> None:

        """
        Check validity of value, must be positive.
        Trigger calculation of _h and _r

        Arguments:
            value {float} -- [description]

        Returns:
            None
        """

        # Check the volume is valid
        self._checkVolumeTop(value)

        self._volume_top = value * 1000

        # Refresh dimensions
        self._h, self._r = self._findHeightRadius()

    @property
    def d_filter(self) -> float:

        """
        Return filter's diameter

        Returns:
            float -- [description]
        """

        return self._d_filter

    @d_filter.setter
    def d_filter(self, value: float) -> None:

        """
        Check and set filter's diameter. Refresh reactor's dimensions

        Arguments:
            value {float} -- [description]

        Returns:
            None
        """

        self._d_filter = value

        # Refresh dimensions
        self._h, self._r = self._findHeightRadius()
        self._z_filter = self._findZFilter()

    @property
    def h_filter(self) -> float:

        """
        Return filter's height

        Returns:
            float -- [description]
        """

        return self._h_filter

    @h_filter.setter
    def h_filter(self, value: float) -> None:

        """
        Check and set filter's height. Refresh reactor's dimensions

        Arguments:
            value {float} -- [description]

        Returns:
            None
        """

        self._h_filter = value

        # Refresh dimensions
        self._h, self._r = self._findHeightRadius()
        self._z_filter = self._findZFilter()

    @property
    def r_int(self) -> float:

        """
        Return radius for reactor

        Returns:
            float -- [description]
        """

        return self._r_int

    @r_int.setter
    def r_int(self, value: float) -> None:

        """
        Set the internal radius of the reactor.

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
            raise ImpossibleAction("Threaded top, can't set internal r")

        self.r_constrained = True

        # Crash if r is negative or null
        if value <= 0:
            raise ValueError("r must be > 0")

        self._r_int = value
        self._h, self._r = self._findHeightRadius()

    @property
    def infos(self) -> Dict[str, Union[str, float]]:

        """
        [summary]

        Returns:
            Dict[str, Union[str, float]] -- [description]
        """
        # Get infos from parent method
        infos: Dict[str, Union[str, float]] = super()._getInfos()

        # Remove volume key, will be replaced by volume_top and volume_bottom
        del infos["volume"]

        # Add infos to dict
        infos["volume_top"] = self.volume_top
        infos["volume_bottom"] = self.volume_bottom
        infos["z_top_filter"] = self.z_top_filter
        infos["z_bottom_filter"] = self.z_bottom_filter
        infos["h_filter"] = self._h_filter
        infos["d_filter"] = self._d_filter
        infos["align_filter_strategy"] = self.align_filter_strategy

        return infos

    def getHeightPercentage(self, entry: InputOutput) -> float:

        """
        Return the height percentage of an InputOutput belonging to this class
        Adapted from base class to take into account the chamber: top or bottom

        Arguments:
            entry {InputOutput} -- [description]

        Returns:
            float -- [description]
        """

        if entry.chamber == "bottom":
            return self._getHeightPercentageBottom(entry)
        elif entry.chamber == "top":
            return self._getHeightPercentageTop(entry)

    def _getHeightPercentageTop(self, entry: InputOutput) -> float:

        """
        Internal function. Calculate percentage height of top chamber for
        'entry', based on entry.height

        Arguments:
            entry {InputOutput} -- [description]

        Returns:
            float -- [description]
        """

        h_bottom, _ = self._calculateHBottom()

        # Calculate minimum and maximum heights
        min_h = self.z_top_filter + entry.diameter / 2

        # max height depends on type of reactor
        if self._type_top in self.CLOSED_TOPS:
            max_h = h_bottom + self._h - entry.diameter / 2
        else:
            max_h = h_bottom + self._h - entry.diameter / 2 - self._walls

        height_per = (entry.height - min_h) * 100 / (max_h - min_h)

        return height_per

    def _getHeightPercentageBottom(self, entry: InputOutput) -> float:

        """
        Internal function. Calculate percentage height of bottom chamber for
        'entry', based on entry.height

        Arguments:
            entry {InputOutput} -- [description]

        Returns:
            float -- [description]
        """

        h_bottom, _ = self._calculateHBottom()

        # Calculate minimum and maximum heights
        min_h = h_bottom + entry.diameter / 2
        max_h = self._z_filter - entry.diameter / 2

        height_per = (entry.height - min_h) * 100 / (max_h - min_h)

        return height_per

    def alignFilterToHeight(self, target_height: float) -> None:

        """
        Align the filter to 'target_height', depending on strategy. Keep
        top aligned if needed

        Arguments:
            target_height {float} -- [description]

        Raises:
            IncompatibilityError -- [description]
            ImpossibleAction -- [description]

        Returns:
            None
        """

        # Lift module to align top and lift module to align filter is not
        # possible, crash
        # N.B: crash only if the top is aligned. align_top_strategy could be
        # set to 'lift', but the top needs to be aligned explicitely
        if (
            self.top_aligned
            and self.align_top_strategy == "lift"
            and self.align_filter_strategy == "lift"
        ):

            mes = "align_top_strategy and align_filter_strategy can't be lift"
            mes = mes + " at the same time"
            raise IncompatibilityError(mes)

        # Simple case: top not aligned, strategy is lift. Lift the reactor
        # enough to reach target height
        elif not self.top_aligned and self.align_filter_strategy == "lift":
            self.liftReactor(target_height - self.z_top_filter)

        # Treat these cases the same way: top unchanged, align filter. If
        # top is aligned, let unchanged, align filter
        elif (
            self.align_filter_strategy == "move_filter"
            or (
                self.align_top_strategy == "lift"
                and self.align_filter_strategy == "move_filter"
            )
            or (
                self.align_top_strategy == "expand"
                and self.align_filter_strategy == "lift"
            )
            or (
                self.align_top_strategy == "expand"
                and self.align_filter_strategy == "move_filter"
            )
        ):

            # Here getHeightPercentage will return the percentage according to
            # the chamber (top or bottom)
            old_in_per = [self.getHeightPercentage(io) for io in self.inputs.values()]

            old_out_per = [self.getHeightPercentage(io) for io in self.outputs.values()]

            diff = target_height - self.z_top_filter

            # Calculate the change in volume
            expanding_volume = np.pi * self._r ** 2 * diff / 1000

            try:
                if diff > 0:
                    self._checkVolumeTop(self.volume_top - expanding_volume)
                else:
                    self._checkVolumeBottom(self.volume_bottom - expanding_volume)
            except ConstraintError:
                mes = "Can't align filter, negative volume for one chamber"
                raise ImpossibleAction(mes)

            if diff > 0:
                self.volume_bottom += expanding_volume
                self.volume_top -= expanding_volume
            else:
                self.volume_bottom -= expanding_volume
                self.volume_top += expanding_volume

            # Same operations as in expandVertically
            # I/Os were created with % of height. Height just changed, so get
            # old percentages and replace input to same percentages of
            # new height
            for old_per, dict_data in zip(old_in_per, self.inputs.items()):
                name, io = dict_data

                if io.chamber == "top":
                    self.addInputPercentageTop(
                        name,
                        height_per=old_per,
                        angle=io.angle,
                        diameter=io.diameter,
                        external=io.external,
                    )

                elif io.chamber == "bottom":
                    self.addInputPercentageBottom(
                        name,
                        height_per=old_per,
                        angle=io.angle,
                        diameter=io.diameter,
                        external=io.external,
                    )

            # I/Os were created with % of height. Height just changed, so get
            # old percentages and replace input to same percentages of
            # new height
            for old_per, dict_data in zip(old_out_per, self.outputs.items()):
                name, io = dict_data

                # Pass for default output
                if name == "default":
                    continue

                if io.chamber == "top":
                    self.addOutputPercentageTop(
                        name,
                        height_per=old_per,
                        angle=io.angle,
                        diameter=io.diameter,
                        external=io.external,
                    )

                elif io.chamber == "bottom":
                    self.addOutputPercentageTop(
                        name,
                        height_per=old_per,
                        angle=io.angle,
                        diameter=io.diameter,
                        external=io.external,
                    )

    def addInputPercentage(
        self,
        name: str,
        height_per: float = 100,
        angle: float = 180,
        diameter: Optional[float] = None,
        external: bool = False,
    ) -> None:

        """
        [summary]

        Arguments:
            name {str} -- [description]

        Keyword Arguments:
            height_per {float} -- [description] (default: {100})
            angle {float} -- [description] (default: {180})
            diameter {Optional[float]} -- [description] (default: {None})
            external {bool} -- [description] (default: {False})

        Raises:
            AttributeError -- [description]

        Returns:
            None
        """

        mes = "'FloatingFilterReactorCAD' object has no attribute 'addInputPercentage'. \
                Use addInputBottomPercentage or addInputTopPercentage instead"

        mes = mes.replace("    ", "")

        raise AttributeError(mes)

    def addOutputPercentage(
        self,
        name: str,
        height_per: float = 100,
        angle: float = 180,
        diameter: Optional[float] = None,
        external: bool = False,
    ) -> None:

        """
        [summary]

        Arguments:
            name {str} -- [description]

        Keyword Arguments:
            height_per {float} -- [description] (default: {100})
            angle {float} -- [description] (default: {180})
            diameter {Optional[float]} -- [description] (default: {None})
            external {bool} -- [description] (default: {False})

        Raises:
            AttributeError -- [description]

        Returns:
            None
        """

        mes = "'FloatingFilterReactorCAD' object has no attribute 'addOutputPercentage'. \
                Use addOutputBottomPercentage or addOutputTopPercentage instead"

        mes = mes.replace("    ", "")

        raise AttributeError(mes)

    def _addInput(
        self,
        name: str,
        height: float,
        diameter: float,
        angle: float = 180,
        external: bool = False,
        chamber: str = "bottom",
    ) -> None:

        """
        Add an input to the reactor. Check there is no collision with filter
        - height: height, in mm, will be checked
        - angle: angle of input, start from x-axis, trigonometric rotation
        - diameter: diameter of input
        - chamber: 'top' or 'bottom' chamber. Default is top. Not useful
          in API, necessary in GUI

        Internal function. The user should never call it directly. The
        user can only add I/O with percentage height. Functions like
        expandVertically will always assume an I/O was added trhough
        percentage, and will always try to move the I/O to the right
        percentage.

        Arguments:
            name {str} -- [description]
            height {float} -- [description]
            diameter {float} -- [description]

        Keyword Arguments:
            angle {float} -- [description] (default: {180})
            external {bool} -- [description] (default: {False})
            chamber {str} -- [description] (default: {"bottom"})

        Raises:
            ConstraintError -- [description]

        Returns:
            None
        """

        # Get the height of the bottom
        h_bottom, _ = self._calculateHBottom()

        # If diameter is none, set diameter according to external/internal I/O
        if diameter is None and not external:
            diameter = cst.D_CAN
        elif diameter is None and external:
            diameter = cst.D_EXT_INLET

        # Calculate minimum and maximum heights for bottom
        min_h1 = h_bottom + diameter / 2
        max_h1 = self._z_filter - diameter / 2

        # Calculate minimum and maximum heights for top
        min_h2 = self._z_filter + self._h_filter + diameter / 2

        # max height depends on type of reactor
        if self._type_top in self.CLOSED_TOPS:
            max_h2 = h_bottom + self._h - diameter / 2
        else:
            max_h2 = h_bottom + self._h - diameter / 2 - self._walls

        if not (height >= min_h1 and height <= max_h1) and not (
            height >= min_h2 and height <= max_h2
        ):

            mes = "Input's h must be between {min_h1} and {max_h1} or "
            mes += f"between {max_h1} and {max_h2}"

            raise ConstraintError(mes)

        # Try to update the IO object if it exists, or
        # Create an InputObject and put it in the dic of inputs
        try:
            self.inputs[name].height = height
            self.inputs[name].diameter = diameter
            self.inputs[name].angle = angle
            self.inputs[name].external = external
            self.inputs[name].chamber = chamber
        except KeyError:
            self.inputs[name] = InputOutput(height, diameter, angle, external, chamber)

    def _addOutput(
        self,
        name: str,
        height: float,
        diameter: float,
        angle: float = 180,
        external: bool = False,
        chamber: str = "top",
    ) -> None:

        """
        Add an output to the reactor. Check there is no collision with filter
        - height: height, in mm, will be checked
        - angle: angle of input, start from x-axis, trigonometric rotation
        - diameter: diameter of input
        - chamber: 'top' or 'bottom' chamber. Default is top. Not useful
          in API, necessary in GUI

        Internal function. The user should never call it directly. The
        user can only add I/O with percentage height. Functions like
        expandVertically will always assume an I/O was added trhough
        percentage, and will always try to move the I/O to the right
        percentage.

        Arguments:
            name {str} -- [description]
            height {float} -- [description]
            diameter {float} -- [description]

        Keyword Arguments:
            angle {float} -- [description] (default: {180})
            external {bool} -- [description] (default: {False})
            chamber {str} -- [description] (default: {"top"})

        Raises:
            ValueError -- [description]
            ConstraintError -- [description]

        Returns:
            None
        """

        # TODO: call super after testing if height for input is valid

        if name == "default" and self._type_bottom in self.BOTTOMS_PIPE:
            raise ValueError("Reactor already has an output called 'default'")

        # Get the height of the bottom
        h_bottom, _ = self._calculateHBottom()

        # If diameter is none, set diameter according to external/internal I/O
        if diameter is None and not external:
            diameter = cst.D_CAN
        elif diameter is None and external:
            diameter = cst.D_EXT_INLET

        # Calculate minimum and maximum heights for bottom
        min_h1 = h_bottom + diameter / 2
        max_h1 = self._z_filter - diameter / 2

        # Calculate minimum and maximum heights for top
        min_h2 = self._z_filter + self._h_filter + diameter / 2

        # max height depends on type of reactor
        if self._type_top in self.CLOSED_TOPS:
            max_h2 = h_bottom + self._h - diameter / 2
        else:
            max_h2 = h_bottom + self._h - diameter / 2 - self._walls

        if not (height >= min_h1 and height <= max_h1) and not (
            height >= min_h2 and height <= max_h2
        ):

            mes = f"Input's h must be between {min_h1} and {max_h1} or "
            mes += f"between {max_h1} and {max_h2}"

            raise ConstraintError(mes)

        # Try to update the IO object if it exists, or
        # Create an OutputObject and put it in the dic of inputs
        try:
            self.outputs[name].height = height
            self.outputs[name].diameter = diameter
            self.outputs[name].angle = angle
            self.outputs[name].external = external
            self.outputs[name].chamber = chamber
        except KeyError:
            self.outputs[name] = InputOutput(height, diameter, angle, external, chamber)

    def addInputPercentageBottom(
        self,
        name: str,
        height_per: float = 100,
        angle: float = 180,
        diameter: Optional[float] = None,
        external: bool = False,
    ) -> None:

        """
        Add an input to the reactor, under the filter
        - height_per: percentage, from 0 to 100 of available height (under
          filter)
        - angle: angle of input, start from x-axis, trigonometric rotation
        - diameter: diameter of input

        Arguments:
            name {str} -- [description]

        Keyword Arguments:
            height_per {float} -- [description] (default: {100})
            angle {float} -- [description] (default: {180})
            diameter {Optional[float]} -- [description] (default: {None})
            external {bool} -- [description] (default: {False})

        Raises:
            ValueError -- [description]

        Returns:
            None
        """

        simple_angle = misc.simplifyAngle(angle)

        # Crash if invalid value for input's height
        if height_per < 0 or height_per > 100:
            raise ValueError("Height % must be >=0 and <=100")

        # Get the height of the bottom
        h_bottom, _ = self._calculateHBottom()

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
        max_h = self._z_filter - diameter_nbr / 2

        # Convert the height from percentage to mm
        real_h = height_per * (max_h - min_h) / 100 + min_h

        # If height is out of range, set it to limit
        # Avoids rounding errors
        if real_h < min_h:
            real_h = min_h
        elif real_h > max_h:
            real_h = max_h

        self._addInput(name, real_h, diameter_nbr, simple_angle, external, "bottom")

    def addInputPercentageTop(
        self,
        name: str,
        height_per: float = 100,
        angle: float = 180,
        diameter: Optional[float] = None,
        external: bool = False,
    ) -> None:

        """
        Add an input to the reactor, above the filter
        - height_per: percentage, from 0 to 100 of available height (above
          filter)
        - angle: angle of input, start from x-axis, trigonometric rotation
        - diameter: diameter of input

        Arguments:
            name {str} -- [description]

        Keyword Arguments:
            height_per {float} -- [description] (default: {100})
            angle {float} -- [description] (default: {180})
            diameter {Optional[float]} -- [description] (default: {None})
            external {bool} -- [description] (default: {False})

        Raises:
            ValueError -- [description]

        Returns:
            None
        """

        simple_angle = misc.simplifyAngle(angle)

        # Crash if invalid value for input's height
        if height_per < 0 or height_per > 100:
            raise ValueError("Height % must be >=0 and <=100")

        # Get the height of the bottom
        h_bottom, _ = self._calculateHBottom()

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
        # add cst.F here to avoid non-manifold. Weird, but only needed in this
        # function.
        min_h = self._z_filter + self._h_filter + diameter_nbr / 2 + cst.F

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

        self._addInput(name, real_h, diameter_nbr, simple_angle, external, "top")

    def addOutputPercentageBottom(
        self,
        name: str,
        height_per: float = 100,
        diameter: Optional[float] = None,
        angle: float = 180,
        external: bool = False,
    ) -> None:

        """
        Add an output to the reactor, under the filter
        - height_per: percentage, from 0 to 100 of available height (under
          filter)
        - angle: angle of input, start from x-axis, trigonometric rotation
        - diameter: diameter of input

        Arguments:
            name {str} -- [description]

        Keyword Arguments:
            height_per {float} -- [description] (default: {100})
            diameter {Optional[float]} -- [description] (default: {None})
            angle {float} -- [description] (default: {180})
            external {bool} -- [description] (default: {False})

        Raises:
            ValueError -- [description]

        Returns:
            None
        """

        simple_angle = misc.simplifyAngle(angle)

        # Crash if invalid value for input's height
        if height_per < 0 or height_per > 100:
            raise ValueError("Height % must be >=0 and <=100")

        # Get the height of the bottom
        h_bottom, _ = self._calculateHBottom()

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
        max_h = self._z_filter - diameter_nbr / 2

        # Convert the height from percentage to mm
        real_h = height_per * (max_h - min_h) / 100 + min_h

        # If height is out of range, set it to limit
        # Avoids rounding errors
        if real_h < min_h:
            real_h = min_h
        elif real_h > max_h:
            real_h = max_h

        self._addOutput(name, real_h, diameter_nbr, simple_angle, external, "bottom")

    def addOutputPercentageTop(
        self,
        name: str,
        height_per: float = 100,
        angle: float = 180,
        diameter: Optional[float] = None,
        external: bool = False,
    ) -> None:

        """
        Add an output to the reactor, above the filter
        - height_per: percentage, from 0 to 100 of available height (above
          filter)
        - angle: angle of input, start from x-axis, trigonometric rotation
        - diameter: diameter of input

        Arguments:
            name {str} -- [description]

        Keyword Arguments:
            height_per {float} -- [description] (default: {100})
            angle {float} -- [description] (default: {180})
            diameter {Optional[float]} -- [description] (default: {None})
            external {bool} -- [description] (default: {False})

        Raises:
            ValueError -- [description]

        Returns:
            None
        """

        simple_angle = misc.simplifyAngle(angle)

        # Crash if invalid value for input's height
        if height_per < 0 or height_per > 100:
            raise ValueError("Height % must be >=0 and <=100")

        # Get the height of the bottom
        h_bottom, _ = self._calculateHBottom()

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
        # add cst.F here to avoid non-manifold. Weird, but only needed in this
        # function.
        min_h = self._z_filter + self._h_filter + diameter_nbr / 2 + cst.F

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

        self._addOutput(name, real_h, diameter_nbr, simple_angle, external, "top")

    def expandVertically(self, value: float) -> None:

        """
        Use this method to expand the reactor vertically by a certain value
        (mm). Will modify _h and recalculate the volume. This method can
        be used to align the top of the reactor to another reactor top.
        Negative values can also be used. It will shorten the reactor's body

        Reimplemented from base class to account for 'expand_strategy'. Top
        OR bottom chambers can be expanded

        Arguments:
            value {float} -- [description]

        Returns:
            None
        """

        # Here getHeightPercentage will return the percentage according to
        # the chamber (top or bottom)
        old_in_per = [self.getHeightPercentage(io) for io in self.inputs.values()]

        old_out_per = [self.getHeightPercentage(io) for io in self.outputs.values()]

        # Calculate the change in volume
        expanding_volume = np.pi * self._r ** 2 * value / 1000

        # Add the expanding volume to one of the chamber, depending on
        # 'expand_strategy'
        if self.expand_strategy == "expand_top":
            self.volume_top += expanding_volume
        elif self.expand_strategy == "expand_bottom":
            self.volume_bottom += expanding_volume

        # I/Os were created with % of height. Height just changed, so get
        # old percentages and replace input to same percentages of new height
        for old_per, dict_data in zip(old_in_per, self.inputs.items()):
            name, io = dict_data

            if io.chamber == "top":
                self.addInputPercentageTop(
                    name,
                    height_per=old_per,
                    angle=io.angle,
                    diameter=io.diameter,
                    external=io.external,
                )

            elif io.chamber == "bottom":
                self.addInputPercentageBottom(
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

            # Pass for default output
            if name == "default":
                continue

            if io.chamber == "top":
                self.addOutputPercentageTop(
                    name,
                    height_per=old_per,
                    angle=io.angle,
                    diameter=io.diameter,
                    external=io.external,
                )

            elif io.chamber == "bottom":
                self.addOutputPercentageTop(
                    name,
                    height_per=old_per,
                    angle=io.angle,
                    diameter=io.diameter,
                    external=io.external,
                )

    def _findHeightRadius(self) -> Tuple[float, float]:

        """
        Find the height (of the straight part of the body) of the reactor.
        r is dependent on the radius of the filter and is explicitely
        calculated

        NOTE: volume of pipes is neglected

        Returns:
            Tuple[float, float] -- [description]
        """

        volume = self._volume_bottom + self._volume_top

        # Calculate possible outside radius, based on the filter. Radius is
        # radius of the filter + tolerance for filter - length to secure filter
        r = self._d_filter / 2 + cst.OFF_FILTER / 2 - cst.SECURE_D_FILTER
        # if user radius for internal is bigger, take it, otherwise use based on filter
        r = max(r, self._r_int)

        if self.r_constrained:
            r_int = self._r_int
        else:
            r_int = r

        if self._type_bottom in self.FLAT_BOTS and self._type_top in self.OPEN_TOPS:

            h = (volume + np.pi * r_int ** 2 * self._h_filter) / (np.pi * r_int ** 2)

        # Both top and bottom are round, add volume of sphere
        elif (
            self._type_bottom in self.ROUND_BOTS and self._type_top in self.CLOSED_TOPS
        ):

            # Calculate h based on r
            h = (volume + np.pi * r_int ** 2 * self._h_filter - 4 / 3 * np.pi * r_int ** 3) / (
                np.pi * r_int ** 2
            )

        # Only top OR bottom is round, add hemisphere to volume
        else:
            # Calculate h based on r
            h = (volume + np.pi * r_int ** 2 * self._h_filter - 2 / 3 * np.pi * r_int ** 3) / (
                np.pi * r_int ** 2
            )

        # Refresh filter's height. The CAD code will use this new value
        # _findZFilter uses the volumes of the chamber to find the filter's
        # height
        try:
            self._z_filter = self._findZFilter()
        except AttributeError:
            pass

        return h, r

    def _findZFilter(self) -> float:

        """
        Find the absolute height (z) of the BOTTOM of the filter

        Returns:
            float -- [description]
        """

        # TODO: add test for this method

        if not self.r_constrained:
            r_int = self._r 
        else:
            r_int = self._r_int

        if self._type_bottom in self.ROUND_BOTS:
            z_filter = (self._volume_bottom - 2 / 3 * r_int) / (np.pi * r_int ** 2)
            z_filter -= r_int/2
        else:
            z_filter = self._volume_bottom / (np.pi * r_int ** 2)

        h_bottom, _ = self._calculateHBottom()
        z_filter += h_bottom

        # Add eventual z translation
        z_filter += self.coo["z"]

        return z_filter

    def _buildInputOutputTube(self, entry: InputOutput) -> s.objects.rotate:

        """
        Build the tube for an input or output from an InputOutput object, if
        it's external. Re-implemented from base class to make sure the tube
        won't collide with the filter.

        Arguments:
            entry {InputOutput} -- [description]

        Raises:
            ConstraintError -- [description]

        Returns:
            s.objects.rotate -- [description]
        """

        max_offset = self._walls - cst.SECURE_D_FILTER

        # Outside radius
        r_ex = self._r + self._walls

        # Width of tube
        width = entry.diameter + 2 * self._walls

        # Calculate offset to correctly merge tube with reactor
        offset = r_ex - np.sqrt(r_ex ** 2 - (width / 2) ** 2)

        # TODO: test exception is raised if input is too big
        if offset > max_offset:
            mes = "This I/O is too big for this reactor. "
            mes += f"Maybe increase wall thickness by {offset - max_offset}?"
            raise ConstraintError(mes)

        return super()._buildInputOutputTube(entry)

    def _buildBody(self) -> s.objects.difference:

        """
        Build the body of the reactor

        Returns:
            s.objects.difference -- [description]
        """

        # if not constrained, then it will be based on filter
        # otherwise, based on user input
        if not self.r_constrained:
            r_int = self._r 
        else:
            r_int = self._r_int

        # Calculate outside radius of cylinder based on filter radius
        filter_rad = self._d_filter / 2 + cst.OFF_FILTER / 2 - cst.SECURE_D_FILTER
        # take max between filter radius and user internal radius
        r_out = max(r_int, filter_rad)

        # Build the body: a simple pipe
        # cst.F to avoid non-manifold surfaces with the top and the bottom
        outer = s.cylinder(r=r_out + self._walls, h=self._h + 2 * cst.F)
        outer = su.down(cst.F)(outer)

        # Maker inner cylinder taller by 2 * cst.F to avoid display bug in
        # openscad
        inner = s.cylinder(r=r_int, h=self._h + 4 * cst.F)
        inner = su.down(2 * cst.F)(inner)

        h_bottom, _ = self._calculateHBottom()

        # Filter bigger than internal radius, then just make a cylinder
        # This is the original way JP was doing this
        if filter_rad == r_out:
            fil = s.cylinder(r=(self._d_filter + cst.OFF_FILTER) / 2, 
                h=self._h_filter)
            fil = su.up(self._z_filter - h_bottom)(fil)
            body = outer - inner - fil
        else: # internal radius bigger than filter, we need extra structure
            out_fil = s.cylinder(r=r_out, h=self._h_filter*2)
            out_fil = su.up(self._z_filter - h_bottom - self._h_filter)(out_fil)
            inout = s.cylinder(r=(self._d_filter - cst.OFF_FILTER*2) / 2, 
                h=self._h_filter*2)
            inout = su.up(self._z_filter - h_bottom - self._h_filter)(inout)
            disk = s.cylinder(r=(self._d_filter + cst.OFF_FILTER) / 2, 
                h=self._h_filter)
            disk = su.up(self._z_filter - h_bottom - self._h_filter*0.5)(disk)
            fil = out_fil-inout-disk
            body = outer - inner + fil - disk

        return body
