#!python
# -*- coding: utf-8 -*-
#
# Copyright 2020 Pintaudi Giorgio
#
import sys

from typing import Optional, Type

from wagascianpy.utils.configuration import Configuration, RepositoryType

try:
    # for Python2
    # noinspection PyPep8Naming,PyUnresolvedReferences
    import Tkinter as tkinter
except ImportError:
    # for Python3
    # noinspection PyPep8Naming,PyUnresolvedReferences
    import tkinter
try:
    # for Python2
    # noinspection PyPep8Naming,PyUnresolvedReferences
    import tkMessageBox as messagebox
except ImportError:
    # for Python3
    # noinspection PyPep8Naming,PyUnresolvedReferences,PyCompatibility
    from tkinter import messagebox

import pygubu

import wagascianpy.database.bsddb
import wagascianpy.database.db_record
import wagascianpy.database.wagascidb
import wagascianpy.program.program_builder
import wagascianpy.utils.environment
import wagascianpy.utils.utils

import wagascianpy.viewer.downloader
import wagascianpy.viewer.show_run_info
import wagascianpy.viewer.topology
import wagascianpy.viewer.utils
import wagascianpy.viewer.parse_args
import wagascianpy.viewer.configuration


class Application(object):
    """Main GUI application
    """

    def __init__(self, config):
        # type: (Type[Configuration]) -> None

        # private attributes
        self._config = config
        self._batch_mode = self._config.viewer.batch_mode()
        self._records = None
        self._topology = wagascianpy.viewer.topology.Topology()

        if not self._batch_mode:
            self._build_gui()

    def _build_gui(self):
        # 1: Create a builder
        self._builder = pygubu.Builder()

        # 2: Load an gui.ui file
        self._builder.add_from_file(wagascianpy.viewer.utils.gui_file_finder())

        # 3: Create the widget using a master as parent
        self._mainwindow = self._builder.get_object('mainwindow')

        # 4: Connect method callbacks
        self._builder.connect_callbacks(self)

        # 5: override report_callback_exception method
        tkinter.Tk.report_callback_exception = self._report_callback_exception

        # 6: set default values
        self._builder.get_object('wallmrd_top_north').invoke()
        self._builder.get_object('wallmrd_bottom_north').invoke()
        self._builder.get_object('wallmrd_top_south').invoke()
        self._builder.get_object('wallmrd_bottom_south').invoke()
        self._builder.get_object('wagasci_top_upstream').invoke()
        self._builder.get_object('wagasci_side_upstream').invoke()
        self._builder.get_object('wagasci_top_downstream').invoke()
        self._builder.get_object('wagasci_side_downstream').invoke()

        # WAGASCI database configuration
        self._builder.get_object('wagasci_repository').set(
            self._config.wagascidb.wagasci_repository())
        self._builder.get_object('wagasci_database').set(
            self._config.wagascidb.wagasci_database())
        self._builder.get_object('wagasci_download_location').set(
            self._config.wagascidb.wagasci_download_location())
        self._builder.get_object('wagasci_decoded_location').set(
            self._config.wagascidb.wagasci_decoded_location())
        if self._config.wagascidb.repository_type() == RepositoryType.Simple:
            self._builder.get_object('simple_repository').invoke()
        elif self._config.wagascidb.repository_type() == RepositoryType.Borg:
            self._builder.get_object('borg_repository').invoke()
        else:
            print("Repository type not recognized : %s" % self._config.wagascidb.repository_type())

        # BSD database configuration
        self._builder.get_object('bsd_repository').set(
            self._config.bsddb.bsd_repository())
        self._builder.get_object('bsd_database').set(
            self._config.bsddb.bsd_database())
        self._builder.get_object('bsd_download_location').set(
            self._config.bsddb.bsd_download_location())

        # Global configuration
        self._builder.get_object('t2krun').set(self._config.global_configuration.t2krun())
        self._builder.get_object('data_quality_location').set(
            self._config.global_configuration.data_quality_location())
        self._builder.get_object('wagasci_libdir').set(self._config.global_configuration.wagasci_libdir())

        # Temperature configuration
        self._builder.get_object('temperature_sqlite_database').set(
            self._config.temperature.temperature_sqlite_database())

        # Viewer configuration
        self._builder.get_object('only_good_runs').invoke()
        self._builder.get_object('include_overlapping').invoke()

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def _report_callback_exception(self, exc, val, tb):
        """Report exceptions to the user
        """
        messagebox.showerror('Exception', message=str(val))

    def _get_configuration(self):
        """Read each member
        """
        # WAGASCI database configuration
        wagasci_repository = self._builder.get_object('wagasci_repository').get()
        wagasci_database = self._builder.get_object('wagasci_database').get()
        wagasci_download_location = self._builder.get_object('wagasci_download_location').get()
        wagasci_decoded_location = self._builder.get_object('wagasci_decoded_location').get()
        if self._builder.tkvariables.__getitem__('is_borg_repo').get():
            repository_type = RepositoryType.Borg
        else:
            repository_type = RepositoryType.Simple

        self._config.wagascidb.override({
            'wagasci_repository': wagasci_repository,
            'wagasci_database': wagasci_database,
            'wagasci_download_location': wagasci_download_location,
            'wagasci_decoded_location': wagasci_decoded_location,
            'repository_type': repository_type
        })

        # BSD database configuration
        bsd_repository = self._builder.get_object('bsd_repository').get()
        bsd_database = self._builder.get_object('bsd_database').get()
        bsd_download_location = self._builder.get_object('bsd_download_location').get()

        self._config.bsddb.override({
            'bsd_repository': bsd_repository,
            'bsd_database': bsd_database,
            'bsd_download_location': bsd_download_location
        })

        # Temperature configuration
        temperature_sqlite_database = self._builder.get_object('temperature_sqlite_database').get()
        self._config.temperature.override({
            'temperature_sqlite_database': temperature_sqlite_database
        })

        # Viewer configuration
        update_wagasci_database = self._builder.tkvariables.__getitem__('update_wagasci_database').get()
        rebuild_wagasci_database = self._builder.tkvariables.__getitem__('rebuild_wagasci_database').get()
        update_bsd_database = self._builder.tkvariables.__getitem__('update_bsd_database').get()
        rebuild_bsd_database = self._builder.tkvariables.__getitem__('rebuild_bsd_database').get()
        only_good_runs = self._builder.tkvariables.__getitem__('only_good_runs').get()
        include_overlapping = self._builder.tkvariables.__getitem__('include_overlapping').get()
        self._config.viewer.override({
            'update_wagasci_database': update_wagasci_database,
            'rebuild_wagasci_database': rebuild_wagasci_database,
            'update_bsd_database': update_bsd_database,
            'rebuild_bsd_database': rebuild_bsd_database,
            'only_good_runs': only_good_runs,
            'include_overlapping': include_overlapping,
        })

        # Global configuration
        t2krun = int(self._builder.get_object('t2krun').get())
        data_quality_location = self._builder.get_object('data_quality_location').get()
        wagasci_libdir = self._builder.get_object('wagasci_libdir').get()
        self._config.global_configuration.override({
            't2krun': t2krun,
            'data_quality_location': data_quality_location,
            'wagasci_libdir': wagasci_libdir,
        })

    def _get_topology(self):
        self._topology.read_topology(self._builder)

    def _get_analyzers_list(self):
        decoder = self._builder.tkvariables.__getitem__('decoder').get()
        bcid_distribution = self._builder.tkvariables.__getitem__('bcid_distribution').get()
        adc_distribution = self._builder.tkvariables.__getitem__('adc_distribution').get()
        spill_number_fixer = self._builder.tkvariables.__getitem__('spill_number_fixer').get()
        beam_summary_data = self._builder.tkvariables.__getitem__('beam_summary_data').get()
        temperature = self._builder.tkvariables.__getitem__('temperature').get()
        data_quality = self._builder.tkvariables.__getitem__('data_quality').get()
        Configuration.analyzer_configuration.override({
            'decoder': decoder,
            'bcid_distribution': bcid_distribution,
            'adc_distribution': adc_distribution,
            'spill_number_fixer': spill_number_fixer,
            'beam_summary_data': beam_summary_data,
            'temperature': temperature,
            'data_quality': data_quality
        })

    def _database_sanity_check(self):
        wagascianpy.viewer.utils.check_repository_and_database_sanity(
            repository=self._config.wagascidb.wagasci_repository(),
            database=self._config.wagascidb.wagasci_database(),
        )
        wagascianpy.viewer.utils.check_repository_and_database_sanity(
            repository=self._config.bsddb.bsd_repository(),
            database=self._config.bsddb.bsd_database(),
        )

    def download(self, overwrite=True, builtin_reporter=True):
        # type: (bool, bool) -> None
        # Read the topology checkboxes
        if not self._batch_mode:
            self._get_topology()

        if builtin_reporter:
            reporter = self._report_callback_exception
        else:
            reporter = None

        # Download the runs
        wagascianpy.viewer.downloader.downloader(
            config=self._config,
            records=self._records,
            topology=self._topology,
            reporter=reporter,
            overwrite=overwrite,
            batch_mode=self._batch_mode)

    def analyze(self, overwrite_flag=False):
        # type: (bool) -> None

        # 1 : update members
        if not self._batch_mode:
            self._get_configuration()
            self._get_analyzers_list()

        # 2 : Check the input folder (you need to have downloaded the raw data before decoding)
        if self._config.analyzer_configuration.decoder():
            run_dic = wagascianpy.viewer.utils.check_input_folder(
                input_folder=self._config.wagascidb.wagasci_download_location(),
                records=self._records, batch_mode=self._batch_mode)
        else:
            run_dic = wagascianpy.viewer.utils.check_input_folder(
                input_folder=self._config.wagascidb.wagasci_decoded_location(),
                records=self._records, batch_mode=self._batch_mode)

        # 3 : create builder
        builder = wagascianpy.program.program_builder.ProgramBuilder(self._config.global_configuration.wagasci_libdir())

        # 4 : set run dictionary
        builder.run_location = run_dic

        # 5 : set save location
        if self._config.analyzer_configuration.decoder() and \
                self._config.wagascidb.wagasci_decoded_location():
            builder.save_location = self._config.wagascidb.wagasci_decoded_location()
        else:
            builder.output_dir_same_as_input()

        # 6 : add decoder
        if self._config.analyzer_configuration.decoder():
            builder.enforce_dependencies()
            builder.add_decoder(overwrite_flag=overwrite_flag,
                                enable_tdc_variables=False,
                                compatibility_mode=False)
        else:
            builder.do_not_enforce_dependencies()

        # 7 : add BCID distribution
        if self._config.analyzer_configuration.bcid_distribution():
            builder.add_bcid_distribution(only_global=True, overwrite=overwrite_flag)

        # 8 : add BCID distribution
        if self._config.analyzer_configuration.adc_distribution():
            builder.add_adc_distribution(overwrite=overwrite_flag)

        # 9 : add spill number fixer
        if self._config.analyzer_configuration.spill_number_fixer():
            builder.add_spill_number_fixer(enable_graphics=False)

        # 10 : add beam summary data
        if self._config.analyzer_configuration.beam_summary_data():
            builder.add_beam_summary_data(
                bsd_database_location=self._config.bsddb.bsd_database(),
                bsd_repository_location=self._config.bsddb.bsd_repository(),
                download_bsd_database_location='/tmp/bsddb.db',
                download_bsd_repository_location=self._config.bsddb.bsd_download_location(),
                t2krun=self._config.global_configuration.t2krun(),
                recursive=True)

        # 11 : add temperature
        if self._config.analyzer_configuration.temperature():
            builder.add_temperature(
                sqlite_database=self._config.temperature.temperature_sqlite_database())

        # 12 : add data quality
        if self._config.analyzer_configuration.data_quality():
            builder.multiple_runs_analyzer_save_location = self._config.global_configuration.data_quality_location()
            builder.add_data_quality()

        # 13 : start program
        builder.program.start()

    def get_time_interval(self, start_time=None, stop_time=None, only_good_runs=True, include_overlapping=True):
        # type: (Optional[str], Optional[str], bool, bool) -> None
        """Get runs in an interval of time
        """

        if not self._batch_mode:
            self._get_configuration()
            only_good_runs = self._builder.tkvariables.__getitem__('only_good_runs').get()
            include_overlapping = self._builder.tkvariables.__getitem__('include_overlapping').get()
            start_time, stop_time = wagascianpy.viewer.utils.get_time_interval_members(self._builder)
        self._database_sanity_check()

        wagascianpy.database.wagascidb.WagasciDataBase.wagasci_lib = self._config.global_configuration.wagasci_libdir()
        with wagascianpy.database.wagascidb.WagasciDataBase(
                repo_location=self._config.wagascidb.wagasci_repository(),
                db_location=self._config.wagascidb.wagasci_database(),
                is_borg_repo=self._config.wagascidb.repository_type() == RepositoryType.Borg,
                update_db=Configuration.viewer.update_wagasci_database(),
                rebuild_db=Configuration.viewer.rebuild_wagasci_database()) as database:
            self._records = database.get_time_interval(datetime_start=start_time,
                                                       datetime_stop=stop_time,
                                                       only_good=only_good_runs,
                                                       include_overlapping=include_overlapping)

            if not self._batch_mode:
                wagascianpy.viewer.show_run_info.make_records_table(config=self._config,
                                                                    builder=self._builder,
                                                                    records=self._records)
            else:
                for record in self._records:
                    wagascianpy.database.wagascidb.WagasciRunRecord(record).pretty_print()

    def get_run_interval(self, start_run=None, stop_run=None, only_good_runs=True):
        # type: (Optional[int], Optional[int], bool) -> None
        """Get runs in an between two runs
        """
        if not self._batch_mode:
            self._get_configuration()
            only_good_runs = self._builder.tkvariables.__getitem__('only_good_runs').get()
            start_run = self._builder.tkvariables.__getitem__('start_run').get()
            stop_run = self._builder.tkvariables.__getitem__('stop_run').get()
        assert start_run is not None and stop_run is not None, "Please specify start run and stop run"
        self._database_sanity_check()

        wagascianpy.database.wagascidb.WagasciDataBase.wagasci_lib = self._config.global_configuration.wagasci_libdir()
        with wagascianpy.database.wagascidb.WagasciDataBase(
                repo_location=self._config.wagascidb.wagasci_repository(),
                db_location=self._config.wagascidb.wagasci_database(),
                is_borg_repo=self._config.wagascidb.repository_type() == RepositoryType.Borg,
                update_db=Configuration.viewer.update_wagasci_database(),
                rebuild_db=Configuration.viewer.rebuild_wagasci_database()) as database:
            self._records = database.get_run_interval(run_number_start=start_run,
                                                      run_number_stop=stop_run,
                                                      only_good=only_good_runs)

            if not self._batch_mode:
                wagascianpy.viewer.show_run_info.make_records_table(config=self._config,
                                                                    builder=self._builder,
                                                                    records=self._records)
            else:
                for record in self._records:
                    wagascianpy.database.wagascidb.WagasciRunRecord(record).pretty_print()

    def get_all(self, only_good_runs=True):
        # type: (bool) -> None
        """Get all WAGASCI runs
        """
        if not self._batch_mode:
            self._get_configuration()
            only_good_runs = self._builder.tkvariables.__getitem__('only_good_runs').get()
        self._database_sanity_check()

        wagascianpy.database.wagascidb.WagasciDataBase.wagasci_lib = self._config.global_configuration.wagasci_libdir()
        with wagascianpy.database.wagascidb.WagasciDataBase(
                repo_location=self._config.wagascidb.wagasci_repository(),
                db_location=self._config.wagascidb.wagasci_database(),
                is_borg_repo=self._config.wagascidb.repository_type() == RepositoryType.Borg,
                update_db=self._config.viewer.update_wagasci_database(),
                rebuild_db=self._config.viewer.rebuild_wagasci_database()) as database:
            self._records = database.get_all(only_good=only_good_runs)

            if not self._batch_mode:
                wagascianpy.viewer.show_run_info.make_records_table(config=self._config,
                                                                    builder=self._builder,
                                                                    records=self._records)
            else:
                for record in self._records:
                    wagascianpy.database.wagascidb.WagasciRunRecord(record).pretty_print()

    def run(self):
        """Run the application
        """
        if not self._batch_mode:
            self._mainwindow.mainloop()


if __name__ == '__main__':

    # Parse shell arguments
    ARGS = wagascianpy.viewer.parse_args.parse_args(sys.argv[1:])

    # Edit the initial configuration
    wagascianpy.viewer.configuration.fill_configuration(ARGS)

    # Create application
    APP = Application(config=Configuration)

    if Configuration.viewer.batch_mode():
        # select runs
        if Configuration.run_select.get_time_interval():
            APP.get_time_interval(start_time=Configuration.run_select.start_time(),
                                  stop_time=Configuration.run_select.stop_time(),
                                  only_good_runs=Configuration.viewer.only_good_runs(),
                                  include_overlapping=Configuration.viewer.include_overlapping())
        if Configuration.run_select.get_run_interval():
            APP.get_run_interval(start_run=Configuration.run_select.start_run(),
                                 stop_run=Configuration.run_select.stop_run(),
                                 only_good_runs=Configuration.viewer.only_good_runs())
        if Configuration.run_select.get_all():
            APP.get_all(only_good_runs=Configuration.viewer.only_good_runs())

        # download
        if Configuration.analyzer_configuration.download():
            APP.download(builtin_reporter=False)

        # analysis
        APP.analyze(overwrite_flag=Configuration.analyzer_configuration.overwrite_flag())

    else:
        APP.run()
