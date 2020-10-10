#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 Pintaudi Giorgio

""" Module to retrieve the data to plot (both X axis and Y axis). The data source can be a BSD file or a WAGASCI file
or a slow device data. The module is implemented using the Strategy design pattern. Each way of collecting the data
is generically called harvester and corresponds to a different strategy. """

import abc
import operator
import os
from typing import Optional, List, Any, Union, Tuple, Dict

import numpy
from six import string_types

import wagascianpy.analysis.beam_summary_data
import wagascianpy.analysis.spill
import wagascianpy.database.db_record
import wagascianpy.database.wagascidb
import wagascianpy.plotting.detector
import wagascianpy.plotting.topology
import wagascianpy.utils.utils
from wagascianpy.plotting.topology import DifIndex

# compatible with Python 2 *and* 3:
ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})


class Patron(object):
    """
    The Patron defines the interface of interest to clients.
    """

    def __init__(self, start=None, stop=None, wagasci_database=None, harvester=None):
        """
        Usually, the Patron accepts a harvester through the constructor, but
        also provides a setter to change it at runtime.
        :param start: start run or start time
        :param stop: stop run or stop time
        :param wagasci_database: wagasci database location
        :param harvester: harvester class
        """
        # type: (Optional[Union[str, int]], Optional[Union[str, int]], Optional[str], Optional[Harvester])

        self._start = start
        self._stop = stop
        self._wagasci_database = wagasci_database
        self._xdata = []
        self._ydata = []
        self._check_arguments()

        self.harvester = harvester

    def _check_arguments(self):
        # type: (...) -> None
        """
        Check that the constructor arguments are sane
        """
        if isinstance(self._start, string_types):
            try:
                self._start = wagascianpy.database.db_record.DBRecord.str2datetime(self._start)
            except ValueError as exception:
                print('Start string must be in the format "%Y/%m/%d %H:%M:%S" or a '
                      'run number (int) : ' + self._start)
                raise exception
        if isinstance(self._stop, string_types):
            try:
                self._stop = wagascianpy.database.db_record.DBRecord.str2datetime(self._stop)
            except ValueError as exception:
                print('Stop string must be in the format "%Y/%m/%d %H:%M:%S" or a '
                      'run number (int) : ' + self._stop)
                raise exception

    def is_harvester_ready(self):
        # type: (...) -> bool
        """
        Check if the harvester class has been set
        :return: true if set false otherwise
        """
        return bool(self._harvester)

    @property
    def harvester(self):
        """
        The Patron maintains a reference to one of the Harvester objects. The
        Patron does not know the concrete class of a harvester. It should work
        with all strategies via the Harvester interface.
        """
        assert self._harvester is not None, "Set data harvester before using it"
        return self._harvester

    @harvester.setter
    def harvester(self, harvester):
        """
        Usually, the Patron allows replacing a Harvester object at runtime.
        """
        self._harvester = harvester
        if harvester is not None:
            self._harvester.set_time_interval(start=self._start,
                                              stop=self._stop,
                                              wagasci_database=self._wagasci_database)

    def gather_data(self, detector_name=None, only_good=False):
        # type: (Optional[str], bool) -> Tuple[List[float], List[Any]]
        """
        Call the harvest_data method of the harvester object to gather the data to plot
        :param detector_name: name of the detector if any
        :param only_good: only gather data and runs flagged as good
        :return: two lists of equal length with X axis data and Y axis data
        """
        return self._harvester.harvest_data(detector_name=detector_name, only_good=only_good)


class Harvester(ABC):
    """
    The Harvester interface declares operations common to all supported versions of some algorithm.
    The Patron uses this interface to call the algorithm defined by the concrete Harvester.
    """

    def __init__(self, database, repository, t2krun):
        # type: (str, str, int) -> None
        """
        :param database: location of the BSD or WAGASCI database
        :param repository: location of the BSD or WAGASCI repository
        :param t2krun: number of T2K run
        """
        self._database = database
        self._repository = repository
        self._t2krun = t2krun
        self._start_time = None
        self._stop_time = None
        if self._repository is not None and not os.path.exists(self._repository):
            raise OSError("Repository directory does not exist : %s" % self._repository)
        if self._database is not None and not os.path.exists(self._database):
            raise OSError("Database file does not exist : %s" % self._database)

    def set_time_interval(self, start, stop, wagasci_database=None):
        # type: (Union[str, int], Union[str, int], Optional[str]) -> None
        """
        Set the time or run interval where to look for data
        :param start: start time or start run
        :param stop: stop time or stop run
        :param wagasci_database: location of the WAGASCI database file
        :return: None
        """
        if start is not None:
            database = wagasci_database if wagasci_database is not None else self._database
            self._start_time, self._stop_time = wagascianpy.database.wagascidb.run_to_interval(start=start, stop=stop,
                                                                                               database=database)

    @abc.abstractmethod
    def harvest_data(self, detector_name=None, only_good=False):
        # type: (Optional[str], bool) -> Tuple[List[float], List[Any]]
        """
        Gather the data to plot
        :param detector_name: name of the detector if any
        :param only_good: only gather data and runs flagged as good
        :return: two lists of equal length with X axis data and Y axis data
        """
        pass


################################################################
#                      Concrete Harvesters                     #
################################################################


class BsdHarvester(Harvester, ABC):

    def _get_spills(self):
        # type: (...) -> List[wagascianpy.analysis.spill.BsdSpill]
        """
        Read the input files and extract the info about the BSD spills
        :return: list of BsdSpill objects
        """
        return wagascianpy.analysis.beam_summary_data.get_bsd_spills(bsd_database=self._database,
                                                                     bsd_repository=self._repository,
                                                                     t2krun=self._t2krun,
                                                                     start_time=self._start_time,
                                                                     stop_time=self._stop_time)

    @abc.abstractmethod
    def harvest_data(self, detector_name=None, only_good=False):
        # type: (Optional[str], bool) -> Tuple[List[float], List[Any]]
        """
        Gather the data to plot
        :param detector_name: ignored
        :param only_good: ignored
        :return: two lists of equal length with X axis data and Y axis data
        """
        pass


class BsdPotHarvester(BsdHarvester):

    def harvest_data(self, detector_name=None, only_good=False):
        # type: (Optional[str], bool) -> Tuple[List[float], List[float]]
        """
        Gather the data to plot. X axis is time, Y axis is POT delivered by neutrino beam line
        :param detector_name: ignored
        :param only_good: ignored
        :return: two lists of equal length with X axis data and Y axis data
        """
        bsd_spills = self._get_spills()
        accumulated_pot_list = []
        accumulated_pot = 0
        timestamp_list = []
        for spill in bsd_spills:
            if spill.bsd_good_spill_flag == wagascianpy.analysis.spill.IS_GOOD_SPILL:
                accumulated_pot += spill.pot
                accumulated_pot_list.append(accumulated_pot)
                timestamp_list.append(spill.timestamp)

        return timestamp_list, accumulated_pot_list


class BsdSpillHarvester(BsdHarvester):

    def harvest_data(self, detector_name=None, only_good=False):
        # type: (Optional[str], bool) -> Tuple[List[float], List[int]]
        """
        Gather the data to plot. X axis is time, Y axis is BSD 32 bit spill number
        :param detector_name: ignored
        :param only_good: ignored
        :return: two lists of equal length with X axis data and Y axis data
        """
        bsd_spills = self._get_spills()
        spill_number_list = []
        timestamp_list = []
        for spill in bsd_spills:
            # if spill.bsd_good_spill_flag == wagascianpy.spill.IS_GOOD_SPILL:
            spill_number_list.append(spill.bsd_spill_number)
            timestamp_list.append(spill.timestamp)

        return timestamp_list, spill_number_list


class WagasciHarvester(Harvester, ABC):

    def __init__(self, topology=None, *args, **kwargs):
        # type: (Optional[wagascianpy.plotting.topology.Topology], *Any, **Any) -> None
        super(WagasciHarvester, self).__init__(*args, **kwargs)
        self._detectors = wagascianpy.plotting.detector.Detectors(enabled_detectors=topology)
        self._trees_have_been_planted = False
        self._active_branches = None

    @property
    def active_branches(self):
        # type: (...) -> List[str]
        """
        :return: list of active branches names
        """
        return self._active_branches

    @active_branches.setter
    def active_branches(self, active_branches):
        # type: (List[str]) -> None
        """
        :param active_branches: list of active branches names
        :return: None
        """
        self._active_branches = active_branches

    @staticmethod
    def _is_dif_good(record, dif_id):
        # type: (Dict[str, Any], int) -> bool
        """
        :param record: WAGASCI run record
        :param dif_id: DIF index
        :return: True if the good data flag of the DIF is set to 1, False if it set to 0
        """
        if DifIndex.is_wallmrd_north(dif_id):
            if not record["wallmrd_north_good_data_flag"]:
                return False
        elif DifIndex.is_wallmrd_south(dif_id):
            if not record["wallmrd_south_good_data_flag"]:
                return False
        elif DifIndex.is_wagasci_upstream(dif_id):
            if not record["wagasci_upstream_good_data_flag"]:
                return False
        elif DifIndex.is_wagasci_downstream(dif_id):
            if not record["wagasci_downstream_good_data_flag"]:
                return False
        return True

    @staticmethod
    def _list_root_files(run_root_dir):
        # type: (str) -> List[Tuple[str, int]]
        """
        List all the files with .root extension and extract the DIF number
        :param run_root_dir: directory to list
        :return: list of tuples where the first element is the file name and the second is the DIF number
        """
        return [(filename, wagascianpy.utils.utils.extract_dif_id(filename))
                for filename in wagascianpy.utils.utils.find_files_with_ext(run_root_dir, 'root')
                if wagascianpy.utils.utils.extract_dif_id(filename) is not None]

    def _plant_trees(self, only_good=False):
        # type: (bool) -> None
        """
        Open the input TFiles and assign a TTree object to each enabled DIF object
        :param only_good: only runs or detectors flagged as good
        :return: None
        """
        if not self._trees_have_been_planted:
            # Assign a TTree to each DIF
            with wagascianpy.database.wagascidb.WagasciDataBase(db_location=self._database, repo_location="") as db:
                records = db.get_time_interval(datetime_start=self._start_time, datetime_stop=self._stop_time,
                                               include_overlapping=False, only_good=only_good)
                for record in sorted(records, key=operator.itemgetter("run_number")):
                    for root_file, dif_id in self._list_root_files(os.path.join(self._repository, record["name"])):
                        if not only_good or self._is_dif_good(record=record, dif_id=dif_id):
                            tree_name = wagascianpy.utils.utils.extract_raw_tree_name(root_file)
                            self._detectors.get_dif(dif_id).add_tree(root_file=root_file, tree_name=tree_name)
            # Set the active branches of the TTree
            for detector in self._detectors:
                for dif in detector:
                    if dif.has_tree():
                        dif.set_active_branches(active_branches=self.active_branches)
                    else:
                        dif.disable()
        self._trees_have_been_planted = True

    def _get_wagasci_spills_from_ttree(self, raw_tree):
        # type: (Any) -> List[wagascianpy.analysis.spill.WagasciBsdSpill]
        """
        Read all the WAGASCI spills of the input TTree into a list of WagasciBsdSpill objects
        :param raw_tree: ROOT.TTree object
        :return: list of WAGASCI spills
        """
        assert raw_tree is not None, "Raw tree should be set before trying to read it"
        wagasci_spills = []
        for event in raw_tree:
            if event.spill_mode != wagascianpy.analysis.spill.WAGASCI_SPILL_BEAM_MODE:
                continue
            wagasci_spill = wagascianpy.analysis.spill.SpillFactory.get_spill("wagascibsd")
            for variable in self.active_branches:
                if not hasattr(event, variable):
                    raise AttributeError("Variable {} not found in TTree {}".format(variable,
                                                                                    raw_tree.GetFile().GetName()))
                setattr(wagasci_spill, variable, getattr(event, variable))
            wagasci_spills.append(wagasci_spill)
        return wagasci_spills

    @abc.abstractmethod
    def harvest_data(self, detector_name=None, only_good=False):
        # type: (Optional[str], bool) -> None
        """
        Open the input TTrees and read the spill information from them
        :param detector_name: name of the detector to gather data from
        :param only_good: only gather data and runs flagged as good
        :return: two lists of equal length with X axis data and Y axis data
        """
        self._plant_trees(only_good)
        assert detector_name is not None, "You must specify a detector where to harvest data from"
        dif = self._detectors.get_detector(detector_name=detector_name)
        assert isinstance(dif, wagascianpy.plotting.detector.Dif), "You should select a DIF and not a whole subdetector"
        if dif.has_tree():
            print("Extracting spills from DIF {} of detector {}".format(dif.name, detector_name))
            dif.set_spills(self._get_wagasci_spills_from_ttree(dif.get_tree()))


class WagasciPotHarvester(WagasciHarvester):

    def __init__(self, *args, **kwargs):
        super(WagasciPotHarvester, self).__init__(*args, **kwargs)
        self.active_branches = ["spill_number", "spill_mode", "fixed_spill_number", "good_spill_flag",
                                "bsd_good_spill_flag", "pot", "timestamp"]

    def harvest_data(self, detector_name=None, only_good=False):
        # type: (Optional[str], bool) -> Tuple[Optional[List[float]], Optional[List[float]]]
        """
        Return a couple of lists of equal length. The first is the X axis timestamp, the second is the Y axis POTs.
        :param detector_name: name of the detector to gather data from
        :param only_good: only gather data and runs flagged as good
        :return: two lists of equal length with X axis data and Y axis data
        """
        if "top" not in detector_name and "bottom" not in detector_name and "side" not in detector_name:
            detector_name += " top"
        super(WagasciPotHarvester, self).harvest_data(detector_name=detector_name, only_good=only_good)
        top_dif = self._detectors.get_detector(detector_name=detector_name)
        if top_dif.is_enabled():
            accumulated_pot_list = []
            accumulated_pot = 0
            timestamp_list = []
            for spill in top_dif.get_spills():
                if spill.good_spill_flag == wagascianpy.analysis.spill.IS_GOOD_SPILL \
                        and spill.bsd_good_spill_flag == wagascianpy.analysis.spill.IS_GOOD_SPILL:
                    if spill.timestamp < 0 or spill.pot < 0:
                        print("Huston there was a problem!")
                        spill.pretty_print()
                        continue
                    timestamp_list.append(spill.timestamp)
                    accumulated_pot += spill.pot
                    accumulated_pot_list.append(accumulated_pot)
            return timestamp_list, accumulated_pot_list
        return None, None


class WagasciSpillHistoryHarvester(WagasciHarvester):

    def __init__(self, *args, **kwargs):
        super(WagasciSpillHistoryHarvester, self).__init__(*args, **kwargs)
        self.active_branches = ["spill_mode", "spill_number", "timestamp"]

    def harvest_data(self, detector_name=None, only_good=False):
        # type: (Optional[str], bool) -> Tuple[Optional[List[float]], Optional[List[int]]]
        """
        Return a couple of lists: the first is the X axis timestamp, the second is the Y axis (non fixed) spill number.
        :param detector_name: name of the detector to gather data from
        :param only_good: only gather data and runs flagged as good
        :return: two lists of equal length with X axis data and Y axis data
        """
        if "top" not in detector_name and "bottom" not in detector_name and "side" not in detector_name:
            detector_name += " top"
        super(WagasciSpillHistoryHarvester, self).harvest_data(detector_name=detector_name, only_good=only_good)
        top_dif = self._detectors.get_detector(detector_name=detector_name)
        if top_dif.is_enabled():
            spill_number_list = []
            timestamp_list = []
            for spill in top_dif.get_spills():
                if spill.timestamp > 0:
                    spill_number_list.append(spill.spill_number)
                    timestamp_list.append(spill.timestamp)
            return timestamp_list, spill_number_list
        return None, None


class WagasciFixedSpillHarvester(WagasciHarvester):

    def __init__(self, *args, **kwargs):
        super(WagasciFixedSpillHarvester, self).__init__(*args, **kwargs)
        self.active_branches = ["spill_mode", "fixed_spill_number", "good_spill_flag",
                                "bsd_good_spill_flag", "timestamp"]

    def harvest_data(self, detector_name=None, only_good=False):
        # type: (Optional[str], bool) -> Tuple[Optional[List[float]], Optional[List[int]]]
        """
        Return a couple of lists: the first is the X axis timestamp, the second is the Y axis fixed spill number.
        :param detector_name: name of the detector to gather data from
        :param only_good: only gather data and runs flagged as good
        :return: two lists of equal length with X axis data and Y axis data
        """
        if "top" not in detector_name and "bottom" not in detector_name and "side" not in detector_name:
            detector_name += " top"
        super(WagasciFixedSpillHarvester, self).harvest_data(detector_name=detector_name, only_good=only_good)
        top_dif = self._detectors.get_detector(detector_name=detector_name)
        if top_dif.is_enabled():
            fixed_spill_number_list = []
            timestamp_list = []
            for spill in top_dif.get_spills():
                if spill.good_spill_flag == wagascianpy.analysis.spill.IS_GOOD_SPILL and spill.timestamp > 0:
                    if spill.fixed_spill_number < wagascianpy.analysis.spill.WAGASCI_MINIMUM_SPILL or \
                            spill.fixed_spill_number > wagascianpy.analysis.spill.WAGASCI_MAXIMUM_SPILL or \
                            spill.timestamp < 0:
                        print("WARNING! Time {} : Spill {}".format(spill.timestamp, spill.fixed_spill_number))
                    fixed_spill_number_list.append(spill.fixed_spill_number)
                    timestamp_list.append(spill.timestamp)
            return timestamp_list, fixed_spill_number_list
        return None, None


class WagasciSpillNumberHarvester(WagasciHarvester):

    def __init__(self, *args, **kwargs):
        super(WagasciSpillNumberHarvester, self).__init__(*args, **kwargs)
        self.active_branches = ["spill_mode", "spill_number"]

    def harvest_data(self, detector_name=None, only_good=False):
        # type: (Optional[str], bool) -> Tuple[Optional[List[int]], Optional[List[int]]]
        """
        Return a couple of lists: the first is the X axis event number, the second is the Y axis (non fixed) spill
        number.
        :param detector_name: name of the detector to gather data from
        :param only_good: only gather data and runs flagged as good
        :return: two lists of equal length with X axis data and Y axis data
        """
        if "top" not in detector_name and "bottom" not in detector_name and "side" not in detector_name:
            detector_name += " top"
        super(WagasciSpillNumberHarvester, self).harvest_data(detector_name=detector_name, only_good=only_good)
        top_dif = self._detectors.get_detector(detector_name=detector_name)
        if top_dif.is_enabled():
            spill_number_list = []
            event_list = []
            for counter, spill in enumerate(top_dif.get_spills()):
                spill_number_list.append(spill.spill_number)
                event_list.append(counter)
            return event_list, spill_number_list
        return None, None


class TemperatureHarvester(WagasciHarvester):

    def __init__(self, *args, **kwargs):
        super(TemperatureHarvester, self).__init__(*args, **kwargs)
        self.active_branches = ["spill_mode", "good_spill_flag", "bsd_good_spill_flag",
                                "timestamp", "temperature"]

    def harvest_data(self, detector_name=None, only_good=False):
        # type: (Optional[str], bool) -> Tuple[Optional[List[float]], Optional[List[float]]]
        """
        Return a couple of lists: the first is the X axis timestamp, the second is the Y axis temperature.
        :param detector_name: name of the detector to gather data from
        :param only_good: only gather data and runs flagged as good
        :return: two lists of equal length with X axis data and Y axis data
        """
        super(TemperatureHarvester, self).harvest_data(detector_name=detector_name, only_good=only_good)
        detector = self._detectors.get_detector(detector_name=detector_name)
        if detector.is_enabled():
            temperature_list = []
            timestamp_list = []
            for spill in detector.get_spills():
                if spill.good_spill_flag == wagascianpy.analysis.spill.IS_GOOD_SPILL and \
                        spill.bsd_good_spill_flag == wagascianpy.analysis.spill.IS_GOOD_SPILL and \
                        spill.timestamp > 0:
                    temperature_list.append(spill.temperature)
                    timestamp_list.append(spill.timestamp)
            return timestamp_list, temperature_list
        return None, None


class HumidityHarvester(WagasciHarvester):

    def __init__(self, *args, **kwargs):
        super(HumidityHarvester, self).__init__(*args, **kwargs)
        self.active_branches = ["spill_mode", "good_spill_flag", "bsd_good_spill_flag",
                                "timestamp", "humidity"]

    def harvest_data(self, detector_name=None, only_good=False):
        # type: (Optional[str], bool) -> Tuple[Optional[List[float]], Optional[List[float]]]
        """
        Return a couple of lists: the first is the X axis timestamp, the second is the Y axis humidity.
        :param detector_name: name of the detector to gather data from
        :param only_good: only gather data and runs flagged as good
        :return: two lists of equal length with X axis data and Y axis data
        """
        super(HumidityHarvester, self).harvest_data(detector_name=detector_name, only_good=only_good)
        detector = self._detectors.get_detector(detector_name=detector_name)
        if detector.is_enabled():
            humidity_list = []
            timestamp_list = []
            for spill in detector.get_spills():
                if spill.good_spill_flag == wagascianpy.analysis.spill.IS_GOOD_SPILL and \
                        spill.bsd_good_spill_flag == wagascianpy.analysis.spill.IS_GOOD_SPILL and \
                        spill.timestamp > 0:
                    humidity_list.append(spill.humidity)
                    timestamp_list.append(spill.timestamp)
            return timestamp_list, humidity_list
        return None, None


class DataQualityHarvester(Harvester, ABC):

    def __init__(self, filename, topology=None, *args, **kwargs):
        # type: (str, wagascianpy.plotting.topology.Topology, Any, Any) -> None
        """
        :param filename: name of the data quality file
        :param topology: Topology object that specifies which are the enabled DIFs
        :param args: positional arguments for the Harvester super class
        :param kwargs: keyword arguments for the Harvester super class
        """
        super(DataQualityHarvester, self).__init__(*args, **kwargs)
        self._filename = filename
        self._detectors = wagascianpy.plotting.detector.Detectors(enabled_detectors=topology)
        self._trees_have_been_planted = False
        self._active_branches = None

    @property
    def active_branches(self):
        # type: (...) -> List[str]
        return self._active_branches

    @active_branches.setter
    def active_branches(self, active_branches):
        # type: (List[str]) -> None
        self._active_branches = active_branches

    def _plant_trees(self):
        # type: (...) -> None
        """
        Open the input TFiles and assign a TTree object to each enabled DIF object
        :return: None
        """

        if not self._trees_have_been_planted:
            for root_file, dif_id in [(filename, wagascianpy.utils.utils.extract_dif_id(filename))
                                      for filename in
                                      wagascianpy.utils.utils.find_files_with_ext(self._repository, 'root')
                                      if (self._filename in filename and
                                          wagascianpy.utils.utils.extract_dif_id(filename) is not None)]:
                if self._detectors.get_dif(dif_id).is_enabled():
                    self._detectors.get_dif(dif_id).add_tree(root_file=root_file, tree_name='dq')
            for detector in self._detectors:
                for dif in detector:
                    if dif.has_tree():
                        dif.set_active_branches(active_branches=self.active_branches)
                    else:
                        dif.disable()
        self._trees_have_been_planted = True

    @abc.abstractmethod
    def harvest_data(self, detector_name=None, only_good=False):
        # type: (Optional[str], bool) -> None
        """
        Setup the TTrees where to gather data from
        :param detector_name: ignored
        :param only_good: ignored
        :return: None
        """
        self._plant_trees()


class GainHarvester(DataQualityHarvester):

    def __init__(self, *args, **kwargs):
        # type: (Any, Any) -> None
        super(GainHarvester, self).__init__(*args, **kwargs)
        self.active_branches = ["average_timestamp", "gain"]

    def harvest_data(self, detector_name=None, only_good=False):
        # type: (Optional[str], bool) -> Tuple[Optional[List[float]], Optional[List[List[float]]]]
        """
        Return a couple of lists: the first is the timestamp (X axis), the second is the list of gain for all the
        channels (Y axis).
        :param detector_name: name of the detector to gather data from
        :param only_good: ignored
        :return: two lists of equal length with X axis data and Y axis data
        """
        super(GainHarvester, self).harvest_data(detector_name=detector_name, only_good=only_good)
        time = []
        data = []
        for detector in self._detectors:
            for dif in [dif for dif in detector if dif.has_tree()]:
                print("Extracting data from DIF {} {}".format(detector.name, dif.name))
                for event in dif.get_tree():
                    if event.average_timestamp > 0.:
                        yarray = numpy.frombuffer(event.gain, dtype="float64")
                        ylist = yarray[~numpy.isnan(yarray)].tolist()
                        ylist = [i for i in ylist if i >= 0.]
                        if ylist:
                            time.append(event.average_timestamp)
                            data.append(ylist)
        return time, data


class DarkNoiseHarvester(DataQualityHarvester):

    def __init__(self, *args, **kwargs):
        # type: (Any, Any) -> None
        super(DarkNoiseHarvester, self).__init__(*args, **kwargs)
        self.active_branches = ["average_timestamp", "dark_noise"]

    def harvest_data(self, detector_name=None, only_good=False):
        # type: (Optional[str], bool) -> Tuple[Optional[List[float]], Optional[List[List[float]]]]
        """
        Return a couple of lists: the first is the timestamp (X axis), the second is the list of dark noise rate for
        all the channels (Y axis).
        :param detector_name: name of the detector to gather data from
        :param only_good: ignored
        :return: two lists of equal length with X axis data and Y axis data
        """
        super(DarkNoiseHarvester, self).harvest_data(detector_name=detector_name, only_good=only_good)
        time = []
        data = []
        for detector in self._detectors:
            for dif in [dif for dif in detector if dif.has_tree()]:
                print("Extracting data from DIF {} {}".format(detector.name, dif.name))
                for event in dif.get_tree():
                    if event.average_timestamp > 0.:
                        yarray = numpy.frombuffer(event.dark_noise, dtype="float64")
                        ylist = yarray[~numpy.isnan(yarray)].tolist()
                        ylist = [i for i in ylist if i >= 1.]
                        if ylist:
                            time.append(event.average_timestamp)
                            data.append(ylist)
        return time, data


class DataQualityTemperatureHarvester(DataQualityHarvester):

    def __init__(self, *args, **kwargs):
        # type: (Any, Any) -> None
        super(DataQualityTemperatureHarvester, self).__init__(*args, **kwargs)
        self.active_branches = ["average_timestamp", "average_temperature"]

    def harvest_data(self, detector_name=None, only_good=False):
        # type: (Optional[str], bool) -> Tuple[Optional[List[float]], Optional[List[float]]]
        """
        Return a couple of lists: the first is the timestamp (X axis), the second is the temperature (Y axis).
        :param detector_name: name of the detector to gather data from
        :param only_good: ignored
        :return: two lists of equal length with X axis data and Y axis data
        """
        super(DataQualityTemperatureHarvester, self).harvest_data(detector_name=detector_name, only_good=only_good)
        time = []
        data = []
        dif = self._detectors.get_detector(detector_name)
        print("Extracting data from DIF {} {}".format(detector_name, dif.name))
        for event in dif.get_tree():
            if event.average_timestamp > 0. and event.average_temperature > 0.:
                time.append(event.average_timestamp)
                data.append(event.average_temperature)
        return time, data
