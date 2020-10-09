#!/usr/bin/python
# coding: utf-8

import solid as s
import solid.utils as su
import numpy as np
from scipy.optimize import fsolve
from typing import Tuple, Dict, Union
import warnings

from . import misc
from . import constants as cst
from .exceptions import *
from .pipe import BentPipeCAD
from .filter_like_reactors import FilterLikeReactor
from .in_out import InputOutput
from .top_in import TopInlet


class FilterReactorCAD(FilterLikeReactor):

    """Class for reactor with filter at the bottom. The filter doesn't move"""

    BOTTOMS = [
        FilterLikeReactor.B_ROUND_EX_O,
        FilterLikeReactor.B_ROUND_IN_O,
        FilterLikeReactor.B_FLAT,
        FilterLikeReactor.B_FLAT_EX_O,
        FilterLikeReactor.B_FLAT_IN_O,
    ]

    ALIGN_FILTER_STRATEGIES = ["Lift reactor", "Adapt"]

    def __init__(
        self,
        volume: float,
        type_top: str,
        type_bottom: str,
        d_filter: float,
        h_filter: float,
        def_out_angle: float = 0,
        *args,
        **kwargs,
    ) -> None:

        """
        Volume is in mL, and will be converted to mm3. type_top and type_bottom should
        be strings enumerated in reactor.py. d_filter and h_filter are the diameter
        and height of the filter, respectively. def_out_angle is the angle for the
        default output (trigonometric direction). The filter is part of the bottom
        (not of the body like in FloatingFilterReactorCAD)

        Arguments:
            volume {float}: volume of the reactor
            type_top {str}: type of top
            type_bottom {str}: type of bottom
            d_filter {float}: filter's diameter
            h_filter {float}: filter's thickness
            def_out_angle {float}: angle for default output (default: {0})

        Raises:
            NotImplementedError: when type bottom is round

        Returns:
            None
        """

        # Name/module type, used by GUI to connect slot and signals
        # Annotated in ObjectCAD
        self.module_type = "Filter reactor"
        self.module_type_short = "FR"

        # Bool to check if r is constrained
        self.r_constrained = False

        # Bool to check if top is aligned
        self.top_aligned = False

        self._type_top = type_top
        self._type_bottom = type_bottom

        # Round bottom with filter, no output, not implemented yet (not sure
        # it would be useful)
        if self._type_bottom == self.B_ROUND:
            mes: str = "FilterReactorCAD: round bottom with filter not possible"
            raise NotImplementedError(mes)

        # Handle threaded tops (r is constrained)
        super()._handleThreadedTops()

        # Filter's dimensions
        # Annotated in base class
        self._d_filter = d_filter
        self._h_filter = h_filter

        # Bool for bottom strategies: is filter too small ?
        self._filter_too_small: bool = False

        # Translations to apply before generating CAD code
        # Will be modified by connectors
        # Annotated in ReactorCAD
        self.coo: Dict[str, float] = {"x": 0, "y": 0, "z": 0, "angle": 0}

        # Check input volume is valid
        self._checkVolume(volume)

        # Don't use the volume property, instead assign internal attribute
        # Do that to explicitely declare _h and _r in init
        self._volume = volume * 1000

        # Find reactor's dimensions
        self._h, self._r = self._findHeightRadius()

        self._handleExtraArgs(kwargs)

        self.inputs: Dict[str, InputOutput] = dict()
        self.outputs: Dict[str, InputOutput] = dict()
        self.top_inlets: Dict[str, TopInlet] = dict()

        # Angle for the output, starting from x axis, clockwise
        self._def_out_angle = misc.simplifyAngle(def_out_angle)

        self._buildDefOutput()

    def _handleExtraArgs(self, kwargs: dict) -> None:

        """
        Handle extra arguments passed to the init function

        Arguments:
            kwargs {dict}: [description]

        Returns:
            None
        """
        super()._handleExtraArgs(kwargs)

        # Strategies to align the top of the filter
        # Possible values:
        # - lift: valid only if top is not aligned. Lift the entire reactor
        # to align filter
        # - adapt: move the filter to align it, and will keep the top
        # unchanged (wherever it is). The body will be extended/shortened to
        # do so
        self.align_filter_strategy: str = "lift"

    @property
    def d_filter(self) -> float:

        """
        Return filter's diameter

        Returns:
            float
        """

        return self._d_filter

    @d_filter.setter
    def d_filter(self, value: float) -> None:

        """
        Check and set filter's diameter. Refresh reactor's dimensions

        Arguments:
            value {float}: desired filter's diameter

        Returns:
            None
        """

        self._d_filter = value

        # Refresh dimensions
        self._h, self._r = self._findHeightRadius()

    @property
    def h_filter(self) -> float:

        """
        Return filter's height

        Returns:
            float
        """

        return self._h_filter

    @h_filter.setter
    def h_filter(self, value: float) -> None:

        """
        Check and set filter's height. Refresh reactor's dimensions

        Arguments:
            value {float}: desired thickness for the filter

        Returns:
            None
        """

        self._h_filter = value

        # Refresh dimensions
        self._h, self._r = self._findHeightRadius()

    @property
    def infos(self) -> Dict[str, Union[str, float]]:

        """
        Return infos about the reactor. Subclassed from base class to add specific
        infos about the filter

        Returns:
            Dict[str, Union[str, float]]
        """
        # Get infos from parent method
        infos: Dict[str, Union[str, float]] = super()._getInfos()

        # Add infos to dict
        infos["z_top_filter"] = self.z_top_filter
        infos["z_bottom_filter"] = self.z_bottom_filter
        infos["h_filter"] = self._h_filter
        infos["d_filter"] = self._d_filter
        infos["filter_too_small"] = self._filter_too_small
        infos["align_filter_strategy"] = self.align_filter_strategy

        return infos

    def alignFilterToHeight(self, target_height: float) -> None:

        """
        Align the filter to 'target_height', depending on strategy. Keep
        top aligned if needed

        Arguments:
            target_height {float}: target height to align filter on

        Raises:
            IncompatibilityError: when align_top_strategy and align_filter_strategy are
                                  both 'lift'
            ImpossibleAction: when top is lower than target filter and
                              align_filter_strategy is 'adapt'

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

        # All these cases are treated the same. Align the filter. Keep top
        # unchanged (it stays aligne if it was)
        elif (
            self.align_filter_strategy == "adapt"
            or (
                self.align_top_strategy == "expand"
                and self.align_filter_strategy == "lift"
            )
            or (
                self.align_top_strategy == "lift"
                and self.align_filter_strategy == "adapt"
            )
        ):

            # Distance to expand
            diff = self.z_top_filter - target_height

            # Reset reactor's z
            self.liftReactor(0)
            try:
                self.expandVertically(diff)
            except ValueError:
                mes = "Can't align filter with 'adapt' strategy. Top is"
                mes = mes + " probably lower than target filter"
                raise ImpossibleAction(mes)

            # Lift reactor to align filter
            self.liftReactor(target_height - self.z_top_filter)

    def _findHeightRadius(self) -> Tuple[float, float]:

        """
        Find the radius and the height (of the straight part of the body)
        of the reactor.

        NOTE: volume of pipes is neglected

        Returns:
            Tuple[float, float]: (h, r)
        """

        # Calculate r and h differently, if r is constrained or not
        if self.r_constrained:
            h, r = self._findHeightRadiusRConstrained()
        else:
            h, r = self._findHeightRadiusRNotConstrained()

        return h, r

    def _findHeightRadiusRNotConstrained(self) -> Tuple[float, float]:

        """
        Find r and h if r is not constrained. First try to calculate them assuming
        filter's radius is big enough for the required volume. If not, calculate it
        with a more complicated strategy (optimization instead of simple calculation)

        Raises:
            ImpossibleAction: when volume is too small for round bottom

        Returns:
            Tuple[float, float]: (h, r)
        """

        # Calculate r and h assuming filter's radius is big enough
        h, r = self._calHeightRadiusAssumeFilterBigEnough()

        # if ratio h/r > 2 * golden ratio, then the filter is too small and we
        # adapt strategy for bottom: it will be built differently
        ratio = h / (2 * r)
        if ratio > 2 * cst.PHI:
            warnings.warn("Filter too small. Adapting strategy for bottom")
            self._filter_too_small = True

            # Reduce the thickness of the walls when filter is too small:
            # It's not merged in the walls so no need for thick walls
            self._walls = cst.WALLS

            warnings.warn(
                f"Walls set to {self.walls} mm bc filter not fused in the walls"
            )

            h, r = self._calHeightRadiusFilterTooSmallRNotConstrained()

        else:
            self._filter_too_small = False

            # TODO: check exception is raised in tests

            # Raise exception is filter is big enough and user tries to
            # use a round bottom (it would make no sense)
            if self._type_bottom in self.ROUND_BOTS:
                mes: str = "FilterReactorCAD: volume too small for round bottom"
                raise ImpossibleAction(mes)

        return h, r

    def _calHeightRadiusAssumeFilterBigEnough(self) -> Tuple[float, float]:

        """
        Calculate h assuming the filter is big enough for the required volume (r of
        the reactor will be calculated based on filter's radius)

        Returns:
            Tuple[float, float]: (h, r)
        """

        # Calculate the radius, it's fixed bc of the filter
        r = self._d_filter / 2 + cst.OFF_FILTER / 2 - cst.SECURE_D_FILTER

        if self._type_top in self.OPEN_TOPS:

            # Calculate h based on r
            h = (self._volume + np.pi * r ** 2 * self._h_filter) / (np.pi * r ** 2)

        # Top is round
        elif self._type_top in self.CLOSED_TOPS:

            # Calculate h based on r
            h = (
                self._volume + np.pi * r ** 2 * self._h_filter - 2 / 3 * np.pi * r ** 3
            ) / (np.pi * r ** 2)

        return h, r

    def _calHeightRadiusFilterTooSmallRNotConstrained(self) -> Tuple[float, float]:

        """
        Calculate h and r in case filter is too small and r is not constrained

        Returns:
            Tuple[float, float]: (h, r)
        """

        # Minimum radius of the cartridge, where the cut sphere meets the
        # filter (theoretically, without accounting for offsets)
        r_min = self._d_filter / 2 + cst.OFF_FILTER / 2 - cst.SECURE_D_FILTER

        def eq_volume(var: tuple) -> Tuple[float, float]:

            """
            Calculate the volume of the reactor, conditionally. h is the height of
            the body, r the radius of the inside body (i.e.: walls not acounted for)

            https://en.wikipedia.org/wiki/Spherical_cap

            Arguments:
                var {tuple}: (h, r)

            Returns:
                Tuple[float, float]: (h, r)
            """

            h, r = var

            # Calculate how far we are to reach golden ratio
            phi_eq = cst.PHI - h / (2 * r)

            if self._type_bottom in self.FLAT_BOTS:
                # Volume of spacer (maintains the filter)
                V_spacer = np.pi * r_min ** 2 * cst.SECURE_H_FILTER_TOP

                V_eq = self._volume - np.pi * r ** 2 * h - V_spacer

            elif self._type_bottom in self.ROUND_BOTS:
                h_cut_sphere = np.sqrt(r ** 2 - r_min ** 2)
                h_cut_sphere = r - h_cut_sphere

                # Calculate the volume of the cut sphere at the bottom of the
                # reactor
                V_hemisphere = 2 / 3 * np.pi * r ** 3
                V_cap = (np.pi * h_cut_sphere ** 2 / 3) * (3 * r - h_cut_sphere)
                V_cut_sphere = V_hemisphere - V_cap

                # Calculate how far we are to reach target volume
                V_eq = self._volume - np.pi * r ** 2 * h - V_cut_sphere

            # If closed top, substract volume of hemisphere
            if self._type_top in self.CLOSED_TOPS:
                V_eq -= 2 / 3 * np.pi * r ** 3

            return (V_eq, phi_eq)

        # Find h and r. Always start with an estimate of 10 and 10 mm, should
        # always work
        h, r = fsolve(eq_volume, (10, 10))

        return h, r

    def _findHeightRadiusRConstrained(self) -> Tuple[float, float]:

        """
        Find h if radius is constrained. First check if constrained radius is not too
        small. If it's big enough, calculate h (optimization, not simple calculation)

        Raises:
            ConstraintError: when constrained radius is too small

        Returns:
            Tuple[float, float]: (h, r)
        """

        # Calculate theoretical radius based on filter's radius (minimum
        # radius)
        h, r = self._calHeightRadiusAssumeFilterBigEnough()

        # If constrained radius is smaller than min radius, crash
        if self._r < r:
            raise ConstraintError(f"Constrained radius too small. Must be > {r}")
        # If constrained radius is equal to min radius (how lucky), keep
        # h and r previously calculated
        elif self._r == r:
            h, r = h, r

        # Calculate h the hard way
        else:
            h, r = self._calHeightRadiusRConstrained()

        return h, r

    def _calHeightRadiusRConstrained(self) -> Tuple[float, float]:

        """
        Calculate h in case the radius is constrained

        Raises:
            ConstraintError: when constrained r is too big

        Returns:
            Tuple[float, float]: (h, r)
        """

        # Minimum radius of the cartridge, where the cut sphere meets the
        # filter (theoretically, without accounting for offsets)
        r_min = self._d_filter / 2 + cst.OFF_FILTER / 2 - cst.SECURE_D_FILTER

        # Flat bottom, no top
        if self._type_bottom in self.FLAT_BOTS and self._type_top in self.OPEN_TOPS:

            # Volume of spacer (maintains the filter)
            V_spacer = np.pi * r_min ** 2 * cst.SECURE_H_FILTER_TOP

            h = (self._volume - V_spacer) / (np.pi * self._r ** 2)

        # Flat bottom, closed top
        elif self._type_bottom in self.FLAT_BOTS and self._type_top in self.CLOSED_TOPS:

            # Volume of spacer (maintains the filter)
            V_spacer = np.pi * r_min ** 2 * cst.SECURE_H_FILTER_TOP

            h = (self._volume - V_spacer - 2 / 3 * np.pi * self._r ** 3) / (
                np.pi * self._r ** 2
            )

        # Round bottom with cut sphere, all cases (no top, closed top)
        elif self._type_bottom in self.ROUND_BOTS:

            h_cut_sphere = np.sqrt(self._r ** 2 - r_min ** 2)
            h_cut_sphere = self._r - h_cut_sphere

            # Calculate the volume of the cut sphere at the bottom of the
            # reactor
            V_hemisphere = 2 / 3 * np.pi * self._r ** 3
            V_cap = (np.pi * h_cut_sphere ** 2 / 3) * (3 * self._r - h_cut_sphere)

            V_cut_sphere = V_hemisphere - V_cap

            if self._type_top in self.OPEN_TOPS:
                h = (self._volume - V_cut_sphere) / (np.pi * self._r ** 2)

            elif self._type_top in self.CLOSED_TOPS:
                h = (self._volume - V_cut_sphere - 2 / 3 * np.pi * self._r ** 3) / (
                    np.pi * self._r ** 2
                )

        if h <= 0:
            raise ConstraintError("Constrained r too big")

        return h, self._r

    def _findZFilter(self) -> float:

        """
        Find the absolute height (z) of the bottom of the filter

        Returns:
            float
        """

        # TODO: add test for this method
        h_bottom = self._calculateHBottom()[0]

        # Flat bottom, so top of the filter is flush with top of bottom
        if self._type_bottom in self.FLAT_BOTS:
            z = h_bottom - self._h_filter

            # If filter is too small and bottom is flat, filter is not
            # flush with bottom of reactor. Substract height of matter on
            # top of the filter
            if self._filter_too_small:
                z -= cst.SECURE_H_FILTER_TOP

        # Round bottoms, with cut sphere
        elif self._type_bottom in self.ROUND_BOTS:
            r_min = self._d_filter / 2 + cst.OFF_FILTER / 2 - cst.SECURE_D_FILTER
            h_cut_sphere = np.sqrt(self._r ** 2 - r_min ** 2)
            z = h_bottom - h_cut_sphere - self._h_filter

        # Add eventual z translation
        z += self.coo["z"]

        return z

    def _calculateHBottom(self) -> Tuple[float, float]:

        """
        Calculate height of the bottom, and the vertical offset in case there is an
        external adaptor

        Returns:
            Tuple[float, float]: (h_bottom, offset)
        """

        h_bottom: float = 0
        offset_ext_inlet: float = 0

        # Simple flat bottom. Not really useful as there is no outlet...
        if self._type_bottom == self.B_FLAT:

            h_bottom = self._walls + self._h_filter

            if self._filter_too_small:
                h_bottom += cst.SECURE_H_FILTER_TOP

        # Flat bottom w/ internal inlet
        elif self._type_bottom == self.B_FLAT_IN_O:

            h_bottom = self._d_can + 2 * self._walls + self._h_filter
            if self._filter_too_small:
                h_bottom += cst.SECURE_H_FILTER_TOP

        # Flat bottom w/ external inlet
        elif self._type_bottom == self.B_FLAT_EX_O:

            # Difference between B_ROUND_EX_O and B_ROUND_IN_O is external
            # inlet. Parts have to be offseted vertically.
            # Calculate this offset
            offset_ext_inlet = (cst.D_EXT_INLET - self._d_can) / 2

            h_bottom = self._d_can + 2 * self._walls + offset_ext_inlet + self._h_filter

        elif self._type_bottom == self.B_ROUND_IN_O:

            # Minimum radius of the cartridge, where the cut sphere meets the
            # filter (theoretically, without accounting for offsets)
            r_min = self._d_filter / 2 + cst.OFF_FILTER / 2 - cst.SECURE_D_FILTER
            h_cut_sphere = np.sqrt(self._r ** 2 - r_min ** 2)
            h_bottom = h_cut_sphere + self._h_filter + self._d_can + 2 * self._walls

        elif self._type_bottom == self.B_ROUND_EX_O:

            # Minimum radius of the cartridge, where the cut sphere meets the
            # filter (theoretically, without accounting for offsets)
            r_min = self._d_filter / 2 + cst.OFF_FILTER / 2 - cst.SECURE_D_FILTER

            h_cut_sphere = np.sqrt(self._r ** 2 - r_min ** 2)

            # Difference between B_ROUND_EX_O and B_ROUND_IN_O is external
            # inlet. Parts have to be offseted vertically.
            # Calculate this offset
            offset_ext_inlet = (cst.D_EXT_INLET - self._d_can) / 2

            h_bottom = (
                h_cut_sphere
                + self._h_filter
                + self._d_can
                + 2 * self._walls
                + offset_ext_inlet
            )

        return h_bottom, offset_ext_inlet

    def _buildBottom(self) -> s.objects.difference:

        """
        Build the bottom of the reactor (pipe, outlets and everything).
        Use smaller functions to build the different types of bottom.

        Returns:
            s.objects.difference: cad object for the bottom
        """

        # Simple flat bottom
        if self._type_bottom == self.B_FLAT:
            bottom = self._buildFlatBottom()

        # Flat bottom w/ internal outlet
        elif self._type_bottom == self.B_FLAT_IN_O:
            bottom = self._buildFlatBottomInO()

        # Flat bottom w/ external outlet
        elif self._type_bottom == self.B_FLAT_EX_O:
            bottom = self._buildFlatBottomExO()

        # Round bottom w/ internal outlet
        elif self._type_bottom == self.B_ROUND_IN_O:
            bottom = self._buildRoundBottomInO()

        # Round bottom with external outlet
        elif self._type_bottom == self.B_ROUND_EX_O:
            bottom = self._buildRoundBottomExO()

        return bottom

    def _buildFlatBottom(self) -> s.objects.difference:

        """
        Build simple flat bottom. This case is not really useful

        Returns:
            s.objects.difference: cad object for the bottom
        """

        # Calculate the height of the bottom, to offset the body and the top,
        # so very bottom of reactor starts at z=0
        h_bottom, offset_ext_inlet = self._calculateHBottom()

        # Main bottom cylinder
        bottom = s.cylinder(r=self._r + self._walls, h=h_bottom)

        # Build the filter space
        filter_space = s.cylinder(
            r=self._d_filter / 2 + cst.OFF_FILTER / 2, h=self._h_filter
        )

        if not self._filter_too_small:
            filter_space = su.up(h_bottom - self._h_filter)(filter_space)
        else:
            # Create a spacer to print on top of the filter, to maintain it
            spacer = s.cylinder(
                r=self._d_filter / 2 + cst.OFF_FILTER / 2 - cst.SECURE_D_FILTER,
                h=cst.SECURE_D_FILTER,
            )
            spacer = su.up(h_bottom - cst.SECURE_D_FILTER)(spacer)
            bottom -= spacer

            filter_space = su.up(h_bottom - self._h_filter - cst.SECURE_H_FILTER_TOP)(
                filter_space
            )

        bottom -= filter_space

        return bottom

    def _buildFlatBottomInO(self) -> s.objects.difference:

        """
        Build flat bottom with internal outlet

        Returns:
            s.objects.difference: cad object for the bottom
        """

        # Calculate the height of the bottom, to offset the body and the top,
        # so very bottom of reactor starts at z=0
        h_bottom, offset_ext_inlet = self._calculateHBottom()

        # Main bottom cylinder
        base = s.cylinder(r=self._r + self._walls, h=h_bottom)

        # Build the filter space
        filter_space = s.cylinder(
            r=self._d_filter / 2 + cst.OFF_FILTER / 2, h=self._h_filter
        )

        if not self._filter_too_small:
            filter_space = su.up(h_bottom - self._h_filter)(filter_space)
        else:
            # Create a spacer to print on top of the filter, to maintain it
            spacer = s.cylinder(
                r=self._d_filter / 2 + cst.OFF_FILTER / 2 - cst.SECURE_D_FILTER,
                h=cst.SECURE_D_FILTER,
            )
            spacer = su.up(h_bottom - cst.SECURE_D_FILTER)(spacer)
            base -= spacer

            filter_space = su.up(h_bottom - self._h_filter - cst.SECURE_H_FILTER_TOP)(
                filter_space
            )

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
        pipe = su.rotate([0, 0, self.def_out_angle])(pipe)
        h_tube = su.rotate([0, 0, self.def_out_angle])(h_tube)

        bottom = base - joint - pipe - h_tube - filter_space

        return bottom

    def _buildFlatBottomExO(self) -> s.objects.difference:

        """
        Build flat bottom with external outlet

        Returns:
            s.objects.difference: cad object for the bottom
        """

        # Calculate the height of the bottom, to offset the body and the top,
        # so very bottom of reactor starts at z=0
        h_bottom, offset_ext_inlet = self._calculateHBottom()

        # Main bottom cylinder
        base = s.cylinder(r=self._r + self._walls, h=h_bottom)

        # Build the filter space
        filter_space = s.cylinder(
            r=self._d_filter / 2 + cst.OFF_FILTER / 2, h=self._h_filter
        )

        if not self._filter_too_small:
            filter_space = su.up(h_bottom - self._h_filter)(filter_space)
        else:
            # Create a spacer to print on top of the filter, to maintain it
            spacer = s.cylinder(
                r=self._d_filter / 2 + cst.OFF_FILTER / 2 - cst.SECURE_D_FILTER,
                h=cst.SECURE_D_FILTER,
            )
            spacer = su.up(h_bottom - cst.SECURE_D_FILTER)(spacer)
            base -= spacer

            filter_space = su.up(h_bottom - self._h_filter - cst.SECURE_H_FILTER_TOP)(
                filter_space
            )

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
        pipe = su.rotate([0, 0, self.def_out_angle])(pipe)
        h_tube = su.rotate([0, 0, self.def_out_angle])(h_tube)
        ex_inlet = su.rotate([0, 0, self.def_out_angle])(ex_inlet)
        flat_surf = su.rotate([0, 0, self.def_out_angle])(flat_surf)

        bottom = base + flat_surf - pipe - joint - h_tube - ex_inlet - filter_space

        return bottom

    def _buildRoundBottomInO(self) -> s.objects.difference:

        """
        Build round bottom with internal outlet

        Returns:
            s.objects.difference: cad object for the bottom
        """

        # Calculate the height of the bottom, to offset the body and the top,
        # so very bottom of reactor starts at z=0
        h_bottom, offset_ext_inlet = self._calculateHBottom()
        print("filter", h_bottom, offset_ext_inlet)

        # Main bottom cylinder
        base = s.cylinder(r=self._r + self._walls, h=h_bottom)

        r_min = self._d_filter / 2 + cst.OFF_FILTER / 2 - cst.SECURE_D_FILTER
        h_cut_sphere = np.sqrt(self._r ** 2 - r_min ** 2)
        print("filter", self._r, r_min, h_cut_sphere)

        sphere = s.sphere(r=self._r)
        sphere = su.up(h_bottom)(sphere)

        sub_base = s.cylinder(r=self._r + self._walls, h=h_bottom - h_cut_sphere)

        # Build the filter space
        filter_space = s.cylinder(
            r=self._d_filter / 2 + cst.OFF_FILTER / 2, h=self._h_filter
        )
        filter_space = su.up(h_bottom - h_cut_sphere - self._h_filter)(filter_space)

        # Joint between bottom of chamber and bent pipe
        # Double length of joint so it pierces the sphere. cst.F to avoid
        # non-manifold surface
        joint = s.cylinder(r=self._d_can / 2, h=self._d_can + cst.F)
        joint = su.up(2 * self._walls + self._d_can / 2 - cst.F)(joint)

        # Bent pipe for siphon. Turns pipe from vertical to horizontal
        pipe = BentPipeCAD(self._d_can, 0, self._walls).cad
        pipe = su.rotate([-90, 0, 180])(pipe)
        pipe = su.up(2 * self._walls + self._d_can / 2)(pipe)
        pipe = su.right(self._walls)(pipe)

        # Horizontal pipe between the bent pipe and the outside of the
        # reactor. cst.F to avoid non manifold surface
        h_tube = s.cylinder(r=self._d_can / 2, h=self._r + cst.F)
        h_tube = su.rotate([0, 90, 0])(h_tube)
        h_tube = su.right(self._walls - cst.F)(h_tube)
        h_tube = su.up(self._walls + self._d_can / 2)(h_tube)

        # Rotate the entire output pipe if an angle is provided for
        # the output
        pipe = su.rotate([0, 0, self.def_out_angle])(pipe)
        h_tube = su.rotate([0, 0, self.def_out_angle])(h_tube)

        bottom = base - sphere + sub_base - joint - pipe - h_tube - filter_space

        return bottom

    def _buildRoundBottomExO(self) -> s.objects.difference:

        """
        Build round bottom with external outlet

        Returns:
            s.objects.difference: cad object for the bottom
        """

        # Calculate the height of the bottom, to offset the body and the top,
        # so very bottom of reactor starts at z=0
        h_bottom, offset_ext_inlet = self._calculateHBottom()

        # Main bottom cylinder
        base = s.cylinder(r=self._r + self._walls, h=h_bottom)

        r_min = self._d_filter / 2 + cst.OFF_FILTER / 2 - cst.SECURE_D_FILTER
        h_cut_sphere = np.sqrt(self._r ** 2 - r_min ** 2)

        sphere = s.sphere(r=self._r)
        sphere = su.up(h_bottom)(sphere)

        sub_base = s.cylinder(r=self._r + self._walls, h=h_bottom - h_cut_sphere)

        # Build the filter space
        filter_space = s.cylinder(
            r=self._d_filter / 2 + cst.OFF_FILTER / 2, h=self._h_filter
        )

        filter_space = su.up(h_bottom - h_cut_sphere - self._h_filter)(filter_space)

        # Joint between bottom of chamber and bent pipe
        # Double length of joint so it pierces the sphere. cst.F to avoid
        # non-manifold surface
        joint = s.cylinder(r=self._d_can / 2, h=self._d_can + cst.F)
        joint = su.up(2 * self._walls + self._d_can / 2 - cst.F + offset_ext_inlet)(
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
        pipe = su.rotate([0, 0, self.def_out_angle])(pipe)
        h_tube = su.rotate([0, 0, self.def_out_angle])(h_tube)
        ex_inlet = su.rotate([0, 0, self.def_out_angle])(ex_inlet)
        flat_surf = su.rotate([0, 0, self.def_out_angle])(flat_surf)

        bottom = (
            base
            + flat_surf
            - sphere
            + sub_base
            - joint
            - pipe
            - h_tube
            - ex_inlet
            - filter_space
        )

        return bottom
