#!python
# -*- coding: utf-8 -*-
#
# Copyright 2020 Pintaudi Giorgio

import os
import sys

import wagascianpy.plotting.detector
import wagascianpy.plotting.marker
import wagascianpy.plotting.parse_args
import wagascianpy.plotting.plotter
import wagascianpy.utils.utils
from wagascianpy.plotting.configuration import Configuration


def spill_history(plotter):
    plotter.template_plotter()


if __name__ == "__main__":

    # Parse shell arguments
    args = wagascianpy.plotting.parse_args.parse_args(sys.argv[1:])

    # Edit the initial configuration
    wagascianpy.plotting.configuration.fill_configuration(args)

    if not os.path.exists(Configuration.plotter.output_path()):
        wagascianpy.utils.utils.mkdir_p(Configuration.plotter.output_path())

    markers = wagascianpy.plotting.marker.MarkerTuple(
        run=Configuration.plotter.run_markers(),
        maintenance=Configuration.plotter.maintenance_markers(),
        trouble=Configuration.plotter.trouble_markers())

    output_file_format = os.path.join(Configuration.plotter.output_path(),
                                      "%s_{name}.pdf" % Configuration.plotter.output_string())

    topology_str = Configuration.plotter.topology()
    topology = wagascianpy.plotting.parse_args.parse_plotting_topology(topology_str)

    if Configuration.bsddb.bsd_download_location():
        bsd_location = Configuration.bsddb.bsd_download_location()
    else:
        bsd_location = Configuration.bsddb.bsd_repository()

    if Configuration.plotter.delivered_pot():
        spill_history(
            wagascianpy.plotting.plotter.BsdPotPlotter(
                output_file_path=output_file_format.format(name='bsd_pot_history'),
                bsd_database=Configuration.bsddb.bsd_database(),
                bsd_repository=bsd_location,
                wagasci_database=Configuration.wagascidb.wagasci_database(),
                t2krun=Configuration.global_configuration.t2krun(),
                start=Configuration.run_select.start(),
                stop=Configuration.run_select.stop(),
                enabled_markers=markers,
                save_tfile=Configuration.run_select.save_tfile()))

    if Configuration.plotter.accumulated_pot():
        spill_history(wagascianpy.plotting.plotter.WagasciPotPlotter(
            output_file_path=output_file_format.format(name='wagasci_pot_history'),
            bsd_database=Configuration.bsddb.bsd_database(),
            bsd_repository=bsd_location,
            wagasci_database=Configuration.wagascidb.wagasci_database(),
            wagasci_repository=Configuration.wagascidb.wagasci_decoded_location(),
            t2krun=Configuration.global_configuration.t2krun(),
            only_good=Configuration.plotter.only_good(),
            start=Configuration.run_select.start(),
            stop=Configuration.run_select.stop(),
            enabled_markers=markers,
            save_tfile=Configuration.run_select.save_tfile()))

    if Configuration.plotter.bsd_spill():
        spill_history(wagascianpy.plotting.plotter.BsdSpillPlotter(
            output_file_path=output_file_format.format(name='bsd_spill_history'),
            bsd_database=Configuration.bsddb.bsd_database(),
            bsd_repository=bsd_location,
            wagasci_database=Configuration.wagascidb.wagasci_database(),
            t2krun=Configuration.global_configuration.t2krun(),
            start=Configuration.run_select.start(),
            stop=Configuration.run_select.stop(),
            enabled_markers=markers,
            save_tfile=Configuration.run_select.save_tfile()))

    if Configuration.plotter.wagasci_spill_history():
        spill_history(wagascianpy.plotting.plotter.WagasciSpillHistoryPlotter(
            output_file_path=output_file_format.format(name='wagasci_spill_history'),
            bsd_database=Configuration.bsddb.bsd_database(),
            bsd_repository=bsd_location,
            wagasci_database=Configuration.wagascidb.wagasci_database(),
            wagasci_repository=Configuration.wagascidb.wagasci_decoded_location(),
            t2krun=Configuration.global_configuration.t2krun(),
            start=Configuration.run_select.start(),
            stop=Configuration.run_select.stop(),
            enabled_markers=markers,
            topology=topology,
            save_tfile=Configuration.run_select.save_tfile()))

    if Configuration.plotter.wagasci_fixed_spill():
        spill_history(wagascianpy.plotting.plotter.WagasciFixedSpillPlotter(
            output_file_path=output_file_format.format(name='wagasci_fixed_spill_history'),
            bsd_database=Configuration.bsddb.bsd_database(),
            bsd_repository=bsd_location,
            wagasci_database=Configuration.wagascidb.wagasci_database(),
            wagasci_repository=Configuration.wagascidb.wagasci_decoded_location(),
            t2krun=Configuration.global_configuration.t2krun(),
            start=Configuration.run_select.start(),
            stop=Configuration.run_select.stop(),
            enabled_markers=markers,
            topology=topology,
            save_tfile=Configuration.run_select.save_tfile()))

    if Configuration.plotter.wagasci_spill_number():
        spill_history(wagascianpy.plotting.plotter.WagasciSpillNumberPlotter(
            output_file_path=output_file_format.format(name='wagasci_spill_number'),
            bsd_database=Configuration.bsddb.bsd_database(),
            bsd_repository=bsd_location,
            wagasci_database=Configuration.wagascidb.wagasci_database(),
            wagasci_repository=Configuration.wagascidb.wagasci_decoded_location(),
            t2krun=Configuration.global_configuration.t2krun(),
            start=Configuration.run_select.start(),
            stop=Configuration.run_select.stop(),
            enabled_markers=markers,
            topology=topology,
            save_tfile=Configuration.run_select.save_tfile()))

    if Configuration.plotter.temperature():
        spill_history(wagascianpy.plotting.plotter.TemperaturePlotter(
            output_file_path=output_file_format.format(name='wagasci_temperature_history'),
            bsd_database=Configuration.bsddb.bsd_database(),
            bsd_repository=bsd_location,
            wagasci_database=Configuration.wagascidb.wagasci_database(),
            wagasci_repository=Configuration.wagascidb.wagasci_decoded_location(),
            t2krun=Configuration.global_configuration.t2krun(),
            start=Configuration.run_select.start(),
            stop=Configuration.run_select.stop(),
            enabled_markers=markers,
            topology=topology,
            save_tfile=Configuration.run_select.save_tfile()))

    if Configuration.plotter.humidity():
        spill_history(wagascianpy.plotting.plotter.HumidityPlotter(
            output_file_path=output_file_format.format(name='wagasci_humidity_history'),
            bsd_database=Configuration.bsddb.bsd_database(),
            bsd_repository=bsd_location,
            wagasci_database=Configuration.wagascidb.wagasci_database(),
            wagasci_repository=Configuration.wagascidb.wagasci_decoded_location(),
            t2krun=Configuration.global_configuration.t2krun(),
            start=Configuration.run_select.start(),
            stop=Configuration.run_select.stop(),
            enabled_markers=markers,
            topology=topology,
            save_tfile=Configuration.run_select.save_tfile()))

    if Configuration.plotter.gain_history():
        spill_history(wagascianpy.plotting.plotter.GainHistoryPlotter(
            output_file_path=output_file_format.format(name='wagasci_gain_history'),
            data_quality_location=Configuration.global_configuration.data_quality_location(),
            data_quality_filename=Configuration.global_configuration.data_quality_filename(),
            enabled_markers=markers,
            topology=topology,
            save_tfile=Configuration.run_select.save_tfile()))

    if Configuration.plotter.dark_noise_history():
        spill_history(wagascianpy.plotting.plotter.DarkNoiseHistoryPlotter(
            output_file_path=output_file_format.format(name='wagasci_dark_noise_history'),
            data_quality_location=Configuration.global_configuration.data_quality_location(),
            data_quality_filename=Configuration.global_configuration.data_quality_filename(),
            enabled_markers=markers,
            topology=topology,
            save_tfile=Configuration.run_select.save_tfile()))
