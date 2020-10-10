#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 Pintaudi Giorgio

import os
import subprocess

from six import string_types
from typing import Dict, Union, Optional

import wagascianpy.program.program
import wagascianpy.utils.utils


class ProgramBuilder(object):
    """
    The ProgramBuilder interface specifies methods for creating the different parts of
    a program
    """

    def __init__(self, wagasci_lib=None):
        # type: (Optional[str]) -> None
        """
        :param wagasci_lib: path to the directory containing the WAGASCI library
        """
        self._wagasci_lib = wagasci_lib
        self._program = wagascianpy.program.program.Program(self._wagasci_lib)

    @property
    def program(self):
        my_program = self._program
        self.reset()
        return my_program

    def reset(self):
        # type: (...) -> None
        """
        Reset the program object
        :return: None
        """
        self._program = wagascianpy.program.program.Program(self._wagasci_lib)

    def add_decoder(self, **kwargs):
        # type: (...) -> None
        """
        Add the wgDecoder analyzer to the list of analyzers of the program
        :param kwargs: arguments to be passed to wgDecoder
        :return: None
        """
        self._program.add_step("decoder", **kwargs)

    def add_bcid_distribution(self, **kwargs):
        # type: (...) -> None
        """
        Create the BCID distribution plots
        :param kwargs: arguments to pass to the BCID distribution analyzer
        :return: None
        """
        self._program.add_step("bcid_distribution", **kwargs)

    def add_adc_distribution(self, **kwargs):
        # type: (...) -> None
        """
        Create the ADC distribution plots
        :param kwargs: arguments to pass to the ADC distribution analyzer
        :return: None
        """
        self._program.add_step("adc_distribution", **kwargs)

    def add_spill_number_fixer(self, **kwargs):
        # type: (...) -> None
        """
        Add the wgSpillNumberFixer analyzer to the list of analyzers of the program
        :param kwargs: arguments to be passed to wgSpillNumberFixer
        :return: None
        """
        self._program.add_step("spill_number_fixer", **kwargs)

    def add_beam_summary_data(self,
                              bsd_database_location,
                              bsd_repository_location,
                              download_bsd_database_location,
                              download_bsd_repository_location,
                              t2krun,
                              **kwargs):
        # type: (str, str, str, str, int, ...) -> None
        if ':' in bsd_database_location:
            if len(bsd_database_location.split(':', 1)) != 2:
                raise ValueError("Invalid database location : %s" % bsd_database_location)
            hostname = bsd_database_location.split(':', 1)[0]
            remote_db_path = bsd_database_location.split(':', 1)[-1]
            local_db_path = download_bsd_database_location
            print("Copying remote database %s into location %s" % (remote_db_path, local_db_path))
            wagascianpy.utils.utils.scp_get(hostname, remote_db_path, local_db_path)
        else:
            local_db_path = bsd_database_location
        if not os.path.exists(local_db_path):
            raise EnvironmentError("Local BSD database not found at %s" % local_db_path)

        if ':' in bsd_repository_location:
            if len(bsd_repository_location.split(':', 1)) != 2:
                raise ValueError("Invalid repository location : %s" % bsd_repository_location)
            remote_repo_path = bsd_repository_location
            local_repo_path = download_bsd_repository_location
            print("Copying remote repository %s into location %s" % (remote_repo_path, local_repo_path))
            rsync = wagascianpy.utils.utils.which("rsync")
            if rsync is None:
                raise RuntimeError("rsync program not found")
            try:
                remote = "{}/t2krun{}/*".format(remote_repo_path, t2krun)
                local = "{}/t2krun{}/".format(local_repo_path, t2krun)
                wagascianpy.utils.utils.mkdir_p(local)
                subprocess.check_output([rsync, "-a", "-essh", remote, local])
            except subprocess.CalledProcessError as exception:
                raise RuntimeError("Error while copying the remote repository %s into the "
                                   "local directory %s : %s" % (remote_repo_path, local_repo_path, str(exception)))
        else:
            local_repo_path = bsd_repository_location
        if not os.path.exists(local_repo_path):
            raise EnvironmentError("Local BSD repository not found at %s" % local_repo_path)

        self._program.add_step("beam_summary_data",
                               bsd_database=local_db_path,
                               bsd_repository=local_repo_path,
                               **kwargs)

    def add_temperature(self, **kwargs):
        # type: (...) -> None
        """
        Add the wgTemperature analyzer to the list of analyzers of the program
        :param kwargs: arguments to be passed to wgTemperature
        :return: None
        """
        self._program.add_step("temperature", **kwargs)

    def add_data_quality(self, **kwargs):
        # type: (...) -> None
        """
        Add the wgDataQuality analyzer to the list of analyzers of the program
        :param kwargs: arguments to be passed to wgDataQuality
        :return: None
        """
        self._program.add_step("data_quality", **kwargs)

    @property
    def run_location(self):
        # type: (...) -> Dict[str, str]
        """
        Get the input runs dictionary
        :return: input runs dictionary (key: run name, value: run path)
        """
        return self._program.get_run_location()

    @run_location.setter
    def run_location(self, run_dict):
        # type: (Dict[str, str]) -> None
        """
        Set the input runs dictionary
        :param run_dict: input runs dictionary (key: run name, value: run path)
        :return: None
        """
        self._program.set_run_location(run_dict)

    @property
    def save_location(self):
        # type: (...) -> Dict[str, str]
        """
        Get a custom location where to store each run decoded data.
        :return: Dictionary where the key is the run name and the value is the path of the folder where the decoded
                 data is to be stored

        """
        return self._program.get_save_location()

    @save_location.setter
    def save_location(self, save_location):
        # type: (Union[str, Dict[str, str]]) -> None
        """
        Set a custom location where to store each run decoded data.
        :param save_location: Dictionary where the key is the run name and the value is the path of the folder where the
        decoded data is to be stored, or top directory where all the output directories will be created. In case only
        the top directory is specified, the same directory structure of the input runs is recreated for the output.
        :rtype: None
        """
        if not save_location:
            raise ValueError("Save location cannot be empty")
        if not os.path.exists(save_location):
            wagascianpy.utils.utils.mkdir_p(save_location)
        save_dict = {}
        if isinstance(save_location, dict):
            save_dict = save_location
        elif isinstance(save_location, string_types):
            run_dict = self._program.get_run_location()
            for run_name in run_dict:
                save_dict[run_name] = os.path.join(save_location, run_name)
        self._program.set_save_location(save_dict)

    @property
    def multiple_runs_analyzer_save_location(self):
        # type: (...) -> str
        """
        In case of analyzers which need to analyze multiple runs at once and store the results in another directory,
        the user needs to specify it. One example is the wgDataQuality program that needs to store the gain and dark
        noise history TTrees in some external directory.
        :return: output directory for analyzers that process multiple runs
        """
        return self._program.multiple_runs_analyzer_save_location

    @multiple_runs_analyzer_save_location.setter
    def multiple_runs_analyzer_save_location(self, save_location):
        # type: (str) -> None
        """
        In case of analyzers which need to analyze multiple runs at once and store the results in another directory,
        the user needs to specify it. One example is the wgDataQuality program that needs to store the gain and dark
        noise history TTrees in some external directory.
        :param save_location: output directory for analyzers that process multiple runs
        :return: None
        """
        self._program.multiple_runs_analyzer_save_location = save_location

    def output_dir_same_as_input(self):
        # type: (...) -> None
        """
        Set the output directory as the same as the input directory
        :return: None
        """
        self._program.output_dir_same_as_input()

    def do_not_stop_on_exception(self):
        # type: (...) -> None
        """
        Do not stop the program execution if an analyzer fails
        :return: None
        """
        self._program._stop_on_exception = False

    def stop_on_exception(self):
        # type: (...) -> None
        """
        Stop the program execution if an analyzer fails
        :return: None
        """
        self._program._stop_on_exception = True

    def enforce_dependencies(self):
        # type: (...) -> None
        """
        Make sure that each analyzer is called in the right order
        :return: None
        """
        self._program._enforce_dependencies = True

    def do_not_enforce_dependencies(self):
        # type: (...) -> None
        """
        Allow an analyzer to be called even if the previous one is not present
        :return: None
        """
        self._program._enforce_dependencies = False
