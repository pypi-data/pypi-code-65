#!python
# -*- coding: utf-8 -*-
#
# Copyright 2019 Pintaudi Giorgio

# pylint: disable-msg=too-many-arguments
# pylint: disable-msg=too-many-function-args
# pylint: disable-msg=too-many-locals

# Python modules
import argparse

# ROOT
import ROOT

import wagascianpy.analysis.adc_distribution
# WAGASCI modules
import wagascianpy.analysis.bcid_distribution

ROOT.PyConfig.IgnoreCommandLineOptions = True


def simple_data_quality(run_root_dir, output_dir, only_global=False, overwrite=False):
    # type: (str, str, bool, bool) -> None

    only_global = bool(only_global)
    overwrite = bool(overwrite)

    wagascianpy.analysis.bcid_distribution.bcid_distribution(input_path=run_root_dir,
                                                             data_quality_dir=output_dir,
                                                             only_global=only_global,
                                                             overwrite=overwrite)

    wagascianpy.analysis.adc_distribution.adc_distribution(input_path=run_root_dir,
                                                           data_quality_dir=output_dir,
                                                           overwrite=overwrite)


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(usage='use "python %(prog)s --help" for more information',
                                     description='Simple data quality checks: BCID distribution and'
                                                 '2D ADC channel histogram.',
                                     argument_default=None)

    PARSER.add_argument('--run_root_dir', metavar='<run root directory>', type=str,
                        required=True, dest="run_root_dir", help='Path to the run directory to analyze')
    PARSER.add_argument('--output_dir', metavar='<output directory>', type=str,
                        required=True, dest="output_dir", help='Output directory')
    PARSER.add_argument('--only-global', required=False, default=True, dest='only_global', action='store_false',
                        help="do not plot the chip by chip BCID distribution but only the global one")
    PARSER.add_argument('--overwrite', required=False, default=False, dest='overwrite', action='store_true')

    PARSER.set_defaults(ignore_wagasci=False)
    ROOT.gROOT.SetBatch(True)

    ARGS = PARSER.parse_args()
    RUN_ROOT_DIR = ARGS.run_root_dir
    OUTPUT_DIR = ARGS.output_dir
    ONLY_GLOBAL = ARGS.only_global
    OVERWRITE = ARGS.overwrite

    simple_data_quality(RUN_ROOT_DIR, OUTPUT_DIR, ONLY_GLOBAL, OVERWRITE)
