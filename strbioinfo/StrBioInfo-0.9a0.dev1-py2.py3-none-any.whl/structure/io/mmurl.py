import gzip
import os
try:
    from urllib.request import urlopen
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import urlopen, HTTPError

from SBI.core import core
from .mmcif import mmCIF
from .mmpdb import mmPDB
from .mmxml import mmXML


class mmURL( object ):
    """Download and read protein structures direct from the PDB database.

    :param str path: When using **fetch**, allows to specify a search/download path.
    """
    def __init__( self, path ):
        self.url        = 'https://files.rcsb.org/download/{0}.{1}'
        self.downloaded = False
        self.filename   = None
        self.path       = path

    def read( self, pdb_id, format=None, clean=False ):
        """Download and read the structure file.

        :param str pdb_id: Identifier of the PDB to read.
        :param str format: Either 'pdb', 'cif' or 'xml'.
        :param bool clean: If true and the file had to be downloaded,
            it will delete the file. If it already existed it will be
            ignored.

        :return: json containing the file's data.

        :raise: HTTPError if PDB id is not found.
        """
        dformat = core.get_option('structure', 'format')
        format = dformat if format is None else format
        core.check_option('structure', 'format', format)
        if format == 'cif':
            data = mmCIF(True).read(self.fetch(pdb_id, format))
        elif format == 'pdb':
            data = mmPDB().read(self.fetch(pdb_id, format))
        elif format == 'xml':
            data = mmXML().read(self.fetch(pdb_id, format))
        if self.downloaded and clean:
            os.unlink(os.path.abspath(self.filename))
        return data

    def fetch( self, pdb_id, format=None ):
        """Download the structure file.

        :param str pdb_id: Identifier of the PDB to download.
        :param str format: Either 'pdb', 'cif' or 'xml'

        :return: Path to the downloaded file.

        :raise: ValueError if format is not known.
        :raise: HTTPError if PDB id is not found.
        """
        # format picking
        dformat = core.get_option('structure', 'format')
        format = dformat if format is None else format
        core.check_option('structure', 'format', format)

        # target file output management
        self.filename = '{0}.{1}.gz'.format(pdb_id, format.lower())
        if self.path is None:
            self.path = core.get_option('system', 'sandbox')
        self.filename = os.path.join(self.path, self.filename)
        if os.path.isfile(self.filename):
            return os.path.abspath(self.filename)

        # download file
        inpdb = urlopen(str(self.url.format(pdb_id, format.lower()))).readlines()
        with gzip.open(self.filename, 'wb') as fo:
            fo.write(b''.join(inpdb))
        self.downloaded = True
        return os.path.abspath(self.filename)
