#  Copyright 2017-2020 Reveal Energy Services, Inc 
#
#  Licensed under the Apache License, Version 2.0 (the "License"); 
#  you may not use this file except in compliance with the License. 
#  You may obtain a copy of the License at 
#
#      http://www.apache.org/licenses/LICENSE-2.0 
#
#  Unless required by applicable law or agreed to in writing, software 
#  distributed under the License is distributed on an "AS IS" BASIS, 
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
#  See the License for the specific language governing permissions and 
#  limitations under the License. 
#
# This file is part of Orchid and related technologies.
#

import functools
from typing import Tuple, Union

import toolz.curried as toolz

import orchid.dot_net_dom_access as dna
from orchid.measurement import Measurement
import orchid.native_subsurface_point as nsp
import orchid.native_treatment_curve_facade as ntc
from orchid.net_quantity import as_datetime, as_measurement, convert_net_quantity_to_different_unit, make_measurement
import orchid.reference_origin as oro
import orchid.unit_system as units


class NativeStageAdapter(dna.DotNetAdapter):
    """Adapts a .NET IStage to be more Pythonic."""

    display_stage_number = dna.dom_property('display_stage_number', 'The display stage number for the stage.')
    start_time = dna.transformed_dom_property('start_time', 'The start time of the stage treatment.', as_datetime)
    stop_time = dna.transformed_dom_property('stop_time', 'The stop time of the stage treatment.', as_datetime)
    display_name_with_well = dna.dom_property('display_name_with_well', 'The display stage number including the well')
    cluster_count = dna.dom_property('number_of_clusters', 'The number of clusters for this stage')

    @staticmethod
    def _sampled_quantity_name_curve_map(sampled_quantity_name):
        return {'Pressure': ntc.TREATING_PRESSURE, 'Slurry Rate': ntc.SLURRY_RATE,
                'Proppant Concentration': ntc.PROPPANT_CONCENTRATION}[sampled_quantity_name]

    def _center_location_depth(self, length_unit: Union[units.UsOilfield, units.Metric],
                               depth_datum: oro.DepthDatum) -> Measurement:
        """
        Return the depth of the stage center relative to the specified `depth_datum.`

        Args:
            length_unit: The unit of length for the returned Measurement.
            depth_datum: The reference datum for the depth.
        """
        subsurface_point = self.center_location(length_unit, oro.WellReferenceFrameXy.ABSOLUTE_STATE_PLANE,
                                                depth_datum)
        return subsurface_point.depth

    @functools.lru_cache()
    def center_location(self, in_length_unit: Union[units.UsOilfield, units.Metric],
                        xy_reference_frame: oro.WellReferenceFrameXy,
                        depth_datum: oro.DepthDatum) -> nsp.SubsurfacePoint:
        """
        Return the location of the center of this stage in the `xy_well_reference_frame` using the `depth_datum`
        in the specified unit.

        Args:
            in_length_unit: The unit of length available from the returned value.
            xy_reference_frame: The reference frame for easting-northing coordinates.
            depth_datum: The datum from which we measure depths.

        Returns:
            The `BaseSubsurfacePoint` of the stage center.
        """
        net_subsurface_point = self._adaptee.GetStageLocationCenter(xy_reference_frame.value,
                                                                    depth_datum.value)
        result = nsp.SubsurfacePoint(net_subsurface_point).as_length_unit(in_length_unit)
        return result

    def center_location_easting(self, length_unit: Union[units.UsOilfield, units.Metric],
                                xy_well_reference_frame: oro.WellReferenceFrameXy) -> Measurement:
        """
        Return the easting location of the stage center relative to the specified reference frame in the
        specified unit.

        Args:
            length_unit: An abbreviation of the unit of length for the returned Measurement.
            xy_well_reference_frame: The reference frame defining the origin.

        Returns:
            A measurement.
        """
        result = self.center_location(length_unit, xy_well_reference_frame, oro.DepthDatum.KELLY_BUSHING).x
        return result

    def center_location_northing(self, length_unit: Union[units.UsOilfield, units.Metric],
                                 xy_well_reference_frame: oro.WellReferenceFrameXy) -> Measurement:
        """
        Return the northing location of the stage center in the `xy_well_reference_frame` in the specified unit.

        Args:
            length_unit: The requested resultant length unit.
            xy_well_reference_frame: The reference frame defining the origin.

        Returns:
            A measurement.
        """
        subsurface_point = self.center_location(length_unit, xy_well_reference_frame,
                                                oro.DepthDatum.KELLY_BUSHING)
        return subsurface_point.y

    def center_location_md(self, length_unit: Union[units.UsOilfield, units.Metric]) -> Measurement:
        """
        Return the measured depth of the stage center in project units.

        Args:
            length_unit: The unit of length for the returned Measurement.
        """
        return self._center_location_depth(length_unit, oro.DepthDatum.KELLY_BUSHING)

    def center_location_tvdgl(self, length_unit: Union[units.UsOilfield, units.Metric]) -> Measurement:
        """
        Returns the total vertical depth from ground level of the stage center in project units.

        Args:
            length_unit: The unit of length for the returned Measurement.
        """
        return self._center_location_depth(length_unit, oro.DepthDatum.GROUND_LEVEL)

    def center_location_tvdss(self, length_unit: Union[units.UsOilfield, units.Metric]) -> Measurement:
        """
        Returns the total vertical depth from sea level of the stage center in project units.

        Args:
            length_unit: The unit of length for the returned Measurement.
        """
        return self._center_location_depth(length_unit, oro.DepthDatum.SEA_LEVEL)

    def center_location_xy(self, length_unit: Union[units.UsOilfield, units.Metric],
                           xy_well_reference_frame: oro.WellReferenceFrameXy) -> Tuple[Measurement, Measurement]:
        """
        Return the easting-northing location of the stage center in the `xy_well_reference_frame` in project units.

        Args:
            length_unit: The unit of length for the returned Measurement.
            xy_well_reference_frame: The reference frame defining the origin.

        Returns:
            A tuple
        """
        subsurface_point = self.center_location(length_unit, xy_well_reference_frame,
                                                oro.DepthDatum.KELLY_BUSHING)
        return subsurface_point.x, subsurface_point.y

    def md_top(self, length_unit_abbreviation: str) -> Measurement:
        """
        Return the measured depth of the top of this stage (closest to the well head / farthest from the toe)
        in the specified unit.

        Args:
            length_unit_abbreviation: An abbreviation of the requested resultant length unit.

        Returns;
         The measured depth of the stage top in the specified unit.
        """
        original = self._adaptee.MdTop
        md_top_quantity = convert_net_quantity_to_different_unit(original, length_unit_abbreviation)
        result = as_measurement(md_top_quantity)
        return result

    def md_bottom(self, length_unit_abbreviation):
        """
        Return the measured depth of the bottom of this stage (farthest from the well head / closest to the toe)
        in the specified unit.

        Args:
            length_unit_abbreviation: An abbreviation of the unit of length for the returned Measurement.

        Returns:
             The measured depth of the stage bottom in the specified unit.
        """
        original = self._adaptee.MdBottom
        md_top_quantity = convert_net_quantity_to_different_unit(original, length_unit_abbreviation)
        result = as_measurement(md_top_quantity)
        return result

    def stage_length(self, length_unit_abbreviation: str) -> Measurement:
        """
        Return the stage length in the specified unit.

        Args:
            length_unit_abbreviation: An abbreviation of the unit of length for the returned Measurement.

        Returns:
            The Measurement of the length of this stage.
        """
        length_magnitude = \
            self.md_bottom(length_unit_abbreviation).magnitude - self.md_top(length_unit_abbreviation).magnitude
        result = make_measurement(length_magnitude, length_unit_abbreviation)
        return result

    def treatment_curves(self):
        """
        Returns the dictionary of treatment curves for this treatment_stage.

        Request a specific curve from the dictionary using the constants defined in `orchid`:

        - `PROPPANT_CONCENTRATION`
        - `SLURRY_RATE`
        - `TREATING_PRESSURE`

        Returns:
            The dictionary containing the available treatment curves.
        """
        if not self._adaptee.TreatmentCurves.Items:
            return {}

        def add_curve(so_far, treatment_curve):
            curve_name = self._sampled_quantity_name_curve_map(treatment_curve.sampled_quantity_name)
            treatment_curve_map = {curve_name: treatment_curve}
            return toolz.merge(treatment_curve_map, so_far)

        result = toolz.pipe(self._adaptee.TreatmentCurves.Items,  # start with .NET treatment curves
                            toolz.map(ntc.NativeTreatmentCurveFacade),  # wrap them in a facade
                            # Transform the map to a dictionary keyed by the sampled quantity name
                            lambda cs: toolz.reduce(add_curve, cs, {}))
        return result
