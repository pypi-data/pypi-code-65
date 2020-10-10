#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 Pintaudi Giorgio

import argparse
import textwrap
from typing import List, Optional

import wagascianpy.plotting.topology


def parse_args(args):
    # type: (List[str]) -> argparse.Namespace
    """
    Parse arguments from command line or configuration file
    :param args: raw arguments
    :return: parsed arguments
    """
    parser = argparse.ArgumentParser(usage='use "python %(prog)s --help" for more information',
                                     argument_default=None, description=textwrap.dedent('''\
                                     Produce spill history plots. If the stop time or stop run is not provided
                                      the present time or the last run are assumed. If both time and run number
                                      are provided the run number is preferred.'''))

    parser.add_argument('-n', '--output-string', metavar='<output string>', dest='output_string',
                        type=str, required=True, help=textwrap.dedent('''\
                        Output string to prepend to the file names
                        '''))

    parser.add_argument('-o', '--output-path', metavar='<output path>', dest='output_path',
                        type=str, required=True, help=textwrap.dedent('''\
                        Directory where to save the output plots
                        '''))
    parser.add_argument('-dp', '--delivered-pot', dest='delivered_pot', required=False, default=False,
                        action='store_true', help=textwrap.dedent('''\
                        If set plot the POT delivered by the beam line in the selected interval of time (or runs)'''))

    parser.add_argument('-ap', '--accumulated-pot', dest='accumulated_pot', required=False, default=False,
                        action='store_true', help=textwrap.dedent('''\
                        If set plot the POT accumulated by the WAGASCI detectors in the selected interval of time (or 
                        runs)'''))

    parser.add_argument('-bs', '--bsd-spill', dest='bsd_spill', required=False, default=False,
                        action='store_true', help=textwrap.dedent('''\
                        If set plot the BSD spill number in the selected interval of time (or runs)'''))

    parser.add_argument('-wsh', '--wagasci-spill-history', dest='wagasci_spill_history', required=False, default=False,
                        action='store_true', help=textwrap.dedent('''\
                        If set plot the WAGASCI spill number history in time for the selected interval of time (or 
                        runs)'''))

    parser.add_argument('-wsn', '--wagasci-spill-number', dest='wagasci_spill_number', required=False, default=False,
                        action='store_true', help=textwrap.dedent('''\
                        If set plot the WAGASCI spill number for the selected interval of time (or runs)'''))

    parser.add_argument('-wfs', '--wagasci-fixed-spill', dest='wagasci_fixed_spill', required=False, default=False,
                        action='store_true', help=textwrap.dedent('''\
                        If set plot the WAGASCI fixed spill number in the selected interval of time (or runs)'''))

    parser.add_argument('-th', '--temperature', dest='temperature', required=False, default=False,
                        action='store_true', help=textwrap.dedent('''\
                        If set plot the WAGASCI and WallMRD temperature in the selected interval of time (or runs)'''))

    parser.add_argument('-hh', '--humidity', dest='humidity', required=False, default=False,
                        action='store_true', help=textwrap.dedent('''\
                        If set plot the WAGASCI and WallMRD humidity in the selected interval of time (or runs)'''))

    parser.add_argument('-gh', '--gain-history', dest='gain_history', required=False, default=False,
                        action='store_true', help=textwrap.dedent('''\
                        If set plot the MPPC gain history in the selected interval of time (or runs)'''))

    parser.add_argument('-dh', '--dark-noise-history', dest='dark_noise_history', required=False, default=False,
                        action='store_true', help=textwrap.dedent('''\
                        If set plot the MPPC dark noise history in the selected interval of time (or runs)'''))

    parser.add_argument('-all', '--all', dest='all', required=False, default=False,
                        action='store_true', help=textwrap.dedent('''\
                        If set plot all available plots are produced for the selected interval of time (or runs)'''))

    parser.add_argument('-mr', '--run-markers', dest='run_markers', required=False, default=False,
                        action='store_true', help=textwrap.dedent('''If set the WAGASCI runs are marked'''))

    parser.add_argument('-mm', '--maintenance-markers', dest='maintenance_markers', required=False, default=False,
                        action='store_true', help=textwrap.dedent('''If set the maintenance days are marked'''))

    parser.add_argument('-mt', '--trouble-markers', dest='trouble_markers', required=False, default=False,
                        action='store_true', help=textwrap.dedent('''If set the electronics and DAQ trouble events are 
                        marked'''))

    parser.add_argument('-tf', '--save-tfile', dest='save_tfile', required=False, default=False,
                        action='store_true', help=textwrap.dedent('''If set save the TCanvas inside a ROOT file'''))

    parser.add_argument('-d', '--wagasci-database', metavar='<WAGASCI run database>', dest='wagasci_database',
                        type=str, required=False, help=textwrap.dedent('''\
                        Path to the WAGASCI run database file. This file is created by the 
                        Wagasci Database Viewer (wagascidb_viewer.py) program and is usually called wagascidb.db.
                        (default: %(default)s)
                        '''))

    parser.add_argument('-f', '--wagasci-decoded-location', metavar='<WAGASCI runs directory>',
                        dest='wagasci_decoded_location', type=str, required=False, help=textwrap.dedent('''\
                        Path to the directory containing all the WAGASCI decoded runs. (default: %(default)s)
                        '''))

    parser.add_argument('-b', '--bsd-database', metavar='<BSD database>', dest='bsd_database',
                        type=str, required=False, help=textwrap.dedent('''\
                        Path to the BSD database file. This file is created by the Wagasci Database Viewer
                         (wagascidb_viewer.py) program and is usually called bsddb.db. (default: %(default)s)
                        '''))

    parser.add_argument('-g', '--bsd-download-location', metavar='<BSD files directory>',
                        dest='bsd_download_location', type=str, required=False, help=textwrap.dedent('''\
                        Path to the directory containing all the BSD root files.
                        '''))

    parser.add_argument('-br', '--bsd-repository', metavar='<BSD repository location>', dest='bsd_repository', type=str,
                        nargs=1, required=False, help=textwrap.dedent('''
                        Same as --bsd-download-location'''))

    parser.add_argument('-t', '--t2krun', metavar='<T2K run>', dest='t2krun', type=int,
                        help='T2K run number (default is 10)', default=10, required=False)

    parser.add_argument('-dql', '--data-quality-location', metavar='<data quality location>',
                        dest='data_quality_location', type=str, required=False, help=textwrap.dedent('''
                        Local folder where to store output of wgDataQuality program.(default: %(default)s)'''))

    parser.add_argument('-dqf', '--data-quality-filename', metavar='<data quality file name>',
                        dest='data_quality_filename', type=str, required=False, help=textwrap.dedent('''
                        Name of the data quality file (excluding dif_X and extension).(default: %(default)s)'''))

    parser.add_argument('-at', '--start-time', metavar='<start time>', dest='start_time', type=str,
                        help='Start date and time in the format "%%Y/%%m/%%d %%H:%%M:%%S"', default=None,
                        required=False)

    parser.add_argument('-ot', '--stop-time', metavar='<stop time>', dest='stop_time', type=str,
                        help='Stop date and time in the format "%%Y/%%m/%%d %%H:%%M:%%S"', default=None,
                        required=False)

    parser.add_argument('-ar', '--start-run', metavar='<start run>', dest='start_run', type=int,
                        help='start run number', default=None, required=False)

    parser.add_argument('-or', '--stop-run', metavar='<stop run>', dest='stop_run', type=int,
                        help='Stop run number', default=None, required=False)

    parser.add_argument('-to', '--topology', metavar='<topology>', dest='topology', type=str, required=False,
                        default=None, help=textwrap.dedent('''
                        Select the subdetectors. List their names separated by comma and do NOT mix the two groups:
                         GROUP BY SUBDETECTOR = (wagasci_upstream, wagasci_downstream, wallmrd_north, wallmrd_south) or
                         GROUP BY DIF = (wagasci_upstream_top, wagasci_upstream_side, wagasci_downstream_top, 
                         wagasci_downstream_side, wallmrd_north_top, wallmrd_north_bottom, wallmrd_south_top, 
                         wallmrd_south_bottom). Some plotters ignore the manually specified topology.
                        (default: All)'''))

    parser.add_argument('-og', '--only-good', dest='only_good', required=False, default=False,
                        action='store_true', help=textwrap.dedent('''\
                        Only select runs and detectors whose flag is set to good (good run or good data)'''))

    # Flatten all arguments
    parsed_args = parser.parse_args(args=args)
    for name, value in vars(parsed_args).items():
        if isinstance(value, list):
            setattr(parsed_args, name, ','.join(value))

    return parsed_args


def parse_plotting_topology(topology_str):
    # type: (Optional[str]) -> wagascianpy.plotting.topology.Topology
    """
    Read a string containing the list of enabled detectors and return a Topology object
    :param topology_str: list of enabled detectors
    :return: Topology object
    """
    if not topology_str:
        iterate_by_dif = True
    elif 'side' in topology_str or 'top' in topology_str or 'bottom' in topology_str:
        iterate_by_dif = True
    else:
        iterate_by_dif = False
    topology = wagascianpy.plotting.topology.Topology(iterate_by_dif=iterate_by_dif)
    if topology_str is None:
        return topology
    else:
        topology.disable_all()
        if iterate_by_dif:
            if 'wagasci_upstream_top' in topology_str:
                topology.wagasci_upstream_top.enable()
            if 'wagasci_upstream_side' in topology_str:
                topology.wagasci_upstream_side.enable()
            if 'wagasci_downstream_top' in topology_str:
                topology.wagasci_downstream_top.enable()
            if 'wagasci_downstream_side' in topology_str:
                topology.wagasci_downstream_side.enable()
            if 'wallmrd_north_top' in topology_str:
                topology.wallmrd_north_top.enable()
            if 'wallmrd_north_bottom' in topology_str:
                topology.wallmrd_north_bottom.enable()
            if 'wallmrd_south_top' in topology_str:
                topology.wallmrd_south_top.enable()
            if 'wallmrd_south_bottom' in topology_str:
                topology.wallmrd_south_bottom.enable()
        else:
            if 'wagasci_upstream' in topology_str:
                topology.wagasci_upstream.enable()
            if 'wagasci_downstream' in topology_str:
                topology.wagasci_downstream.enable()
            if 'wallmrd_north' in topology_str:
                topology.wallmrd_north.enable()
            if 'wallmrd_south' in topology_str:
                topology.wallmrd_south.enable()
    return topology
