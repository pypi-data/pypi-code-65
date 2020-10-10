#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright 2019 Pintaudi Giorgio, Eguchi Aoi

import json
import os
import re
import subprocess

from six import string_types
from typing import Optional, Tuple, Dict, Mapping, Union

import wagascianpy.utils
from wagascianpy.analysis.analysis import WagasciAnalysis
from wagascianpy.pyrmod.pyrmod import PyrameSlowModule
from wagascianpy.utils.environment import WagasciEnvironment

_DETECTORS = {'wallmrd_top_north': {"1": {"1": {"1-3": 32}}},
              'wallmrd_bottom_north': {"1": {"2": {"1-3": 32}}},
              'wallmrd_top_south': {"1": {"3": {"1-3": 32}}},
              'wallmrd_bottom_south': {"1": {"4": {"1-3": 32}}},
              'wagasci_top_upstream': {"2": {"1": {"1-20": 32}}},
              'wagasci_side_upstream': {"2": {"2": {"1-20": 32}}},
              'wagasci_top_downstream': {"2": {"3": {"1-20": 32}}},
              'wagasci_side_downstream': {"2": {"4": {"1-20": 32}}},
              'wallmrd_north': {"1": {"1": {"1-3": 32}, "2": {"1-3": 32}}},
              'wallmrd_south': {"1": {"3": {"1-3": 32}, "4": {"1-3": 32}}},
              'wagasci_upstream': {"2": {"1": {"1-20": 32}, "2": {"1-20": 32}}},
              'wagasci_downstream': {"2": {"3": {"1-20": 32}, "4": {"1-20": 32}}}}

_FULL_SETUP = "wallmrd_north|wallmrd_south|wagasci_upstream|wagasci_downstream"

_MAX_NCHIPS = 20


###############################################################################
#                              WagasciConfig                                  #
###############################################################################

class WagasciConfig(PyrameSlowModule):
    _wg_config_module_name = "wg_config"

    def __init__(self, *arg, **kwargs):
        super(WagasciConfig, self).__init__(module_name=self._wg_config_module_name, *arg, **kwargs)


###############################################################################
#                          get_topology_from_xml                              #
###############################################################################

def get_topology_from_xml(acq_config_xml, wagasci_libdir=None):
    # type: (str, Optional[str]) -> Dict
    """
    Generate topology dictionary from the Pyrame configuration XML file
    :param acq_config_xml: path to the Pyrame configuration XML file
    :param wagasci_libdir: path to the WAGASCI libraries directory
    :return: topology dictionary
    """
    env = WagasciEnvironment()
    if wagasci_libdir is None:
        wagasci_libdir = env['WAGASCI_LIBDIR']
    if not os.path.exists(wagasci_libdir):
        raise OSError("WAGASCI library directory not found!")
    wagasci_analyzer = WagasciAnalysis(wagasci_libdir)
    topology_string, pointer = wagasci_analyzer.get_dif_topology(acq_config_xml)
    dif_topology = json.loads(topology_string)
    wagasci_analyzer.free_topology(pointer)
    del wagasci_analyzer
    return dif_topology


###############################################################################
#                          create_acq_config_xml                              #
###############################################################################

def create_acq_config_xml(topology,  # type: str
                          acq_config_path=None,  # type: Optional[str]
                          acq_config_xml=None,  # type: Optional[str]
                          running_dir=None,  # type: Optional[str]
                          run_top_dir=None,  # type: Optional[str]
                          gdcc_mac_addr=None,  # type: Optional[str]
                          dif_mapping_file=None,  # type: Optional[str]
                          mac_mapping_file=None,  # type: Optional[str]
                          simulate=False,  # type: bool
                          use_rundb=False  # type: bool
                          ):
    # type: (...) -> Tuple[int, str]
    """ Create Pyrame configuration XML file for the data taking acquisition
            :param topology: topology string
            :param acq_config_path: directory where to create the Pyrame XML configuration file
            :param acq_config_xml: file name of the Pyrame XML configuration file
            :param running_dir: directory were the data is temporarily stored during data acquisition
            :param run_top_dir: directory were the data is copied after data acquisition
            :param gdcc_mac_addr: GDCC MAC address string
            :param dif_mapping_file: JSON file containing the mapping between DIF ID number and GDCC port number
            :param mac_mapping_file: JSON file containing the mapping between GDCC ID number and GDCC MAC address
            :param simulate: in the configuration file set the simulation fields to true.
             Different from the Pyrame module call simulation.
            :param use_rundb: If set the Pyrame rundb module is activated

    """

    _conf_string = r'wg_config('
    for var_name, var_value in locals().items():
        if var_value not in [None, ""] and not var_name.startswith('_'):
            if isinstance(var_value, string_types):
                var_value = var_value.replace(',', r'\,')
            _conf_string += r'{}={},'.format(var_name, var_value)
    _conf_string.rstrip(',')
    _conf_string += r')'

    try:
        WagasciConfig(conf_string=_conf_string)
    except RuntimeError as err:
        return 0, str(err)

    return 1, "ok"


###############################################################################
#                read GDCC to DIF topology mapping file                       #
###############################################################################

def read_dif_mapping(mapping_file):
    # type: (Optional[str]) -> Dict[str, Dict[str, int]]
    """ Read the *mapping_file* containing the DIF/GDCC mapping

    # Assuming the following DIF - GDCC mapping as default:
    #
    # GDCC 1 port   -   DIF ID
    # 1                 0
    # 2                 1
    # 3                 2
    # 4                 3
    # GDCC 2 port   -   DIF ID
    # 1                 4
    # 2                 5
    # 3                 6
    # 4                 7
    """
    try:
        with open(mapping_file) as json_file:
            dif_mapping = json.load(json_file)
    except (TypeError, IOError, ValueError) as exception:
        dif_mapping = None
        print('"%s" mapping not found or invalid : %s' % (mapping_file, str(exception)))
    if not dif_mapping:
        print('Using default GDCC-DIF mapping.')
        dif_mapping = json.loads(
            '{"1":{"1":0,"2":1,"3":2,"4":3,"5":8,"6":9,"7":10}'
            ',"2":{"1":4,"2":5,"3":6,"4":7,"5":11,"6":12,"7":13}}')
    return dif_mapping


###############################################################################
#                  read GDCC MAC addresses mapping file                       #
###############################################################################

def read_mac_mapping(mapping_file):
    # type: (str) -> Dict[str, str]
    """ Read the *mapping_file* containing the GDCC to MAC address mapping

    # Assuming the following GDCC MAC mapping as default:
    #
    # GDCC 1
    # 00:0A:35:01:FE:06
    # GDCC 2
    # 00:0A:35:01:FE:01
    """
    try:
        with open(mapping_file) as json_file:
            mac_mapping_inv = json.load(json_file)
            mac_mapping = {value: key for key, value in
                           mac_mapping_inv.items()}
    except (IOError, ValueError) as exception:
        print('"%s" mapping file not found or invalid. '
              'Using default mapping : %s' % (mapping_file, str(exception)))
        mac_mapping = {"1": "00:0A:35:01:FE:06", "2": "00:0A:35:01:FE:01"}
    return mac_mapping


###############################################################################
#                                 dict_merge                                  #
###############################################################################

def dict_merge(dct, merge_dct):
    # type: (Dict, Dict) -> None
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for key in merge_dct:
        if (key in dct and isinstance(dct[key], dict)
                and isinstance(merge_dct[key], Mapping)):
            dict_merge(dct[key], merge_dct[key])
        else:
            dct[key] = merge_dct[key]


###############################################################################
#                                 get_net_if                                  #
###############################################################################

def get_net_if():
    # type: (...) -> str
    """Return the name of the network interface connected to the 192.168.10.0/24 LAN"""
    gdcc_pc_dev = None
    get_dev_command = "ip -o addr show"
    process = subprocess.Popen(get_dev_command.split(), stdout=subprocess.PIPE)
    ps_output, error = process.communicate()
    if error:
        raise ValueError("Error when looking for network interface : %s" % error)
    for line in ps_output.strip().decode().splitlines():
        if re.search("192.168.10", line):
            fields = line.strip().split()
            gdcc_pc_dev = fields[1]
            break
    if gdcc_pc_dev is None:
        print("could not find a network interface connected "
              "to the 192.168.10.0 LAN")
        gdcc_pc_dev = "eth0"
    return gdcc_pc_dev


###############################################################################
#                            parse_topology_string                            #
###############################################################################

def parse_topology_string(topology_string):
    # type: (str) -> str
    """parse topology string containing detector names
        :param topology_string: topology string
        :return parsed topology string
    """
    if topology_string == "full_setup":
        topology_string = _FULL_SETUP
    have_detector_labels = False
    topology_new = {}
    for detector, detector_topology in _DETECTORS.items():
        if detector in topology_string:
            have_detector_labels = True
            dict_merge(topology_new, detector_topology)
    if have_detector_labels:
        topology_old = topology_new.copy()
        topology_new.clear()
    else:
        topology_old = json.loads(topology_string.replace('\\', ''))
        topology_new.clear()
    for gdcc, dif_map in topology_old.items():
        topology_new[gdcc] = {}
        for dif, asu_map_old in dif_map.items():
            asu_key = next(iter(asu_map_old))
            asu_map_new = {}
            if "-" in asu_key:
                asu_list = asu_key.split("-")
                if len(asu_list) != 2:
                    raise ValueError("chip range is invalid : %s" % asu_key)
                n_channels = asu_map_old[asu_key]
                try:
                    first_asu = int(asu_list[0])
                    last_asu = int(asu_list[1])
                except ValueError:
                    raise ValueError("chip range is invalid : %s" % asu_key)
                if first_asu == last_asu or first_asu != 1 or \
                        first_asu is None or last_asu is None or \
                        last_asu - first_asu >= _MAX_NCHIPS:
                    raise ValueError("chip range is invalid : %s" % asu_key)
                for asu in range(first_asu, last_asu + 1, 1):
                    asu_map_new[str(asu)] = n_channels
            else:
                asu_map_new = asu_map_old
            topology_new[gdcc][dif] = asu_map_new
    return json.dumps(topology_new)


###############################################################################
#                          acqconfigxml_file_finder                           #
###############################################################################

def acqconfigxml_file_finder(run_root_dir, run_name):
    # type: (str, str) -> str
    env = wagascianpy.utils.environment.WagasciEnvironment()
    path1 = os.path.join(run_root_dir, run_name + ".xml")
    path2 = os.path.join(run_root_dir, os.path.basename(env['WAGASCI_ACQCONFIGDIR']), env['WAGASCI_ACQCONFIGXML'])
    path3 = os.path.join(run_root_dir, env['WAGASCI_ACQCONFIGXML'])
    if os.path.exists(path1):
        acqconfigxml = path1
    elif os.path.exists(path2):
        acqconfigxml = path2
    elif os.path.exists(path3):
        acqconfigxml = path3
    else:
        raise EnvironmentError("XML acquisition configuration file not found")
    return acqconfigxml


###############################################################################
#                              gdcc2dif_topology                              #
###############################################################################

def gdcc2dif_topology(gdcc_topology, dif_mapping_file=None):
    # type: (Union[str, Dict], Optional[str]) -> Dict
    """
    Convert GDCC topology into DIF topology
    :param gdcc_topology: GDCC topology string
    :param dif_mapping_file: path to the DIF-GDCC port mapping file
    :return: DIF topology
    """
    if isinstance(gdcc_topology, str):
        gdcc_topology = gdcc_topology.replace('\\', '')
        gdcc_topology = json.loads(gdcc_topology)
    dif_mapping = read_dif_mapping(dif_mapping_file)
    dif_topology = {}
    for gdcc, port_dic in gdcc_topology.items():
        for port, chip_dic in port_dic.items():
            dif_id = dif_mapping[gdcc][port]
            dif_topology[str(dif_id)] = {}
            for chip_id, n_channels in chip_dic.items():
                dif_topology[str(dif_id)][str(int(chip_id) - 1)] = n_channels
    return dif_topology
