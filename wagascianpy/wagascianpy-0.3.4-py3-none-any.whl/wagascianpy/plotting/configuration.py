#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# copyright 2020 pintaudi giorgio
#

import argparse
import sys
import time

from wagascianpy.utils.configuration import *


def fill_configuration(args=None):
    # type: (Optional[[argparse.Namespace, Dict[str, Any]]]) -> None
    """
    Take as input the parsed arguments from command line and return the Configuration object
    :param args: parsed arguments
    :return: Configuration object
    """

    if isinstance(args, argparse.Namespace):
        args = vars(args)

    # plotting configuration
    output_string = args["output_string"]
    output_path = args["output_path"]
    delivered_pot = args["delivered_pot"]
    accumulated_pot = args["accumulated_pot"]
    bsd_spill = args["bsd_spill"]
    wagasci_spill_history = args["wagasci_spill_history"]
    wagasci_spill_number = args["wagasci_spill_number"]
    wagasci_fixed_spill = args["wagasci_fixed_spill"]
    temperature = args["temperature"]
    humidity = args["humidity"]
    gain_history = args["gain_history"]
    dark_noise_history = args["dark_noise_history"]
    all_plotters = args["all"]
    run_markers = args["run_markers"]
    maintenance_markers = args["maintenance_markers"]
    trouble_markers = args["trouble_markers"]
    topology = args["topology"]
    only_good = args["only_good"]
    save_tfile = args["save_tfile"]
    # WAGASCI database configuration
    wagasci_database = args["wagasci_database"]
    wagasci_decoded_location = args["wagasci_decoded_location"]
    # BSD database configuration
    bsd_database = args["bsd_database"]
    bsd_repository = args["bsd_repository"]
    bsd_download_location = args["bsd_download_location"]
    # global configuration
    t2krun = args["t2krun"]
    data_quality_location = args["data_quality_location"]
    data_quality_filename = args["data_quality_filename"]
    # run selectors
    start_time = args["start_time"]
    stop_time = args["stop_time"]
    start_run = args["start_run"]
    stop_run = args["stop_run"]

    # sanity checks
    if all_plotters:
        delivered_pot = accumulated_pot = bsd_spill = wagasci_spill_history = True
        wagasci_spill_number = wagasci_fixed_spill = temperature = humidity = True
        gain_history = dark_noise_history = True

    start = start_run if start_run else start_time
    stop = stop_run if stop_run else stop_time

    # wagasci database configuration
    if not wagasci_database:
        wagasci_database = Configuration.wagascidb.wagasci_database()
    if not wagasci_decoded_location:
        wagasci_decoded_location = Configuration.wagascidb.wagasci_decoded_location()

    # bsd database configuration
    if not bsd_database:
        bsd_database = Configuration.bsddb.bsd_database()
    if not bsd_download_location:
        bsd_download_location = Configuration.bsddb.bsd_download_location()
    if not bsd_repository:
        bsd_repository = Configuration.bsddb.bsd_repository()

    # global configuration
    if not t2krun:
        t2krun = Configuration.global_configuration.t2krun()
    if not data_quality_location:
        data_quality_location = Configuration.global_configuration.data_quality_location()

    # WAGASCI database configuration
    Configuration.wagascidb.override({
        'wagasci_database': wagasci_database,
        'wagasci_decoded_location': wagasci_decoded_location
    })

    # BSD database configuration
    Configuration.bsddb.override({
        'bsd_database': bsd_database,
        'bsd_download_location': bsd_download_location,
        'bsd_repository': bsd_repository
    })

    # global configuration
    Configuration.global_configuration.override({
        't2krun': t2krun,
        'data_quality_location': data_quality_location,
        'data_quality_filename': data_quality_filename
    })

    # plotter configuration
    Configuration.create_section('plotter')
    Configuration.plotter.override({
        'output_string': output_string,
        'output_path': output_path,
        'delivered_pot': delivered_pot,
        'accumulated_pot': accumulated_pot,
        'bsd_spill': bsd_spill,
        'wagasci_spill_history': wagasci_spill_history,
        'wagasci_spill_number': wagasci_spill_number,
        'wagasci_fixed_spill': wagasci_fixed_spill,
        'temperature': temperature,
        'humidity': humidity,
        'gain_history': gain_history,
        'dark_noise_history': dark_noise_history,
        'run_markers': run_markers,
        'maintenance_markers': maintenance_markers,
        'trouble_markers': trouble_markers,
        'save_tfile': save_tfile,
        'topology': topology,
        'only_good': only_good
    })

    # run selectors
    Configuration.create_section('run_select')
    Configuration.run_select.override({
        'start': start,
        'stop': stop,
    })

    print("CONFIGURATION:")
    Configuration.dump()
    sys.stdout.flush()
    time.sleep(1)
