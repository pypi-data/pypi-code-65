#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 Pintaudi Giorgio

import abc
import inspect
import json
import os
import shutil
import time
from collections import OrderedDict
from enum import Enum
from typing import Any, List, Dict, Optional, Union

from recordclass import recordclass

import wagascianpy.analysis.adc_distribution
import wagascianpy.analysis.analysis
import wagascianpy.analysis.bcid_distribution
import wagascianpy.analysis.beam_summary_data
import wagascianpy.utils.acq_config_xml
import wagascianpy.utils.environment
import wagascianpy.utils.utils

# compatible with Python 2 *and* 3:
ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})
# Chain mutable tuple
Chain = recordclass('Chain', ['link', 'thread'])


class AnalyzerInputType(Enum):
    """
    Type of input of the analyzer. single_run means that the analyzer accepts a single run at a time. multiple_runs
    means that the analyzer combine the information from multiple runs.
    """
    single_run = 1,
    multiple_runs = 2


class AnalyzerThreadingType(Enum):
    """
    Multithreading capabilities of an analyzer. multi_threaded means that the analyzer can act on the input files
    concurrently. single_threaded means that it should not be more than one active thread of the analyzer at a time.
    """
    multi_threaded = 1,
    single_threaded = 2


class Analyzer(ABC):
    """
    virtual class that represents an analizer program. It is assumed that the analyzer program acts on one or
    more WAGASCI runs. The output can be a series of plots, a new ROOT file or just to modify the input ROOT file or
    a combination of those.
    """
    depends = None

    def __init__(self,
                 analyzer_name,  # type: str
                 run_name,  # type: str
                 run_root_dir,  # type: str
                 output_dir,  # type: str
                 wagasci_libdir=None,  # type: Optional[str]
                 run_number=None,  # type: Optional[int]
                 default_args=None,  # type: Optional[Dict]
                 **kwargs):

        """
        :param analyzer_name: arbitrary name of the analyzer program
        :param run_name: name of the run to analyze
        :param run_root_dir: directory where the run files are located
        :param output_dir: directory where the output files are to be saved
        :param wagasci_libdir: directory where the WAGASCI library is
        :param run_number: run number
        :param default_args: default arguments of the analyzer program
        :param kwargs: variable arguments of the analyzer program
        """
        self.name = analyzer_name
        self.run_name = run_name
        self.run_number = run_number
        self.run_root_dir = run_root_dir
        self.output_dir = output_dir
        self._wagasci_libdir = wagasci_libdir
        if self._wagasci_libdir is None:
            try:
                env = wagascianpy.utils.environment.WagasciEnvironment()
                self._wagasci_libdir = env['WAGASCI_LIBDIR']
            except KeyError:
                raise KeyError("WAGASCI_LIBDIR variable not found in the shell environment")
        if default_args:
            self.args = default_args
        else:
            self.args = OrderedDict()
        self.set_init_arguments(**kwargs)

    @abc.abstractmethod
    def _set_runtime_arguments(self, input_file):
        pass

    @abc.abstractmethod
    def spawn(self, chains):
        pass

    def get_topology(self, acq_config_xml):
        """
        Get the detector topology (DIF - CHIP - CHAN) from the XML configuration file
        :rtype: dict
        :param acq_config_xml: path to XML file containing the acquisition configuration
        :return: Detector topology dictionary
        """
        chain = wagascianpy.analysis.analysis.WagasciAnalysis(self._wagasci_libdir)
        topology_string, pointer = chain.get_dif_topology(acq_config_xml)
        chain.free_topology(pointer)
        return json.loads(topology_string.decode('utf-8'))

    def multiple_input_loop(self, input_files, chains):
        # type: (Union[List[str], List[List[str]]], Dict[int, Chain]) -> None
        """
        Analyze the input files concurrently  using the analyzer whose name is self.name and arguments are self.args
        :param input_files: input files
        :param chains: dictionary where the key is the DIF ID and the value is a Chain recordclass object.
        """
        if chains:
            if len(chains) != len(input_files):
                raise ValueError("The number of chains ({}) must be the same as the number of "
                                 "input files ({})".format(len(chains), len(input_files)))
        for input_file in sorted(input_files):
            self._set_runtime_arguments(input_file)
            dif_id = int(wagascianpy.utils.utils.extract_dif_id(input_file))
            if not isinstance(chains, dict):
                raise TypeError("The chains dictionary must be initialized upstream")
            if dif_id not in chains:
                chain = Chain
                chain.link = wagascianpy.analysis.analysis.WagasciAnalysis(self._wagasci_libdir)
                chain.thread = chain.link.spawn(self.name, **self.args)
                chains[dif_id] = chain
                time.sleep(1)
            else:
                chains[dif_id].thread = chains[dif_id].link.spawn(self.name, **self.args)
            print("Spawn thread with DIF {} : LINK ID {} : THREAD ID {}".format(dif_id, id(chains[dif_id].link),
                                                                                id(chains[dif_id].thread)))

    def single_input_loop(self, input_file, chains):
        # type: (str, Dict[int, Chain]) -> None
        """
        Analyze the input file using the analyzer whose name is self.name and arguments are self.args
        :param input_file: input file
        :param chains: dictionary where the key is the DIF ID and the value is a Chain recordclass object.
        """
        if chains and len(chains) > 1:
            raise IndexError("The method %s does not support more than one chain" %
                             inspect.currentframe().f_code.co_name)
        self._set_runtime_arguments(input_file)
        dummy_id = 0
        if not isinstance(chains, dict):
            raise TypeError("The chains dictionary must be initialized upstream")
        if dummy_id not in chains:
            chain = Chain
            chain.link = wagascianpy.analysis.analysis.WagasciAnalysis(self._wagasci_libdir)
            chain.thread = chain.link.spawn(self.name, **self.args)
            chains[dummy_id] = chain
        else:
            chains[dummy_id].thread = chains[dummy_id].link.spawn(self.name, **self.args)
        print("Spawn thread with DIF {} : LINK ID {} : THREAD ID {}".format(dummy_id, id(chains[dummy_id].link),
                                                                            id(chains[dummy_id].thread)))

    def set_init_arguments(self, **kwargs):
        """
        Set the default value of some of the analyzer program arguments
        :param kwargs: default arguments
        """
        for key, value in kwargs.items():
            if key not in self.args:
                raise KeyError("Analyzer %s does not accept argument %s" % (self.name, key))
            self.args[key] = value


class Decoder(Analyzer):
    """
    Wrapper around the wgDecoder program
    """
    name = "decoder"
    depends = None
    input_type = AnalyzerInputType.single_run
    threading_type = AnalyzerThreadingType.multi_threaded

    _default_args = wagascianpy.utils.utils.get_arguments_ordered_dict(
        wagascianpy.analysis.analysis.WagasciAnalysis.decoder)
    _default_args.update({'calibration_dir': "",
                          'overwrite_flag': False,
                          'compatibility_mode': False,
                          'enable_tdc_variables': False})

    def __init__(self, **kwargs):
        super(Decoder, self).__init__(analyzer_name=self.name, default_args=self._default_args, **kwargs)

        self.acq_config_xml = wagascianpy.utils.acq_config_xml.acqconfigxml_file_finder(
            self.run_root_dir, self.run_name)
        if not os.path.exists(self.acq_config_xml):
            raise OSError("Acquisition configuration XML file not found : %s"
                          % self.acq_config_xml)
        self._topology = self.get_topology(self.acq_config_xml)
        wagascianpy.utils.utils.renametree(run_root_dir=self.run_root_dir, run_name=self.run_name,
                                           dif_topology=self._topology)

    def _set_runtime_arguments(self, input_file):
        # type: (str) -> None
        """
        Set arguments at execution time. By execution time I mean the moment the wgDecoder program is launched
        through the spawn method.
        :param input_file: input file
        :return: None
        """
        self.args["input_file"] = input_file
        self.args["output_dir"] = self.output_dir
        dif_id = int(wagascianpy.utils.utils.extract_dif_id(input_file))
        self.args["dif"] = dif_id
        self.args["n_chips"] = len(self._topology[str(dif_id)])

    def spawn(self, chains):
        # type: (Dict[int, Chain]) -> None
        """
        Spawn the wgDecoder threads contained in the chains dict
        :param chains: dictionary where the key is the DIF ID and the value is a Chain recordclass object.
        :return: None
        """
        if os.path.isfile(self.run_root_dir) and self.run_root_dir.endswith('.raw'):
            input_files = [self.run_root_dir]
        else:
            input_files = wagascianpy.utils.utils.find_files_with_ext(self.run_root_dir, 'raw')
        if not os.path.exists(self.output_dir):
            wagascianpy.utils.utils.mkdir_p(self.output_dir)
        for xml_file in wagascianpy.utils.utils.find_files_with_ext(self.run_root_dir, 'xml'):
            try:
                shutil.copy2(src=xml_file, dst=os.path.join(self.output_dir, os.path.basename(xml_file)))
            except shutil.SameFileError:
                pass
        for log_file in wagascianpy.utils.utils.find_files_with_ext(self.run_root_dir, 'log'):
            try:
                shutil.copy2(src=log_file, dst=os.path.join(self.output_dir, os.path.basename(log_file)))
            except shutil.SameFileError:
                pass
        self.multiple_input_loop(input_files, chains)


class SpillNumberFixer(Analyzer):
    """
    Wrapper around the wgSpillNumberFixer program
    """
    name = "spill_number_fixer"
    depends = "decoder"
    input_type = AnalyzerInputType.single_run
    threading_type = AnalyzerThreadingType.single_threaded

    _default_args = wagascianpy.utils.utils.get_arguments_ordered_dict(
        wagascianpy.analysis.analysis.WagasciAnalysis.spill_number_fixer)
    _default_args.update({'output_filename': "", 'passes': "", 'offset': 0,
                          'enable_graphics': False})

    def _set_runtime_arguments(self, _):
        """
        Set arguments at execution time. By execution time I mean the moment the wgSpillNumberFixer program is launched
        through the spawn method.
        :return: None
        """
        self.args["output_filename"] = self.run_name
        self.args["passes"] = wagascianpy.utils.utils.spill_number_fixer_passes_calculator(self.run_number)

    def __init__(self, **kwargs):
        super(SpillNumberFixer, self).__init__(analyzer_name=self.name, default_args=self._default_args, **kwargs)
        self.args["input_dir"] = self.run_root_dir
        self.args["output_dir"] = self.output_dir

    def spawn(self, chains):
        """
        Spawn the wgSpillNumberFixer threads contained in the chains dict
        :param chains: dictionary where the key is the DIF ID and the value is a Chain recordclass object.
        :return: None
        """
        if not os.path.exists(self.output_dir):
            wagascianpy.utils.utils.mkdir_p(self.output_dir)
        self.single_input_loop(self.run_root_dir, chains)


class BeamSummaryData(Analyzer):
    """
    Wrapper around the wgBeamSummaryData program
    """
    name = "beam_summary_data"
    depends = "spill_number_fixer"
    input_type = AnalyzerInputType.single_run
    threading_type = AnalyzerThreadingType.single_threaded

    _default_args = wagascianpy.utils.utils.get_arguments_ordered_dict(
        wagascianpy.analysis.beam_summary_data.beam_summary_data)
    _default_args.update({'t2krun': 10,
                          'recursive': True})

    def __init__(self, **kwargs):
        super(BeamSummaryData, self).__init__(analyzer_name=self.name, default_args=self._default_args, **kwargs)

    def _set_runtime_arguments(self, input_path):
        # type: (str) -> None
        """
        Set arguments at execution time. By execution time I mean the moment the wgBeamSummaryData program is launched
        through the spawn method.
        :param input_path: input path
        :return: None
        """
        self.args["input_path"] = input_path
        if os.path.isdir(input_path):
            self.args["recursive"] = True
        else:
            self.args["recursive"] = False

    def spawn(self, chains):
        # type: (Dict[int, Chain]) -> None
        """
        Spawn the wgBeamSummaryData threads contained in the chains dict
        :param chains: dictionary where the key is the DIF ID and the value is a Chain recordclass object.
        :return: None
        """
        self.single_input_loop(self.run_root_dir, chains)


class BcidDistribution(Analyzer):
    """
    Wrapper around the bcid_distribution function
    """
    name = "bcid_distribution"
    depends = "decoder"
    input_type = AnalyzerInputType.single_run
    threading_type = AnalyzerThreadingType.single_threaded

    _default_args = wagascianpy.utils.utils.get_arguments_ordered_dict(
        wagascianpy.analysis.bcid_distribution.bcid_distribution)
    _default_args.update({'only_global': True, 'overwrite': True})

    def __init__(self, **kwargs):
        super(BcidDistribution, self).__init__(analyzer_name=self.name, default_args=self._default_args, **kwargs)

    def _set_runtime_arguments(self, input_path):
        # type: (str) -> None
        """
        Set arguments at execution time. By execution time I mean the moment the bcid distribution function  is
        executed through the spawn method.
        :param input_path: input path
        :return: None
        """
        self.args["input_path"] = input_path
        self.args["data_quality_dir"] = self.output_dir

    def spawn(self, chains):
        # type: (Dict[int, Chain]) -> None
        """
        Spawn the wgDecoder threads contained in the chains dict
        :param chains: dictionary where the key is the DIF ID and the value is a Chain recordclass object.
        :return: None
        """
        if os.path.isfile(self.run_root_dir) and self.run_root_dir.endswith('tree.root'):
            input_files = [self.run_root_dir]
        else:
            input_files = wagascianpy.utils.utils.find_files_with_ext(self.run_root_dir, 'root')
        if not os.path.exists(self.output_dir):
            wagascianpy.utils.utils.mkdir_p(self.output_dir)
        for input_file in input_files:
            self._set_runtime_arguments(input_file)
            link = wagascianpy.analysis.analysis.WagasciAnalysis(self._wagasci_libdir)
            link.bcid_distribution(**self.args)


class AdcDistribution(Analyzer):
    """
    Wrapper around the adc_distribution function
    """
    name = "adc_distribution"
    depends = "decoder"
    input_type = AnalyzerInputType.single_run
    threading_type = AnalyzerThreadingType.single_threaded

    _default_args = wagascianpy.utils.utils.get_arguments_ordered_dict(
        wagascianpy.analysis.adc_distribution.adc_distribution)
    _default_args.update({'overwrite': True})

    def __init__(self, **kwargs):
        super(AdcDistribution, self).__init__(analyzer_name=self.name, default_args=self._default_args, **kwargs)

    def _set_runtime_arguments(self, input_path):
        # type: (str) -> None
        """
        Set arguments at execution time. By execution time I mean the moment the adc distribution function  is
        executed through the spawn method.
        :param input_path: input path
        :return: None
        """
        self.args["input_path"] = input_path
        self.args["data_quality_dir"] = self.output_dir

    def spawn(self, chains):
        # type: (Dict[int, Chain]) -> None
        """
        Spawn the wgDecoder threads contained in the chains dict
        :param chains: dictionary where the key is the DIF ID and the value is a Chain recordclass object.
        :return: None
        """
        if os.path.isfile(self.run_root_dir) and self.run_root_dir.endswith('tree.root'):
            input_files = [self.run_root_dir]
        else:
            input_files = wagascianpy.utils.utils.find_files_with_ext(self.run_root_dir, 'root')
        if not os.path.exists(self.output_dir):
            wagascianpy.utils.utils.mkdir_p(self.output_dir)
        for input_file in input_files:
            self._set_runtime_arguments(input_file)
            link = wagascianpy.analysis.analysis.WagasciAnalysis(self._wagasci_libdir)
            link.bcid_distribution(**self.args)


class Temperature(Analyzer):
    """
    Wrapper around the wgTemperature program
    """
    name = "temperature"
    depends = "beam_summary_data"
    input_type = AnalyzerInputType.single_run
    threading_type = AnalyzerThreadingType.multi_threaded

    _default_args = wagascianpy.utils.utils.get_arguments_ordered_dict(
        wagascianpy.analysis.analysis.WagasciAnalysis.temperature)
    _default_args.update({'sqlite_database': "/hsm/nu/wagasci/data/temphum/mh_temperature_sensors_t2krun10.sqlite3"})

    def __init__(self, **kwargs):
        super(Temperature, self).__init__(analyzer_name=self.name, default_args=self._default_args, **kwargs)

    def _set_runtime_arguments(self, input_file):
        # type: (str) -> None
        """
        Set arguments at execution time. By execution time I mean the moment the wgTemperature program is launched
        through the spawn method.
        :param input_file: input file
        :return: None
        """
        self.args["input_file"] = input_file

    def spawn(self, chains):
        # type: (Dict[int, Chain]) -> None
        """
        Spawn the wgTemperature threads contained in the chains dict
        :param chains: dictionary where the key is the DIF ID and the value is a Chain recordclass object.
        :return: None
        """
        if os.path.isfile(self.run_root_dir) and self.run_root_dir.endswith('.root'):
            input_files = [self.run_root_dir]
        else:
            input_files = [filename for filename
                           in wagascianpy.utils.utils.find_files_with_ext(self.run_root_dir, 'root')
                           if wagascianpy.utils.utils.extract_dif_id(filename) is not None]
        self.multiple_input_loop(input_files, chains)


class DataQuality(Analyzer):
    """
    Wrapper around the wgDataQuality program
    """
    name = "data_quality"
    depends = "temperature"
    input_type = AnalyzerInputType.multiple_runs
    threading_type = AnalyzerThreadingType.multi_threaded

    _default_args = wagascianpy.utils.utils.get_arguments_ordered_dict(
        wagascianpy.analysis.analysis.WagasciAnalysis.data_quality)
    _default_args.update({'passes': 3, 'enable_plotting': False})

    def __init__(self, **kwargs):
        super(DataQuality, self).__init__(analyzer_name=self.name, default_args=self._default_args, **kwargs)
        self.data_quality_filename = self.run_name
        self.args["data_quality_dir"] = self.output_dir
        if self.run_number is not None:
            self.data_quality_filename = "{}_{}".format(self.data_quality_filename, self.run_number)

    def _set_runtime_arguments(self, input_file):
        # type: (str) -> None
        """
        Set arguments at execution time. By execution time I mean the moment the wgDataQuality program is launched
        through the spawn method.
        :param input_file: input file
        :return: None
        """
        self.args["tree_files"] = input_file
        dif_id = int(wagascianpy.utils.utils.extract_dif_id(input_file))
        self.args["data_quality_file"] = "{}_ecal_dif_{}.root".format(self.data_quality_filename, dif_id)
        self.args["dif_id"] = dif_id

    def spawn(self, chains):
        # type: (Dict[int, Chain]) -> None
        """
        Spawn the wgDataQuality threads contained in the chains dict
        :param chains: dictionary where the key is the DIF ID and the value is a Chain recordclass object.
        :return: None
        """
        if not isinstance(self.run_root_dir, list):
            self.run_root_dir = [self.run_root_dir]
        input_files_dict = {}
        topology_source = self.args["topology_source"]
        if not topology_source:
            topology_source = wagascianpy.utils.acq_config_xml.acqconfigxml_file_finder(
                self.run_root_dir[0], os.path.basename(self.run_root_dir[0]))
        self.args["topology_source"] = topology_source
        topology = self.get_topology(topology_source)
        for dif_id in topology:
            input_files_dict[dif_id] = []
            for run_dir in self.run_root_dir:
                for root_file in wagascianpy.utils.utils.find_files_with_ext(run_dir, 'root'):
                    if str(dif_id) == str(wagascianpy.utils.utils.extract_dif_id(root_file)):
                        input_files_dict[dif_id].append(root_file)
        input_files = sorted(input_files_dict.values())
        self.multiple_input_loop(input_files, chains)


class AnalyzerFactory(ABC):
    """
    Abstract factory design patter to produce Analyzer objects.
    """

    def __init__(self, **kwargs):
        """
        :param kwargs: arguments to pass to the analyzer object constructor
        """
        self._kwargs = kwargs

    @abc.abstractmethod
    def get_analyzer(self, run_root_dir, output_dir, **kwargs):
        # type: (str, str, **Any) -> None
        """
        Build analyzer (abstract method)
        :param run_root_dir: directory where the run files are stored
        :param output_dir: directory where to save the output files
        :param kwargs: additional arguments for the analyzer
        :return: None
        """
        self._kwargs.update(kwargs)


class DecoderFactory(AnalyzerFactory):
    depends = Decoder.depends
    name = Decoder.name
    input_type = Decoder.input_type
    threading_type = Decoder.threading_type

    def get_analyzer(self, run_root_dir, output_dir, **kwargs):
        # type: (str, str, **Any) -> Decoder
        """
        Build wgDecoder analyzer
        :param run_root_dir: directory where the run files are stored
        :param output_dir: directory where to save the output files
        :param kwargs: additional arguments for the analyzer
        :return: Decoder object
        """
        super(DecoderFactory, self).get_analyzer(run_root_dir=run_root_dir, output_dir=output_dir, **kwargs)
        return Decoder(run_root_dir=run_root_dir, output_dir=output_dir, **self._kwargs)


class SpillNumberFixerFactory(AnalyzerFactory):
    depends = SpillNumberFixer.depends
    name = SpillNumberFixer.name
    input_type = SpillNumberFixer.input_type
    threading_type = SpillNumberFixer.threading_type

    def get_analyzer(self, run_root_dir, output_dir, **kwargs):
        # type: (str, str, **Any) -> SpillNumberFixer
        """
        Build wgSpillNumberFixer analyzer
        :param run_root_dir: directory where the run files are stored
        :param output_dir: directory where to save the output files
        :param kwargs: additional arguments for the analyzer
        :return: Decoder object
        """
        super(SpillNumberFixerFactory, self).get_analyzer(run_root_dir=run_root_dir, output_dir=output_dir, **kwargs)
        return SpillNumberFixer(run_root_dir=run_root_dir, output_dir=output_dir, **self._kwargs)


class BeamSummaryDataFactory(AnalyzerFactory):
    depends = BeamSummaryData.depends
    name = BeamSummaryData.name
    input_type = BeamSummaryData.input_type
    threading_type = BeamSummaryData.threading_type

    def get_analyzer(self, run_root_dir, output_dir, **kwargs):
        # type: (str, str, **Any) -> BeamSummaryData
        """
        Build beam_summary_data analyzer
        :param run_root_dir: directory where the run files are stored
        :param output_dir: directory where to save the output files
        :param kwargs: additional arguments for the analyzer
        :return: Decoder object
        """
        super(BeamSummaryDataFactory, self).get_analyzer(run_root_dir=run_root_dir, output_dir=output_dir, **kwargs)
        return BeamSummaryData(run_root_dir=run_root_dir, output_dir=output_dir, **self._kwargs)


class BcidDistributionFactory(AnalyzerFactory):
    depends = BcidDistribution.depends
    name = BcidDistribution.name
    input_type = BcidDistribution.input_type
    threading_type = BcidDistribution.threading_type

    def get_analyzer(self, run_root_dir, output_dir, **kwargs):
        # type: (str, str, **Any) -> BcidDistribution
        """
        Build bcid_distribution analyzer
        :param run_root_dir: directory where the run files are stored
        :param output_dir: directory where to save the output files
        :param kwargs: additional arguments for the analyzer
        :return: Decoder object
        """
        super(BcidDistributionFactory, self).get_analyzer(run_root_dir=run_root_dir, output_dir=output_dir, **kwargs)
        return BcidDistribution(run_root_dir=run_root_dir, output_dir=output_dir, **self._kwargs)


class AdcDistributionFactory(AnalyzerFactory):
    depends = AdcDistribution.depends
    name = AdcDistribution.name
    input_type = AdcDistribution.input_type
    threading_type = AdcDistribution.threading_type

    def get_analyzer(self, run_root_dir, output_dir, **kwargs):
        # type: (str, str, **Any) -> AdcDistribution
        """
        Build adc_distribution analyzer
        :param run_root_dir: directory where the run files are stored
        :param output_dir: directory where to save the output files
        :param kwargs: additional arguments for the analyzer
        :return: Decoder object
        """
        super(AdcDistributionFactory, self).get_analyzer(run_root_dir=run_root_dir, output_dir=output_dir, **kwargs)
        return AdcDistribution(run_root_dir=run_root_dir, output_dir=output_dir, **self._kwargs)


class TemperatureFactory(AnalyzerFactory):
    depends = Temperature.depends
    name = Temperature.name
    input_type = Temperature.input_type
    threading_type = Temperature.threading_type

    def get_analyzer(self, run_root_dir, output_dir, **kwargs):
        # type: (str, str, **Any) -> Temperature
        """
        Build wgTemperature analyzer
        :param run_root_dir: directory where the run files are stored
        :param output_dir: directory where to save the output files
        :param kwargs: additional arguments for the analyzer
        :return: Decoder object
        """
        super(TemperatureFactory, self).get_analyzer(run_root_dir=run_root_dir, output_dir=output_dir, **kwargs)
        return Temperature(run_root_dir=run_root_dir, output_dir=output_dir, **self._kwargs)


class DataQualityFactory(AnalyzerFactory):
    depends = DataQuality.depends
    name = DataQuality.name
    input_type = DataQuality.input_type
    threading_type = DataQuality.threading_type

    def get_analyzer(self, run_root_dir, output_dir, **kwargs):
        # type: (str, str, **Any) -> DataQuality
        """
        Build wgDataQuality analyzer
        :param run_root_dir: directory where the run files are stored
        :param output_dir: directory where to save the output files
        :param kwargs: additional arguments for the analyzer
        :return: Decoder object
        """
        super(DataQualityFactory, self).get_analyzer(run_root_dir=run_root_dir, output_dir=output_dir, **kwargs)
        return DataQuality(run_root_dir=run_root_dir, output_dir=output_dir, **self._kwargs)

 
class AnalyzerFactoryProducer:
    """
    Abstract factory design patter to produce Analyzer objects.
    """
    _ReturnType = Union[DecoderFactory, SpillNumberFixerFactory, BeamSummaryDataFactory, TemperatureFactory,
                        DataQualityFactory, BcidDistributionFactory, AdcDistributionFactory]

    def __init__(self, wagasci_libdir=None):
        # type: (str) -> None
        """
        :param wagasci_libdir: WAGASCI library directory
        """
        self._wagasci_libdir = wagasci_libdir
        pass

    def get_factory(self, type_of_factory, **kwargs):
        # type: (str, **Any) -> _ReturnType
        """
        Return the analyzer factory of the desired type
        :param type_of_factory: name of the factory
        :param kwargs: arguments to pass to the factory constructor
        :return: AnalyzerFactory object
        """
        if type_of_factory == "decoder":
            return DecoderFactory(wagasci_libdir=self._wagasci_libdir, **kwargs)
        if type_of_factory == "spill_number_fixer":
            return SpillNumberFixerFactory(wagasci_libdir=self._wagasci_libdir, **kwargs)
        if type_of_factory == "beam_summary_data":
            return BeamSummaryDataFactory(wagasci_libdir=self._wagasci_libdir, **kwargs)
        if type_of_factory == "temperature":
            return TemperatureFactory(wagasci_libdir=self._wagasci_libdir, **kwargs)
        if type_of_factory == "data_quality":
            return DataQualityFactory(wagasci_libdir=self._wagasci_libdir, **kwargs)
        if type_of_factory == "bcid_distribution":
            return BcidDistributionFactory(wagasci_libdir=self._wagasci_libdir, **kwargs)
        if type_of_factory == "adc_distribution":
            return AdcDistributionFactory(wagasci_libdir=self._wagasci_libdir, **kwargs)
        raise NotImplementedError("Factory %s not implemented or not recognized" % type_of_factory)
