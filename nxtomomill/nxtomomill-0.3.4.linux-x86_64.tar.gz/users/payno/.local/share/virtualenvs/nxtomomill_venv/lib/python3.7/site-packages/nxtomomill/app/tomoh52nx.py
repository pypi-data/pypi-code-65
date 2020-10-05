# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2015-2020 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

"""
This module provides global definitions and methods to transform
a tomo dataset written in edf into and hdf5/nexus file
"""

__authors__ = ["C. Nemoz", "H. Payno", "A.Sole"]
__license__ = "MIT"
__date__ = "16/01/2020"

import logging
from nxtomomill import utils
from nxtomomill.settings import (H5_Z_TRANS_KEYS, H5_Y_TRANS_KEYS,
                                 H5_X_TRANS_KEYS, H5_VALID_CAMERA_NAMES,
                                 H5_ROT_ANGLE_KEYS, H5_ACQ_EXPO_TIME_KEYS,
                                 H5_X_PIXEL_SIZE, H5_Y_PIXEL_SIZE)
from nxtomomill.settings import (H5_ALIGNMENT_TITLES, H5_PROJ_TITLES,
                                 H5_REF_TITLES, H5_DARK_TITLES, H5_INIT_TITLES)
from nxtomomill.converter import h5_to_nx, H5FileKeys, H5ScanTitles
import argparse


logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


_SETTABLE_PARAMETERS_UNITS = \
    {
        'energy': 'kev',
    }

_SETTABLE_PARAMETERS = _SETTABLE_PARAMETERS_UNITS.keys()


def _getPossibleInputParams():
    """

    :return: string with param1 (expected unit) ...
    """
    res = []
    for key, value in _SETTABLE_PARAMETERS_UNITS.items():
        res.append('{} ({})'.format(key, value))
    return ', '.join(res)


def _extract_param_value(key_values):
    '''extract all the key / values elements from the str_list. Expected
    format is `param_1_name param_1_value param_2_name param_2_value ...`

    :param str str_list: raw input string as `param_1_name param_1_value
                         param_2_name param_2_value ...`
    :return: dict of tuple (param_name, param_value)
    :rtype: dict
    '''
    if len(key_values) % 2 != 0:
        raise ValueError('Expect a pair `param_name, param_value` for each '
                         'parameters')

    def pairwise(it):
        it = iter(it)
        while True:
            try:
                yield next(it), next(it)
            except StopIteration:
                # no more elements in the iterator
                return
    res = {}
    for name, value in pairwise(key_values):
        if name not in _SETTABLE_PARAMETERS:
            raise ValueError('parameters {} is not managed'.format(name))
        res[name] = value
    return res


def main(argv):
    """
    """
    parser = argparse.ArgumentParser(description='convert data acquired as '
                                                 'hdf5 from bliss to nexus '
                                                 '`NXtomo` classes')
    parser.add_argument('input_file_path', help='master file of the '
                                                'acquisition')
    parser.add_argument('output_file', help='output .nx or .h5 file')
    parser.add_argument('--file_extension',
                        action="store_true",
                        default='.nx',
                        help='extension of the output file. Valid values are '
                             '' + '/'.join(utils.FileExtension.values()))
    parser.add_argument('--single-file',
                        help='merge all scan sequence to the same output file. '
                             'By default create one file per sequence and '
                             'group all sequence in the output file',
                        dest='single_file',
                        action='store_true',
                        default=False)
    parser.add_argument('--no-input',
                        help='Do not ask for any',
                        dest='request_input',
                        action='store_false',
                        default=True)

    parser.add_argument('--x_trans_keys', default=','.join(H5_X_TRANS_KEYS),
                        help='x translation key in bliss HDF5 file')
    parser.add_argument('--y_trans_keys', default=','.join(H5_Y_TRANS_KEYS),
                        help='y translation key in bliss HDF5 file')
    parser.add_argument('--z_trans_keys', default=','.join(H5_Z_TRANS_KEYS),
                        help='z translation key in bliss HDF5 file')
    parser.add_argument('--valid_camera_names', default=','.join(H5_VALID_CAMERA_NAMES),
                        help='Valid NXDetector dataset name to be considered'
                             'as a camera that we want to convert')
    parser.add_argument('--rot_angle_keys', default=','.join(H5_ROT_ANGLE_KEYS),
                        help='Valid dataset name for rotation angle')
    parser.add_argument('--acq_expo_time_keys', default=','.join(H5_ACQ_EXPO_TIME_KEYS),
                        help='Valid dataset name for acquisition exposure time')
    parser.add_argument('--x_pixel_size_key', default=H5_X_PIXEL_SIZE,
                        help='X pixel size key to read')
    parser.add_argument('--y_pixel_size_key', default=H5_Y_PIXEL_SIZE,
                        help='Y pixel size key to read')

    # scan titles
    parser.add_argument('--init_titles', default=','.join(H5_INIT_TITLES),
                        help='Titles corresponding to init scans')
    parser.add_argument('--dark_titles', default=','.join(H5_DARK_TITLES),
                        help='Titles corresponding to dark scans')
    parser.add_argument('--ref_titles', default=','.join(H5_REF_TITLES),
                        help='Titles corresponding to ref scans')
    parser.add_argument('--proj_titles', default=','.join(H5_PROJ_TITLES),
                        help='Titles corresponding to projection scans')
    parser.add_argument('--align_titles', default=','.join(H5_ALIGNMENT_TITLES),
                        help='Titles corresponding to alignment scans')
    parser.add_argument('--set-params', default='',
                        nargs='*',
                        help='Allow manual definition of some parameters. ' \
                             'Valid parameters (and expected input unit) '
                             'are: {}.'.format(_getPossibleInputParams()))
    options = parser.parse_args(argv[1:])
    conv = utils.get_tuple_of_keys_from_cmd
    file_keys = H5FileKeys(x_trans_keys=conv(options.x_trans_keys),
                           y_trans_keys=conv(options.y_trans_keys),
                           z_trans_keys=conv(options.z_trans_keys),
                           valid_camera_names=conv(options.valid_camera_names),
                           rot_angle_keys=conv(options.rot_angle_keys),
                           acq_expo_time_keys=conv(options.acq_expo_time_keys),
                           x_pixel_size=options.x_pixel_size_key,
                           y_pixel_size=options.y_pixel_size_key,
                           )
    scan_titles = H5ScanTitles(init_titles=conv(options.init_titles),
                               dark_titles=conv(options.dark_titles),
                               ref_titles=conv(options.ref_titles),
                               proj_titles=conv(options.proj_titles),
                               align_titles=conv(options.align_titles))
    options.set_params = _extract_param_value(options.set_params)

    h5_to_nx(input_file_path=options.input_file_path,
             output_file=options.output_file, single_file=options.single_file,
             file_extension=options.file_extension,
             request_input=options.request_input, file_keys=file_keys,
             scan_titles=scan_titles,
             param_already_defined=options.set_params)
    exit(0)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
