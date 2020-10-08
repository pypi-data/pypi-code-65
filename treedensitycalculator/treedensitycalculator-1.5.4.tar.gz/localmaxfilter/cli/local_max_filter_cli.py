# -*- coding: utf-8 -*-
"""
| ----------------------------------------------------------------------------------------------------------------------
| Date                : August 2018
| Copyright           : © 2018 - 2020 by Tinne Cahy (Geo Solutions) and Ann Crabbé (KU Leuven)
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
| You should have received a copy of the GNU General Public License. If not see www.gnu.org/licenses.
| ----------------------------------------------------------------------------------------------------------------------
"""
import os
import argparse

from ..in_out import run_algorithm_local_max_filter
from ..scripts.local_max_filter import LocalMaxFilter


def create_parser():
    parser = argparse.ArgumentParser(description=str(LocalMaxFilter.__doc__))

    parser.add_argument('image', metavar='image', type=str, help='input reflectance image path')

    parser.add_argument('window', metavar='sliding_window', type=int,
                        help='length of the sliding window, in meters (default 5 m), '
                             'should be a multiple of the image pixel size')

    parser.add_argument('-m', '--mask', metavar='\b', type=str,
                        help='overlapping vector mask path')

    parser.add_argument('-v', '--voronoi', action='store_true', default=False,
                        help='create a Voronoi shapefile based on the tree locations (default off)')

    parser.add_argument('-s', '--snap', metavar='\b', type=float,
                        help='give distance [m] for the snap tool, should be max half of the window size, '
                             'tree tops which are closer to each other than the given distance will be taken as one')

    parser.add_argument('-o', '--output', metavar='\b',
                        help='path for output files, give base without extension '
                             '(default: in same folder with extension _window_{}.shp)')

    return parser


def run_local_max(args):
    """
    Documentation: treedensity -h
    """
    mask_path = os.path.abspath(args.mask) if args.mask else None
    output_base_path = os.path.abspath(args.output) if args.output else os.path.abspath(args.image)

    def log_function(text):
        print(str(text))

    point, mask, voronoi = run_algorithm_local_max_filter(image_path=os.path.abspath(args.image),
                                                          window=args.window,
                                                          update_progress_bar=log_function,
                                                          log_function=log_function,
                                                          mask_path=mask_path,
                                                          output_base_path=output_base_path,
                                                          snap_distance=args.snap,
                                                          voronoi=args.voronoi)

    print("Output point layer: {}".format(point))
    print("Output mask layer: {}".format(mask))
    print("Output voronoi layer: {}".format(voronoi))


def main():
    # Include code to work with processing algorithms
    # ===============================================
    import sys
    from qgis.core import QgsApplication
    from qgis.analysis import QgsNativeAlgorithms

    if not os.environ.get('QGIS_PREFIX_PATH'):
        if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            os.environ['QGIS_PREFIX_PATH'] = '/usr'
        else:
            os.environ['QGIS_PREFIX_PATH'] = os.path.join("C:", os.sep, "OSGeo4W64", "apps", "qgis")

    QgsApplication.setPrefixPath(os.environ['QGIS_PREFIX_PATH'], True)
    qgs = QgsApplication([], False)
    qgs.initQgis()

    # Append the path where processing plugin can be found
    # Ubuntu Linux for example the prefix path is: /usr  and plugins: (qgis_prefix)/share/qgis/python/plugins
    sys.path.append(os.path.join(os.environ['QGIS_PREFIX_PATH'], 'share', 'qgis', 'python', 'plugins'))  # unix, mac
    # On Windows for example the prefix path is: C:\\OSGeo4W\\apps\\qgis\\ and plugins: (qgis_prefix)\\python\\plugins
    sys.path.append(os.path.join(os.environ['QGIS_PREFIX_PATH'], 'python', 'plugins'))  # windows

    import processing
    from processing.core.Processing import Processing
    Processing.initialize()
    QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

    # ===============================================

    parser = create_parser()
    run_local_max(parser.parse_args())


if __name__ == '__main__':
    main()
