#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 Pintaudi Giorgio

import collections
import errno
import hashlib
import inspect
import json
import os
import re
import shutil
import subprocess
import sys
from collections import OrderedDict
from typing import Optional, Dict, Any, Union

import paramiko
from scp import SCPClient
from six import string_types
from undecorated import undecorated

import wagascianpy.utils.environment

try:
    import ROOT

    ROOT.PyConfig.IgnoreCommandLineOptions = True
except ImportError:
    ROOT = False

try:
    # noinspection PyCompatibility
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping

_DEFAULT_TIMEZONE = "Asia/Tokyo"


###############################################################################
#                                 copytree                                    #
###############################################################################

def copytree(src, dst, dif_topology=None, symlinks=False, ignore=None):
    """Copy run_root_dir folder into dst folder (it does not create the dst folder
    if it does not exist)

    """
    if os.path.exists(src) and os.path.isdir(src):
        if not os.listdir(src):
            raise ValueError('Directory "%s" is empty' % src)
    else:
        raise ValueError('Directory "%s" doesn\'t exist' % src)

    dif_list = []
    dif_counter = 0
    if dif_topology is not None:
        dif_list = sorted(list(dif_topology.keys()))
    for item in sorted(os.listdir(src)):
        source_file = os.path.join(src, item)
        destination_file = os.path.join(dst, item)
        if os.path.isdir(source_file):
            shutil.copytree(source_file, destination_file, symlinks, ignore)
        else:
            if dif_topology is not None and "ecal_dif" in source_file:
                destination_file = re.sub(r"_ecal_dif_[0-9]+.raw",
                                          "_ecal_dif_%s.raw" % (str(dif_list[dif_counter])),
                                          destination_file)
                dif_counter += 1
            shutil.copy2(source_file, destination_file)


###############################################################################
#                               renametree                                    #
###############################################################################

def renametree(run_root_dir, run_name, dif_topology):
    # type:(str, str, Dict) -> None
    """
    Rename runs in folder according to topology
    :param run_root_dir: Folder where the raw data files are stored
    :param run_name: name of the run
    :param dif_topology: topology dictionary
    :return: None
    """
    if not isinstance(dif_topology, dict):
        raise ValueError("DIF topology must be a dictionary!")

    if os.path.exists(run_root_dir) and os.path.isdir(run_root_dir):
        if not os.listdir(run_root_dir):
            raise ValueError('Directory "%s" is empty' % run_root_dir)
    else:
        raise ValueError('Directory "%s" doesn\'t exist' % run_root_dir)
    topology_dif_list = sorted(list(dif_topology.keys()))
    file_dif_list = []
    for file_name in sorted(wagascianpy.utils.utils.find_files_with_ext(path=run_root_dir, extension='raw')):
        if "ecal_dif" in file_name:
            match = re.search(r"_ecal_dif_([0-9]+).raw", file_name)
            if match is not None:
                file_dif_list.append(match.group(1))
    if collections.Counter(topology_dif_list) == collections.Counter(file_dif_list):
        return
    if len(file_dif_list) != len(topology_dif_list):
        raise ValueError("Number of raw files ({}) is different from topology ({})".format(len(file_dif_list),
                                                                                           len(topology_dif_list)))
    dictionary = dict(zip(sorted(file_dif_list), sorted(topology_dif_list)))
    for file_dif_id, topology_dif_id in dictionary.items():
        old_file_name = "{}_ecal_dif_{}.raw".format(run_name, file_dif_id)
        tmp_file_name = "{}_ecal_dif_{}.raw.tmp".format(run_name, topology_dif_id)
        os.rename(os.path.join(run_root_dir, old_file_name), os.path.join(run_root_dir, tmp_file_name))
    for tmp_file_name in sorted(wagascianpy.utils.utils.find_files_with_ext(path=run_root_dir, extension='tmp')):
        new_file_name = tmp_file_name.replace('.tmp', '')
        os.rename(os.path.join(run_root_dir, tmp_file_name), os.path.join(run_root_dir, new_file_name))


###############################################################################
#                              static_vars                                    #
###############################################################################

def static_vars(**kwargs):
    """Static variables inside function for Python"""

    def decorate(func):
        """Decorator for static_vars"""
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


###############################################################################
#                                  mkdir_p                                    #
###############################################################################

def mkdir_p(path):
    """Create a directory recursively. If the directory already exists, do
    nothing

    """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


###############################################################################
#                                 join_threads                                #
###############################################################################

def join_threads(threads):
    """ Join all the threads in the list *threads*"""
    for thread in threads:
        result = thread.join()
        if result not in [0, -1]:
            print("Error number : %s" % result)
            exit(result)


###############################################################################
#                                limit_threads                                #
###############################################################################

def limit_threads(threads, max_threads):
    """Limit the number of simultaneuously running threads"""
    while len(threads) > max_threads:
        result = threads[0].join()
        if result not in [0, -1]:
            print("Error number : %s" % result)
            exit(result)
        threads.pop(0)


###############################################################################
#                              join_single_chain                              #
###############################################################################

def join_single_chain(chain_for_each_dif):
    """ Join all chains of threads for a single run """
    for dif_id, chain in chain_for_each_dif.items():
        print("JOIN DIF {} : LINK ID {} : THREAD ID {}".format(dif_id, id(chain.link), id(chain.thread)))
        result = chain.thread.join()
        if result not in [0, -1]:
            raise RuntimeError("DIF {} : Error code {}".format(dif_id, result))


###############################################################################
#                                 join_chains                                 #
###############################################################################

def join_chains(chains_for_each_run):
    """ Join all chains of threads in the list of chains """
    for run_name, chain_for_each_dif in chains_for_each_run.items():
        for dif_id, chain in chain_for_each_dif.items():
            print("JOIN DIF {} : LINK ID {} : THREAD ID {}".format(dif_id, id(chain.link), id(chain.thread)))
            result = chain.thread.join()
            if result not in [0, -1]:
                raise RuntimeError("RUN {} DIF {} : Error code {}".format(run_name, dif_id, result))


###############################################################################
#                                limit_chains                                #
###############################################################################

def limit_chains(chains_for_each_run, max_threads):
    """Limit the number of simultaneuously running threads"""
    num_threads = 0
    for chain_for_each_dif in chains_for_each_run.values():
        for chain in chain_for_each_dif.values():
            if chain.thread.is_alive():
                num_threads += 1
    for run_name, chain_for_each_dif in sorted(chains_for_each_run.items()):
        for dif_id, chain in sorted(chain_for_each_dif.items()):
            if num_threads <= max_threads:
                return
            if chain.thread.is_alive():
                result = chain.thread.join()
                num_threads -= 1
                if result not in [0, -1]:
                    raise RuntimeError("RUN {} DIF {} : Error code {}".format(run_name, dif_id, result))


###############################################################################
#                            list_dir_with_integer                            #
###############################################################################

def list_dir_with_integer(path):
    """List all directories containing an integer.

    Args:
        path: path to a directories containing other directories

    Return:
        list of tuples named 'dir_with_integer'. Each tuple contains
        two elements:
            - num eger
            - num_dir : directory name

    """
    if not os.path.exists(path) or not os.path.isdir(path):
        raise ValueError("Directory does not exists : %s" % path)
    dir_list = os.listdir(path)
    if not dir_list:
        raise ValueError("Empty directory : %s" % path)
    nums_re = re.compile(r"\d+")
    dir_with_integer = collections.namedtuple('dir_with_integer', 'num num_dir')
    result = []
    for directory in dir_list:
        if bool(nums_re.search(directory)):
            result.append(dir_with_integer(nums_re.search(directory).group(0),
                                           directory))
    return sorted(result)


###############################################################################
#                         get_immediate_subdirectories                        #
###############################################################################

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


###############################################################################
#                              find_first_match                               #
###############################################################################

def find_first_match(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


###############################################################################
#                              find_files_with_ext                            #
###############################################################################

def find_files_with_ext(path, extension):
    file_list = []
    for root, _, files in os.walk(path):
        for file_name in files:
            if file_name.lower().endswith('.%s' % extension.strip('.')):
                file_list.append(os.path.join(root, file_name))
    return file_list


###############################################################################
#                                extract_dif_id                               #
###############################################################################


def extract_dif_id(path):
    # type: (str) -> Optional[int]
    if not path:
        return None
    if isinstance(path, list):
        path = path[0]
    if isinstance(path, string_types) and ',' in path:
        path = path.split(',')[0]
    file_name = os.path.basename(path)
    try:
        dif_id = int(re.search(r'_dif_([\d]+)', file_name).group(1))
    except (IndexError, AttributeError):
        dif_id = None
    return dif_id


###############################################################################
#                            extract_raw_tree_name                            #
###############################################################################

def extract_raw_tree_name(tfile):
    # type: (Union[str, ROOT.TFile]) -> str
    """
    Find the name of the raw data TTree. The raw data TTRee name changed in the past
    so this function is here just for compatibility reasons. The new name is "raw".
    :param tfile: TFile where the TTree resides. Can be a string or a TFile object
    :return: name of the raw data TTree
    """
    if ROOT:
        if isinstance(tfile, string_types):
            tfile = ROOT.TFile(tfile)
        if tfile.GetListOfKeys().Contains("raw"):
            return "raw"
        else:
            tree_name = "tree_dif_%s" % extract_dif_id(tfile.GetName())
            if tfile.GetListOfKeys().Contains(tree_name):
                return tree_name
            else:
                raise AttributeError("TTree not found in TFile %s" % tfile.GetName())
    else:
        raise ImportError("ROOT module not found")


###############################################################################
#                              extract_user_info                              #
###############################################################################

def extract_user_info(tfile, info):
    # type: (Union[str, ROOT.TFile], str) -> Any
    """
    Extract the user info from a raw data TTree inside a TFile
    :param tfile: TFile where the TTree resides. Can be a string or a TFile object
    :param info: name of the parameter to extract
    :return: parameter value
    """
    if ROOT:
        if isinstance(tfile, string_types):
            tfile = ROOT.TFile(tfile)
        treename = extract_raw_tree_name(tfile)
        tree = getattr(tfile, treename)
        if tree.GetUserInfo().FindObject(info):
            return tree.GetUserInfo().FindObject(info).GetVal()
        else:
            raise KeyError("info {} not found in TFile".format(info))
    else:
        raise ImportError("ROOT module not found")


###############################################################################
#                            change_directory (Cd)                            #
###############################################################################

class Cd(object):
    """Context manager for changing the current working directory"""

    def __init__(self, new_path):
        self.saved_path = None
        self.new_path = os.path.expanduser(new_path)

    def __enter__(self):
        self.saved_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)


###############################################################################
#                                    which                                    #
###############################################################################

def which(program):
    """ python implementation of the which bash command"""

    def _is_exe(file_path):
        """Check if file is executable or not"""
        return os.path.isfile(file_path) and os.access(file_path, os.X_OK)

    fpath, _ = os.path.split(program)
    if fpath:
        if _is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if _is_exe(exe_file):
                return exe_file
    return None


###############################################################################
#                                 run_cmd                                     #
###############################################################################

def run_cmd(cmd):
    """ Run a shell command"""

    try:
        stdout = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exception:
        if exception.output:
            raise RuntimeError("Command cmd failed with outout : %s" % str(exception.output))
        raise RuntimeError("failed to execute command %s" % (str(cmd)))

    return str(stdout.decode())


###############################################################################
#                              run_borg_cmd                                   #
###############################################################################

def run_borg_cmd(cmdlist, check_progress=False):
    """ Run a borg command"""

    # Uncomment to debug borg
    # print(cmdlist)

    try:
        environment = dict(os.environ)
        environment["BORG_UNKNOWN_UNENCRYPTED_REPO_ACCESS_IS_OK"] = "yes"
        if check_progress:
            return subprocess.Popen(cmdlist,
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    env=environment)
        else:
            stdout = subprocess.check_output(cmdlist,
                                             shell=True,
                                             stderr=subprocess.STDOUT,
                                             env=environment)

    except subprocess.CalledProcessError as exception:
        if exception.output:
            print(exception.output)
            for line in exception.output.splitlines():
                json_out = json.loads(line)
                if json_out['levelname'] in [u'WARNING', u'ERROR', u'CRITICAL']:
                    raise RuntimeError(json_out['message'])
        raise RuntimeError("failed to execute command %s" % (str(cmdlist)))

    return str(stdout.decode())


###############################################################################
#                             create_ssh_client                               #
###############################################################################

def _create_ssh_client(hostname):
    client = paramiko.SSHClient()
    paramiko.transport.banner_timeout = 300

    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh_config = paramiko.SSHConfig()
    user_config_file = os.path.expanduser("~/.ssh/config")
    if os.path.exists(user_config_file):
        with open(user_config_file) as filename:
            ssh_config.parse(filename)
    else:
        print("SSH configuration file not found at %s" % user_config_file)

    cfg = {'hostname': hostname}

    user_config = ssh_config.lookup(cfg['hostname'])
    for ssh_cfg_name, paramiko_cfg_name in {'hostname': 'hostname',
                                            'user': 'username',
                                            'port': 'port'}.items():
        if ssh_cfg_name in user_config:
            cfg[paramiko_cfg_name] = user_config[ssh_cfg_name]

    if 'proxycommand' in user_config:
        cfg['sock'] = paramiko.ProxyCommand(user_config['proxycommand'])

    if 'identityfile' in user_config:
        cfg['key_filename'] = os.path.expanduser(user_config['identityfile'][0])
        if not os.path.exists(cfg['key_filename']):
            raise Exception("Specified IdentityFile " + cfg['key_filename'] + " for " +
                            hostname + " in ~/.ssh/config not existing anymore.")
    print("SSH configuration : %s" % cfg)
    client.connect(**cfg)
    return client


###############################################################################
#                                   scp_put                                   #
###############################################################################

def scp_put(hostname, src_path, dst_path):
    """ Copy from local to remote using SCP """
    ssh = _create_ssh_client(hostname)
    with SCPClient(ssh.get_transport()) as scp:
        scp.put(src_path, dst_path)


###############################################################################
#                                   scp_get                                   #
###############################################################################

def scp_get(hostname, src_path, dst_path):
    """ Copy from remote to local using SCP """
    ssh = _create_ssh_client(hostname)
    src_filename = os.path.basename(src_path)
    dst_filename = os.path.basename(dst_path)
    dst_dirname = os.path.dirname(dst_path)
    with Cd(dst_dirname):
        with SCPClient(ssh.get_transport()) as scpclient:
            scpclient.get(src_path)
        print("Renaming %s into %s" % (os.path.join(dst_dirname, src_filename),
                                       os.path.join(dst_dirname, dst_filename)))
        os.rename(os.path.join(dst_dirname, src_filename),
                  os.path.join(dst_dirname, dst_filename))
    if not os.path.exists(dst_path):
        raise Exception("Failed to scp from %s:%s to %s" % (hostname, src_path, dst_path))


###############################################################################
#                                 silentremove                                #
###############################################################################

def silentremove(filename):
    """Remove file quietly"""
    try:
        os.remove(filename)
    except (OSError, IOError) as error:
        if error.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred


###############################################################################
#                             silentremovedirs                                #
###############################################################################

def silentremovedirs(dirname):
    """Remove directory quietly"""
    shutil.rmtree(dirname, ignore_errors=True)


###############################################################################
#                                   sha256sum                                 #
###############################################################################

# Python program to find SHA256 hexadecimal hash string of a file
def sha256sum(filename):
    with open(filename, "rb") as f:
        filebyte = f.read()  # read entire file as bytes
        readable_hash = hashlib.sha256(filebyte).hexdigest()
        return readable_hash


###############################################################################
#                                  utf8_decorator                             #
###############################################################################

def utf8_decorator(func):
    """ decorator for encoding utf8 on all unicode arguments """

    def wrapper(*args, **kwargs):
        """ function wrapper """
        new_args = (x.encode('utf-8') if isinstance(x, string_types) else x for x in args)
        new_kwargs = {k: v.encode('utf-8') if isinstance(v, string_types) else v for k, v in kwargs.items()}
        return func(*new_args, **new_kwargs)

    return wrapper


###############################################################################
#                                  Get arguments                              #
###############################################################################

def get_arguments_ordered_dict(function):
    if sys.version_info.major >= 3:
        # noinspection PyUnresolvedReferences
        args = OrderedDict([(key, None) for key in inspect.getfullargspec(undecorated(function)).args[1:]])
    else:
        # noinspection PyDeprecation
        args = OrderedDict([(key, None) for key in inspect.getargspec(undecorated(function)).args[1:]])
    return args


###############################################################################
#                               Spill number fixer                            #
###############################################################################

def spill_number_fixer_passes_calculator(run_number):
    if run_number in range(58, 79):
        passes = {
            "1s": "FirstPassOnSteroids",
            "2s": "SecondPassOnSteroids",
            "3s": "ThirdPassOnSteroids",
            "1r": "FirstPassRegular",
            "2r": "SecondPassRegular",
            "3r": "ThirdPassRegular",
            "4r": "FourthPassRegular"
        }
    else:
        passes = {
            "1r": "FirstPassRegular",
            "2r": "SecondPassRegular",
            "3r": "ThirdPassRegular",
            "4r": "FourthPassRegular"
        }

    if run_number == 59:
        passes.pop("3s", None)
    elif run_number == 65:
        passes.pop("3s", None)
    elif run_number == 66:
        passes.pop("3s", None)

    return ','.join(list(passes.values()))
