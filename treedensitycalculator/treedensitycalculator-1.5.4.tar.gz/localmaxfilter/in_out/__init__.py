# -*- coding: utf-8 -*-
"""
| ----------------------------------------------------------------------------------------------------------------------
| Date                : March 2019
| Copyright           : © 2019 - 2020 by Tinne Cahy (Geo Solutions) and Ann Crabbé (KU Leuven)
| Email               : acrabbe.foss@gmail.com
| Acknowledgements    : Translated from Local Maximum Filter [C++ software]
|                       Ghent University, Laboratory of Forest Management and Spatial Information Techniques
|                       Lieven P.C. Verbeke
|
| This file is part of the QGIS Tree Density Calculator plugin and treedensitycalculator python package.
|
| This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
| License as published by the Free Software Foundation, either version 3 of the License, or any later version.
|
| This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
| warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
|
| You should have received a copy of the GNU General Public License along with Foobar.  If not see www.gnu.org/licenses.
| ----------------------------------------------------------------------------------------------------------------------
"""
import os
import tempfile

from .imports import import_image, import_vector_as_image
from .exports import write_mask_layer, write_point_layer, write_voronoi_layer
from ..scripts.local_max_filter import LocalMaxFilter


def run_algorithm_local_max_filter(image_path, window, update_progress_bar, log_function,
                                   mask_path=None, output_base_path=None, snap_distance=None, voronoi=None,
                                   feedback=None, context=None):
    """
    General interface between the GUI/CLI and script.

    :param image_path: the absolute path to the raster file
    :param window: window size in meters
    :param update_progress_bar: function to update the progress bar
    :param log_function: function to log
    :param mask_path: absolute path to the vector file (optional)
    :param output_base_path: base path for output files (optional)
    :param snap_distance: snap distance for output points (optional)
    :param voronoi: set to True if you want voronoi polygons as output (optional)
    :param feedback: necessary for the processing tool
    :param context: necessary for the processing tool
    :return:
    """

    if image_path is None:
        raise Exception("Choose a correct image file.")

    # get raster (clipped by mask) and its metadata
    img, img_srs, img_gt = import_image(image_path=image_path, mask_path=mask_path, window_size=window,
                                        feedback=feedback, context=context)

    # get area of interest as raster
    area_raster = import_vector_as_image(path=mask_path, geo_transform=img_gt, image_size=img.shape, image_srs=img_srs,
                                         window_size=window, feedback=feedback, context=None) if mask_path else None

    # convert the window size from meters to number of pixels (odd number)
    pixel_size = img_gt[1]
    window_px = int((window / pixel_size) // 2 * 2 + 1)
    if window_px == 1:
        window_px = 3

    # Print in the log the size of the window in pixels
    log_function('The window is built out of {0} by {0} pixels'.format(window_px))

    if snap_distance:
        if snap_distance > window / 2:
            raise Exception('Snap distance should be max half of the window size')
        snap_distance = int(snap_distance / pixel_size)
        # Print in the log the snap distance in pixels
        log_function('The snap distance is {0} pixels'.format(snap_distance))

    # Run LMF
    lmf_result = LocalMaxFilter(window_px).execute(img, area_of_interest=area_raster, snap=snap_distance,
                                                   geo_transform=img_gt, p=update_progress_bar)
    update_progress_bar(100)

    # base name for output files
    if not output_base_path:
        output_base_path = os.path.join(tempfile.gettempdir(),  os.path.basename(os.path.splitext(image_path)[0]))
    else:
        output_base_path, _ = os.path.splitext(output_base_path)
    output_base_path = '{0}_window_{1}'.format(output_base_path, window_px)

    # point layer
    output_point_path = output_base_path + '_point.shp'
    write_point_layer(output_path=output_point_path, points_dict=lmf_result, geo_transform=img_gt, srs=img_srs,
                      mask_path=mask_path, feedback=feedback, context=context)

    # Output mask in case it was given:
    if mask_path:
        output_mask_path = output_base_path + '_mask.shp'
        write_mask_layer(output_mask_path, mask_path, output_point_path)
    else:
        output_mask_path = None

    # write point layer to Voronoi polygon layer
    if voronoi:
        output_voronoi_path = output_base_path + '_voronoi.shp'
        write_voronoi_layer(output_path=output_voronoi_path, point_path=output_point_path, mask_path=mask_path,
                            feedback=feedback, context=context)
    else:
        output_voronoi_path = None

    return output_point_path, output_mask_path, output_voronoi_path
