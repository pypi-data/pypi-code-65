# Copyright (C) 2020  James Alexander Clark <james.clark@ligo.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
registrar is a utility for registering IGWN files already on storage
"""

# pylint: disable=import-error,superfluous-parens,fixme

import logging
import re
import sys
import os
import time
import threading
import traceback
from configparser import NoOptionError
import daemon
from daemon import pidfile

from rucio.client.client import Client
import rucio.rse.rsemanager as rsemgr
from rucio.common.config import config_get
from rucio.common.exception import (DataIdentifierAlreadyExists,
                                    RSEBlacklisted,
                                    DataIdentifierNotFound)

import gwrucio.utils

# Maximum number of replica dicts to send to the server
_MAX_CHUNK = 1000

# Frame/sft names follow https://dcc.ligo.org/LIGO-T010150
_IGWN_RE = \
    re.compile(r'([A-Z]+)-([A-Za-z0-9_]+)-([0-9]+)-([0-9]+).([A-Za-z]+)')

# Impose constraint on dataset names:
_DATASET_RE = re.compile(r'([A-Za-z0-9_]+)')

logging.basicConfig(
    stream=sys.stdout,
    level=getattr(
        logging,
        config_get('common',
                   'loglevel',
                   raise_exception=False,
                   default='DEBUG').upper()),
    format='%(asctime)s\t%(process)d\t%(levelname)s\t%(message)s')

GRACEFUL_STOP = threading.Event()

try:
    # FIXME: figure out a clean way to instantiate this inside a function
    # Instantiate the Client
    CLIENT = Client()
    # pylint: disable=broad-except
except Exception:
    logging.critical('Could not instantiate client: %s',
                     str(traceback.format_exc()))


def stop():
    """
    Graceful exit
    """
    GRACEFUL_STOP.set()


def cast_metadata(metadata):
    """
    Cast metadata values to appropriate types.

    E.g., gps-start-time should be an int.

    Modifies dictionary in-place by default
    """
    ints = ['gps-start-time', 'gps-end-time', 'duration']

    for meta_key in metadata:
        if meta_key in ints:
            metadata[meta_key] = int(metadata[meta_key])


def get_lfn_meta(path, common_metadata):
    """
    Create a dictionary of IGWN metadata from the filename and from global
    metadata contained in a configuration file.

    Parameters
    ----------
    :param path: Path or basename of a file which follows
        https://dcc.ligo.org/LIGO-T010150
    :type path: str
    :param common_metadata:
        Dictionary of metadata common to multiple files.  For SFTs MUST
        contain: ifo, window, and calibration
    :type common_metadata: dict
    """
    if common_metadata:
        metadata = dict(common_metadata)
    else:
        metadata = dict()

    # Parse metadata from basename
    metadata['obs'], content, metadata['gps-start-time'], \
        metadata['duration'], metadata['extension'] = \
        _IGWN_RE.match(os.path.basename(path)).groups()

    # File content
    if 'sft' in metadata['extension']:

        try:
            metadata['content'] = "_".join([metadata['ifo'],
                                            metadata['window'],
                                            metadata['calibration']])
        except KeyError:
            logging.error("File naming requires metadata: %s",
                          gwrucio.utils.REQUIRED_SFT_KEYS)

        try:
            # Check for any special tags like "Gated"
            metadata['content'] += f"_{metadata['special']}"
        except KeyError:
            pass
        metadata['content'] = metadata['content'].upper()

    elif metadata['extension'] == 'gwf':
        metadata['content'] = content

    else:
        raise ValueError("Extension %s unsupported" % metadata['extension'])

    # Ensure times are numerical
    cast_metadata(metadata)

    # Derived metadata
    metadata['gps-end-time'] = metadata['gps-start-time'] + \
        metadata['duration']

    return metadata


class ReplicaSet:
    """
    List of DIDs and their attributes to be registered
    """
    def __init__(self, pathlist, scope, rse, common_metadata=None):
        """
        Constructor for the ReplicaSet class

        :param scope: Scope for replicas
        :type scope: str
        :param pathlist: list of file paths to register
        :type pathlist: list of strings
        :param rse: RSE to register replicas at
        :type rse: str
        :param metadata: common metadata to attach to each DID
        :type metadata: dict
        """

        self.scope = scope
        self.rse = rse

        self.__pathlist = pathlist
        self.__common_metadata = common_metadata
        self._replicas = self.replica_list()

    @property
    def replicas(self):
        """
        Return the replica list
        """
        return self._replicas

    @property
    def scope(self):
        """Return Scope replicas registered at"""
        return self._scope

    @scope.setter
    def scope(self, scope):
        """Set scope for registration"""
        if scope not in (vscope for vscope in CLIENT.list_scopes()):
            raise ValueError("Scope %s does not exist" % scope)
        self._scope = scope

    @property
    def rse(self):
        """Return RSE replicas registered at"""
        return self._rse

    @rse.setter
    def rse(self, rse):
        """Set RSE for registration"""
        if rse not in [vrse['rse'] for vrse in CLIENT.list_rses()]:
            raise ValueError("RSE %s does not exist" % rse)
        self._rse = rse

    @property
    def size(self):
        """Get size of dataset"""
        return len(self._replicas)

    def replica_list(self):
        """
        Create a list of dictionaries of DID metadata

        :param pathlist: List of file paths
        :type pathlist: list of strings
        :param metadata: Dataset metadata configuration
        :type metadata: ConfigParser
        :returns: list of dictionaries with metadata
        """
        def _meta2lfn(meta):
            """
            Construct LFN from metadata
            """
            name = "-".join([meta['obs'], meta['content'],
                             str(meta['gps-start-time']),
                             str(meta['duration'])])
            return ".".join([name, meta['extension']])

        # Parse metadata
        logging.debug("Parsing LFNs for metadata")
        replica_meta_list = (get_lfn_meta(path, self.__common_metadata) for
                             path in self.__pathlist)

        # Get RSE info to determin URI
        rse_info = rsemgr.get_rse_info(self.rse)

        replicas = [{
            'scope': self.scope,
            'name': _meta2lfn(replica_meta),
            'pfn': gwrucio.utils.get_pfn(rse_info, path),
            'meta': replica_meta,
        } for path, replica_meta in zip(self.__pathlist, replica_meta_list) if
                    replica_meta['extension']]

        return replicas


class ReplicaRegister(ReplicaSet):
    """
    Register a set of replicas
    """
    def __init__(self, *args, dataset=None):
        """
        Constructor for the ReplicaRegister class: extends the ReplicaSet to
        add registration methods
        """
        # super(ReplicaRegister, self).__init__(*args)
        super().__init__(*args)
        if dataset:
            self.dataset = dataset
        self.__metadata = False

    @property
    def dataset(self):
        """Return datase replicas registered in"""
        return self._dataset

    @dataset.setter
    def dataset(self, dataset):
        """
        Sets the dataset files will be attached to.

        Name must be underscore-separated alpha-numeric characters

        Checks dataset exists and creates it if not.  A rule is added at this
        RSE if write-access is allowed.
        """
        matched = re.match(_DATASET_RE, dataset)
        if not bool(matched):
            raise ValueError("Dataset name %s does not follow %s" %
                             (dataset, _DATASET_RE))

        # Check dataset exists and create it if not
        # - Adds a rule if the RSE allows it
        try:
            CLIENT.add_dataset(scope=self.scope,
                               name=dataset,
                               rules=[{
                                   'account': CLIENT.account,
                                   'copies': 1,
                                   'rse_expression': self.rse,
                                   'grouping': 'DATASET',
                                   'lifetime': None
                               }])
            logging.info("Dataset %s added with rule at %s", dataset,
                         self.rse)
        except RSEBlacklisted:
            logging.info(
                "Dataset %s added, RSE write blacklisted on %s (no rule)",
                self.rse, dataset)
            CLIENT.add_dataset(scope=self.scope, name=dataset)
        except DataIdentifierAlreadyExists:
            logging.debug("Dataset %s already exists", dataset)

        # Set value of dataset
        self._dataset = dataset

    def add_replicas(self, logstr):
        """
        Add the replicas to the rucio database
        """
        if self.replicas:
            logging.info('%s Adding/attaching replicas', logstr)

            # list_content and list_replicas use lists of did dicts
            dids = [{key: replica[key] for key in ['scope', 'name']}
                    for replica in self.replicas]

            # Why is this function here and not in add_did_meta?
            # - because we need/want the checksums when we add replicas
            def compute_metadata(replica):
                """Retrieve metadata for an individual replica"""
                replica['bytes'] = gwrucio.utils.gfal_bytes(replica['pfn'])
                replica['adler32'] = gwrucio.utils.gfal_adler32(replica['pfn'])
                replica['md5'] = gwrucio.utils.gfal_md5(replica['pfn'])
                return replica

            # DIDs already in the database:
            new_replicas = []
            logging.debug("%s Reducing replica list", logstr)
            for rdx, replica in enumerate(self.replicas):
                logging.debug("%s Working on file %d/%d", logstr, rdx+1,
                              len(self.replicas))
                try:
                    CLIENT.get_metadata(replica['scope'], replica['name'])
                    logging.debug("%s Already exists, skipping checksums (%s)",
                                  logstr, replica['name'])
                    # DID exists
                except DataIdentifierNotFound:
                    # DID does not exist, compute metadata and get ready to add
                    replica_start_time = time.time()
                    logging.debug("%s Computing checksums for file %s", logstr,
                                  replica['pfn'])
                    compute_metadata(replica)
                    logging.debug("%s Checksums took %.fs (%s)", logstr,
                                  time.time() - replica_start_time,
                                  replica['pfn'])
                    new_replicas.append(replica)

            # Add replicas
            if new_replicas:

                # Split replica list into manageable chunks
                replica_chunks = gwrucio.utils.chunker(new_replicas,
                                                       _MAX_CHUNK)
                for chunk in replica_chunks:
                    CLIENT.add_replicas(rse=self.rse, files=chunk,
                                        ignore_availability=True)

            # Attach to dataset
            logging.info('%s Attaching any new files to %s', logstr,
                         self.dataset)

            # Check if dids are children of the current dataset
            parent = {'scope': self.scope, 'type': 'DATASET',
                      'name': self.dataset}
            dids_to_attach = [did for did in dids if parent not in
                              list(CLIENT.list_parent_dids(did['scope'],
                                                           did['name']))]
            if dids_to_attach:
                did_chunks = gwrucio.utils.chunker(dids_to_attach, _MAX_CHUNK)
                for chunk in did_chunks:
                    CLIENT.add_files_to_dataset(scope=self.scope,
                                                name=self.dataset,
                                                files=chunk)

    def add_did_meta(self, logstr):
        """
        Add did metadata.  Separate method allows us to call this independently
        of initial registration so it can be used to update DIDs.
        """
        if self.replicas:
            logging.debug("%s Adding DID metadata", logstr)

        for replica in self.replicas:
            _ = [
                CLIENT.set_metadata(scope=self.scope,
                                    name=replica['name'],
                                    key=key,
                                    value=replica['meta'][key])
                for key in replica['meta'].keys()
            ]


def registrar(didset=None, thread_info=None, add_files=True):
    """
    Sequence of operations to register a dataset
    """
    try:
        prepend_str = 'Thread [%i/%i] :' % thread_info
        if add_files:
            # add_replicas will skip regisration of old files but will ensure
            # orphaned files get attached to a dataset
            didset.add_replicas(prepend_str)
        didset.add_did_meta(prepend_str)
    # pylint: disable=broad-except
    except Exception:
        logging.critical('%s %s', prepend_str, str(traceback.format_exc()))


def registration(config, online=True):
    """
    Principal operations

    1. Identify input files
    2. Parse file metadata and create collections of DIDs
    3. Compute file metadata and register for each set of DIDs

    :param diskcache: List of file paths
    :type pathlist: list of strings
    :param metadata: Dataset metadata configuration
    :type metadata: ConfigParser
    :returns: list of dictionaries with metadata

    """
    # Start timer
    global_start_time = time.time()

    while online:
        local_start_time = time.time()

        # Get files to register
        diskcache_path = config['instance']['diskcache_dump']

        # Diskcache behaviors:
        #   Feed a PFN list - if lines in PFN list match the regex, we get a
        #   diskcache read error, falls back to normal file read
        #   If lines in PFN list do not match the regex, we get an empty list

        # Scenario: use PFN list where regex not in list (mismatched list and
        # ini)
        #   won't match the regex: empty list, no registration

        # Scenario: use diskcache for the wrong kind of file
        #   won't match the regex: empty list

        # Scenario: feed PFN list with matching regex
        #   diskcache read fails, falls back to parsing as list

        # i.e., the only time diskcache reading fails, and we fall back to
        # directly interpreting the PFN list, is if we provide a PFN list in
        # which diskcache finds matching file types

        try:
            filepaths, gps_end_time = gwrucio.utils.read_disk_cache(
                diskcache_path, config)
        except ValueError:
            logging.critical("Diskcache read failed, parsing %s as PFN list",
                             diskcache_path)

            with open(diskcache_path, 'r') as pfnfile:
                filepaths = pfnfile.read().splitlines()

        logging.info("Found %d matching files", len(filepaths))

        # Parse configuration
        try:
            dataset = config['global']['dataset']
        except NoOptionError:
            logging.warning('No dataset specified')
            dataset = None

        try:
            did_metadata = dict(config['common-metadata'])
        except NoOptionError:
            logging.warning('No common metadata will be applied to these DIDs')
            did_metadata = dict()

        # Ensure we only have useful threads
        threads = config['instance'].getint('threads')
        if threads > len(filepaths):
            threads = len(filepaths)

        # Generate replica sets for each thread
        didsets = (ReplicaRegister(filegroup,
                                   config['global']['scope'],
                                   config['instance']['rse'],
                                   did_metadata,
                                   dataset=dataset)
                   for filegroup in gwrucio.utils.grouper(filepaths, threads))

        # Initialise threads
        threads = [
            threading.Thread(target=registrar,
                             kwargs={
                                 'didset': didset,
                                 'thread_info': (idx + 1, threads)
                             }) for idx, didset in enumerate(didsets)
        ]

        # Start threads
        _ = [thread.start() for thread in threads]
        logging.debug('waiting for interrupts')

        # Wait for threads to finish
        while threads:
            threads = [
                thread.join() for thread in threads
                if thread and thread.isAlive()
            ]

        # Stop timer for this iteration
        logging.info("This iteration took: %-0.4f sec.",
                     (time.time() - local_start_time))

        # Update the running total uptime
        total_uptime = time.time() - global_start_time

        # Stop the loop unless we're running in online mode
        if not config['instance'].getboolean('online'):
            online = False
        # elif total_uptime > max_uptime:
        else:
            # Update minimum-gps for next loop
            config.set('data', 'minimum-gps', str(gps_end_time))

            logging.info("Going to sleep for %s sec.",
                         config['instance']['sleep_interval'])
            time.sleep(config['instance'].getfloat('sleep_interval'))

    # Stop timer
    logging.info("Total uptime: %-0.4f sec.",
                 total_uptime)


def run(config):
    """
    Run registration
    """
    daemon_mode = config['instance'].getboolean('daemon')
    if daemon_mode:
        # stdout, stderr -> log file
        outfile = open(config['instance']['log_file'], 'w')
        errfile = outfile
    else:
        # running in foreground, log to screen
        outfile = sys.stdout
        errfile = sys.stderr

    pfile = pidfile.TimeoutPIDLockFile(config['instance']['pid_file'])

    online = True
    with daemon.DaemonContext(detach_process=daemon_mode,
                              pidfile=pfile,
                              stdout=outfile,
                              stderr=errfile):
        registration(config, online)
