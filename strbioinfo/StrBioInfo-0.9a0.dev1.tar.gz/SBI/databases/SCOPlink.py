# -*- coding: utf-8 -*-
"""
.. codeauthor:: Jaume Bonet <jaume.bonet@gmail.com>

.. affiliation::
    Structural BioInformatics Lab <sbi.upf.edu>
    Baldo Oliva <baldo.oliva@upf.edu>

.. class:: SCOPLink
"""

# Standard Libraries
from tempfile import NamedTemporaryFile
import os

# External Libraries
import requests
import pandas as pd

# This Library
import SBI.core as core


__all__ = ['SCOPLink']


class SCOPLink( object ):
    """Controls data retrieval from the databases SCOP_ and SCOP2_.

    .. note::
        This functionality depends on the :ref:`global configuration options <configuration>` ``db.scop``
        and ``db.scop2``, that point to the top level url of the downloadable files of each database.

    :param int scop_version: Define the version of SCOP to target (``1`` or ``2``).
    :param src release_version: For each SCOP versions multiple releases might exist.

    :raises:
        :ValueError: If ``scop_version`` is unrecognized.

    .. _SCOP: http://scop.mrc-lmb.cam.ac.uk/scop/
    .. _SCOP2: http://scop2.mrc-lmb.cam.ac.uk/
    """
    def __init__( self, scop_version, release_version ):
        self.__name__ = 'databases.SCOPLink'
        self._release = str(release_version)
        try:
            self._version = int(scop_version)
            if self._version not in [1, 2]:
                raise ValueError()
        except ValueError:
            raise ValueError('Unknown SCOP version {}'.format(self._version))

    def get_data( self ):
        """Retrieve data from the declared SCOP version.

        :return: :class:`~pandas.DataFrame`
        """
        if self._version == 1:
            return self._get_data_scop1()
        elif self._version == 2:
            return self._get_data_scop2()
        else:
            raise NotImplementedError

    def _get_data_scop1( self ):
        """Retrieve data from SCOP_.

        .. _SCOP: http://scop.mrc-lmb.cam.ac.uk/scop/

        :return: :class:`~pandas.DataFrame`
        """
        url = '/'.join([core.get_option('db', 'scop'), 'dir.cla.scop.txt_' + self._release])
        local_file = _retrieve_data(url)
        df = pd.read_csv(local_file.name, sep='\t', comment='#', header=None,
                         names=['domain_id', 'pdb', 'selectors', 'cluster_id', 'scop_id', 'class'])
        local_file.close()
        df[['class', 'fold', 'superfamily', 'family',
            'domain', 'species', 'entry']] = df.apply(lambda row: [x.split('=')[1] for x in row['class'].split(',')],
                                                      axis=1, result_type='expand')
        df['selectors'] = df['selectors'].str.split(',')
        df['selectors'] = df['selectors'].map(tuple)
        return df

    def _get_data_scop2( self ):
        """Retrieve data from SCOP2_.

        .. _SCOP2: http://scop2.mrc-lmb.cam.ac.uk/

        :return: :class:`~pandas.DataFrame`
        """
        url = '/'.join([core.get_option('db', 'scop2'), 'domain_segments_pdb_' + self._release])
        local_file = _retrieve_data(url)
        df = pd.read_csv(local_file.name, sep='\t', comment='#', header=None,
                         names=['scop_id', 'serial', 'pdb', 'chain', 'begin', 'end'])
        local_file.close()

        url = '/'.join([core.get_option('db', 'scop2'), 'domains2nodes_' + self._release])
        local_file = _retrieve_data(url)
        df2 = pd.read_csv(local_file.name, sep='\t', comment='#', header=None,
                          names=['scop_id', 'node_id'])
        local_file.close()

        url = '/'.join([core.get_option('db', 'scop2'), 'scop2_nodes_names_' + self._release])
        local_file = _retrieve_data(url)
        df3 = pd.read_csv(local_file.name, sep='\t', comment='#', header=None,
                          names=['node_id', 'node_name'])
        local_file.close()

        url = '/'.join([core.get_option('db', 'scop2'), 'scop2_graph_nodes_' + self._release])
        local_file = _retrieve_data(url)
        df4 = pd.read_csv(local_file.name, sep='\t', comment='#', header=None,
                          names=['node_id', 'child_id'])
        local_file.close()

        df['selectors'] = df.apply(lambda row: tuple(['{0}:{1}-{2}'.format(row['chain'], row['begin'], row['end'])]), axis=1)
        df = df.merge(df2, on='scop_id').merge(df3, on='node_id')
        df['leaf'] = df['node_id'].isin(df4['node_id'])
        df['domain_id'] = df['pdb'] + df['chain'] + df['scop_id'].map(str) + df['serial'].map(str)
        return df


def _retrieve_data( url ):
    """Download the url into a tempfile.
    """
    if core.get_option('system', 'verbose') == 2:
        print('Downloading from {} '.format(url))
    local_file = NamedTemporaryFile(delete=core.get_option('system', 'verbose') < 2)
    r = requests.get(url, stream=True)
    if r.status_code != requests.codes.ok:
        raise IOError('Remote path {} cannot be found'.format(url))
    for chunk in r.iter_content(chunk_size=1024):
        if chunk:
            local_file.write(chunk)
    if core.get_option('system', 'verbose') == 2:
        print('into temporary file {}'.format(local_file.name))
    local_file.flush()
    os.fsync(local_file.fileno())
    return local_file
