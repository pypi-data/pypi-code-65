# -*- coding: utf-8 -*-
"""
.. codeauthor:: Jaume Bonet <jaume.bonet@gmail.com>

.. affiliation::
    Structural BioInformatics Lab <sbi.upf.edu>
    Baldo Oliva <baldo.oliva@upf.edu>

.. class:: PDBeChemLink
"""

# Standard Libraries
import ftplib
import os
import tarfile

# External Libraries
import requests
import six
from tqdm import tqdm
import pandas as pd

# This Library
import SBI.core as core
from SBI.structure.io import mmCIF

if six.PY2:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse


__all__ = ['PDBeChemLink']


class PDBeChemLink( object ):
    """Controls the download and parsing of **PDBeChem database**.

    .. note::
        This functionality depends on the :ref:`global configuration options <configuration>` ``db.pdbechem``.
        The value for this variable can be a local or remote ``tar.gz`` file. For remote, be sure to add header
        ``http`` or ``ftp`` to the url. The target is assigned on object instantiation; thus,
        changes applied to the global variable after that will not take effect in a given instance
        of the :class:`.PDBeChemLink`.

    :raises:
        :ValueError: If the database source cannot be reached.
    """
    def __init__( self ):
        self.__name__ = 'databases.PDBeChemlink'
        self._target = core.get_option('db', 'pdbechem')
        if not self.is_source_local and not self.is_source_remote:
            raise ValueError('{0} cannot reach source {1}'.format(self.__name__, self._target) )

    # Boolean Checks
    @property
    def is_source_local( self ):
        """Check if source is an *existing* local file

        :return :class:`bool`
        """
        return os.path.isfile(self._target)

    @property
    def is_source_remote( self ):
        """Check if source is an *existing* remote file

        :return :class:`bool`
        """
        url = urlparse(self._target)
        if url.scheme == 'http':
            return requests.get(self._target).status_code == requests.codes.ok
        elif url.scheme == 'ftp':
            s = ftplib.FTP(url.netloc)
            s.login()
            try:
                s.size(url.path)
            except ftplib.error_perm:
                return False
            return True
        else:
            return False

    # Methods
    def get_database( self, instances=None ):
        """Retrieve content from the database into a :class:`~pandas.DataFrame`.

        .. note::
            This functionality depends on the :ref:`global configuration options <configuration>` ``io.overwrite``.

        :param instances: If specified, only load the requested instances of the database.
        :type instances: Union[:class:`str`, :func:`list` of :class:`str`]

        :return: :class:`~pandas.DataFrame` - Content data of the database

        :raise:
            :IOError: If trying to download from remote and a local version exists. Can be
                avoided by setting ``io.overwrite`` global option to :data:`True`.
            :IOError: If the input is not a ``tar.gz`` file.
        """
        local_file = self._download()
        if not tarfile.is_tarfile(local_file):
            raise IOError('Expected input should be a tar.gz file')
        if instances is not None:
            instances = ['mmcif/' + _.upper() + ".cif" for _ in instances]

        parser = mmCIF(monoliners=True)
        tar = tarfile.open(local_file, 'r:gz')
        data = None
        all_names = tar.getnames()
        if instances is not None:
            all_names = sorted(list(set(all_names).intersection(set(instances))))
        for name in tqdm(all_names, desc='PDBeChem'):
            fhandle = tar.extractfile(tar.getmember(name))
            if fhandle:
                info = parser._from_filehandle(fhandle)
                info = info[info.keys()[0]]['_chem_comp']
                if data is not None:
                    data = {key: value + data[key] for key, value in info.iteritems()}
                else:
                    data = info

        df = pd.DataFrame(data)
        df['type'] = df['type'].str.upper()
        df['mon_nstd_parent_comp_id'] = df['mon_nstd_parent_comp_id'].str.upper()
        return df

    # Private Methods
    def _download( self ):
        if self.is_source_local:
            return self._target

        url = urlparse(self._target)
        local_file = 'mmcif.tar.gz'
        if not os.path.isfile(local_file) or core.get_option('io', 'overwrite') is True:
            if url.scheme == 'http':
                r = requests.get(url, stream=True)
                with open(local_file, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
            if url.scheme == 'ftp':
                s = ftplib.FTP(url.netloc)
                s.login()
                s.cwd(os.path.split(url.path)[0])
                s.retrbinary("RETR " + os.path.split(url.path)[1], open(local_file, 'wb').write)
            return local_file
        else:
            raise IOError('mmcif.tar.gz already exists in this location. Unable to overwrite')
