# -*- coding: utf-8 -*-
"""
.. codeauthor:: Jaume Bonet <jaume.bonet@gmail.com>

.. affiliation::
    Structural BioInformatics Lab <sbi.upf.edu>
    Baldo Oliva <baldo.oliva@upf.edu>

.. class:: PDBLink
"""

# Standard Libraries
from subprocess import call
import os
import re
import glob

# External Libraries

# This Library
import SBI.core as core
from SBI.utils import list2file


__all__ = ['PDBLink']


class PDBLink( object ):
    """Controls the download and parsing of `Protein Data Bank <http://www.rcsb.org/>`.

    .. note::
        This functionality depends on the :ref:`global configuration options <configuration>` ``db.pdb``,
        that points to the rsync entry point on the PDB database.

    .. note::
        This functionality depends on the :ref:`global configuration options <configuration>` ``structure.format``.
        When downloading the database, it will download the requested format.

    All configuration options are set up at instantiation time and, thus, will not be affected by future changes.

    :raises:
        :ValueError: If the database source cannot be reached.
    """
    def __init__( self, local ):
        self.__name__ = 'databases.PDBlink'
        self._target  = core.get_option('db', 'pdb')
        self._format  = core.get_option('structure', 'format')
        self._subfld  = {'cif': 'mmCIF/', 'pdb': 'pdb/', 'xml': 'XML/'}[self._format]
        self._local   = os.path.abspath(local)

    def list_local( self ):
        """List all the PDB entries present in the local database.

        :return: :func:`list` of :class:`str` - assumes standard formats and excludes extensions.
        :raises:
            :IOError: If a path for the PDB entry cannot be found.
        """
        formats = re.compile('[pdb]{0,1}(\w{4})\.(?:ent|cif|pdb|xml)[\.gz]{0,1}')

        def do_search(filename, formats):
            try:
                return re.search(formats, filename).group(1)
            except AttributeError:
                # Nothing is found
                return None

        if not os.path.isdir(self._local):
            raise IOError('Unable to locate the expected local PDB.')
        return list(filter(None, [do_search(x, formats) for x in glob.glob(os.path.join(self._local, '*', '*'))]))

    def get_local( self, pdbid ):
        """Get the path of a PDB identifier in the local PDB database.

        :param str pdbid: Identifier of the PDB entry.

        :return: :class:`str` - path to the PDB entry.

        :raises:
            :IOError: If a path for the PDB entry cannot be found.
        """
        formats = {'cif': ['.cif', '{}.cif.gz'], 'pdb': ['.pdb', 'pdb{}.ent.gz', '{}.pdb.gz'], 'xml': ['.xml', '{}.xml.gz']}[self._format]
        prefolder = pdbid[1:3].lower()
        for fr in formats:
            pdb_file = os.path.join(self._local, prefolder, fr.format(pdbid.lower()))
            if os.path.isfile(pdb_file):
                return pdb_file
        raise IOError('File for the PDB code {0} cannot be found in local database {1} with format {2}.'.format(pdbid, self._local, self._format))

    def store_local_path( self, filename ):
        """Given a PDB filename, create the appropiate structure to store it following PDB directory conventions.

        :param str filename: Filename to create the path structure for.

        :return: :class:`str` - The full path for ``filename``.
        """
        prefolder = filename[1:3].lower()
        prefolder = os.path.join(self._local, prefolder)
        if not os.path.isdir(prefolder):
            os.makedirs(prefolder)
        return os.path.join(prefolder, filename)

    def download( self, status='divided', delete=True, selected=None ):
        """Create a local PDB database by ``rsync`` from the `Protein Data Bank <http://www.rcsb.org/>`.

        .. note::
            This functionality depends on the :ref:`global configuration options <configuration>` ``io.overwrite``.

        .. note::
            This functionality depends on the :ref:`global configuration options <configuration>` ``system.testing``.
            If active, only a pre-defined list of files will be downloaded. This is important to limit test time and
            disk usage.

        :param str local: Tree root path for the
        :param str status: Status of the PDB source to download. Currently available
            status are: ``divided`` for current relesases or ``obsolete``.
        :param bool delete: When :data:`True`, sync also deletions from the PDB source.
        :param selected: File with the list of structures of interest.
        :type selected: Union[:class:`str`, :func:`list` of :class:`str`]

        :raises:
            :IOError: If ``local`` path exists and ``io.overwrite`` is :data:`False`.
        """
        if not core.get_option('io', 'overwrite') and os.path.isdir(self._local):
            raise IOError('Folder {} exists and cannot be overwritten.'.format(self._local))
        if not os.path.isdir(self._local):
            os.mkdir(self._local)

        url = "/".join([self._target, status, self._subfld])
        command = ['rsync', '-rlpt', '-v', '-z']
        if selected is not None:
            selected = list2file(selected)
            command.append('--files-from={}'.format(selected))
        if delete:
            command.append('--delete')
        command.extend(['--port=33444', url, self._local])
        call(command)

    def complex_query( self, query, local ):
        """
        """
        # @TODO: Allow submission of XML queries.
        pass



# """PDBlink
#
# author: jbonet
# date:   10/2013
#
# @oliva's lab
# """
#
# """
# Import Standard Libraries
# """
# import sys, os, copy
# import subprocess
# import warnings
# import urllib
# import ftplib
#
# """
# Dependences in SBI library
# """
# from SBI               import SBIglobals
# from SBI.structure import PDB
# from SBI.beans     import Path
# from SBI.beans     import File
# from SBI.databases import PDBftp, PDBrsync
# from SBI.sequence  import Fasta
#
#
# class PDBlink(object):
#     """The PBDlink class controls the management of PDB on database level
#
#         For some functionalities, it requires rsync (in the path). Thus, it might be limited to unix-derived OS.
#
#     """
#     def __init__(self, local = None, PDBseq = None):
#         self._local    = None if local  is None else os.path.abspath(local)
#         self._PDBseq   = None if PDBseq is None else os.path.abspath(PDBseq)
#         self.__name__  = 'databases.PDBlink'    # This must be included in every class for the SBIglobals.alert()
#
#     """ATTRIBUTES"""
#     @property
#     def local(self):         return self._local
#     @local.setter
#     def local(self, value):  self._local = os.path.abspath(value)
#
#     @property
#     def PDBseq(self):        return self._PDBseq
#     @PDBseq.setter
#     def PDBseq(self, value): self._PDBseq = os.path.abspath(value)
#
#     @property
#     def localPDBs(self):
#         for pdb_file in Path.list_files(root = self.local, pattern = '*.ent.gz'):
#             yield pdb_file
#
#     @property
#     def source(self):
#         return PDBftp['show']
#
#     """BOOLEANS"""
#     @property
#     def has_local(self):    return self._local is not None
#
#     """METHODS"""
#     def get_PDBseq_filtered(self, resolution_threshold, output_file):
#         resolutions     = self.get_resolutions()
#         names           = [k for k, v in resolutions.iteritems() if float(v) <= float(resolution_threshold)]
#         sequences       = Fasta(os.path.join(self.PDBseq,'PDBseq.fa'))
#         selectedseq     = sequences.retrieve(copy.deepcopy(names), prefix_size = 4)
#         return Fasta.build_multifasta(output_file, selectedseq, True)
#
#         # outdir   = self.PDBseq if self.PDBseq is not None else os.curdir
#         # return os.path.join(outdir, 'PDBseq.{0}.fa'.format(str(resolution_threshold).replace('.','_')))
#
#     def sync_PDB(self, log_file = None):
#         if not self.has_local:
#             raise NameError('A local PDB database must be defined to sync with.')
#
#         Path.mkdir(self.local)
#
#         command = ['rsync', '-rlpt', '-v', '-z', '--port=' + PDBrsync['port'], PDBrsync['address'],  self.local]
#
#         p = subprocess.Popen(command,
#                              stdout = open(log_file,'w') if log_file is not None else subprocess.PIPE,
#                              stderr = subprocess.PIPE)
#
#         SBIglobals.alert('verbose', self, 'Executing: {0}'.format(" ".join(command)))
#
#         out, err = p.communicate()
#         if err.strip() != '':
#             raise SystemError('{0}'.format(err))
#
#     def make_PDBseq(self, log_file, resolution_threshold = None):
#         if not self.has_local:
#             raise NameError('A local PDB database must be defined to do create a PDBseq database.')
#         outdir = self.PDBseq if self.PDBseq is not None else os.curdir
#
#         Path.mkdir(self.PDBseq)
#         fasta_file = File(file_name = os.path.join(outdir, 'PDBseq.fa'),     action = 'w', overwrite = True)
#         fasta_fd   = fasta_file.descriptor
#         idx_file   = File(file_name = os.path.join(outdir, 'PDBseq.fa.idx'), action = 'w', overwrite = True)
#         idx_fd     = idx_file.descriptor
#         # if resolution_threshold is not None:
#         #     filtered_file_name = self.get_PDBseq_filtered(resolution_threshold)
#         #     filtered_file      = File(file_name = filtered_file_name, action = 'w', overwrite = True)
#         #     filtered_fd        = filtered_file.descriptor
#         #     resolutions        = self.get_resolutions(resolution_threshold = resolution_threshold)
#         log_file   = File(file_name = log_file, action = 'w', overwrite = True)
#         log_idx    = log_file.descriptor
#
#         for pdb_file in self.localPDBs:
#             log_idx.write("Reading File: {0}\n".format(pdb_file))
#             newPDB = PDB(pdb_file = pdb_file, dehydrate = True)
#             fasta_idx = newPDB.FASTA_IDX(nucleotide=False)
#             if len(fasta_idx['FASTA']) != len(fasta_idx['IDX']):
#                 log_idx.write('ERROR!!!!! Number of fastas and indexes are different for pdb {0}!!\n'.format(newPDB.id))
#             if len(fasta_idx['FASTA']) > 0:
#                 log_idx.write('\tPrinting FASTA and IDX...\n')
#             else:
#                 log_idx.write('\tProblably just a nucleotide PDB...\n')
#             for c in range(len(fasta_idx['FASTA'])):
#                 sequence = fasta_idx['FASTA'][c].split('\n')[1]
#                 sequence = sequence.replace('X','').replace('x','')
#                 if len(sequence) > 0:
#                     fasta_fd.write(fasta_idx['FASTA'][c] + "\n")
#                     if resolution_threshold is not None and newPDB.id in resolutions and not newPDB.is_all_ca:
#                         filtered_fd.write(fasta_idx['FASTA'][c] + "\n")
#                     idx_fd.write(fasta_idx['IDX'][c] + "\n")
#             del(newPDB)
#
#         #CLOSE & END
#         fasta_file.close()
#         idx_file.close()
#         if resolution_threshold is not None:
#             filtered_fd.close()
#
#     def get_resolutions(self):
#         # resolutions (-1) are for methods that do not define resolution
#         resolutions = {}
#
#         ftp = ftplib.FTP(PDBftp['address'])
#         ftp.login()
#         ftp.cwd(PDBftp['derived'])
#         resoluIDX = []
#         ftp.retrlines('RETR ' + PDBftp['resolution'], resoluIDX.append)
#         ftp.quit()
#
#         SBIglobals.alert('debug', self, 'Retrieving resolution data from PDB FTP...')
#
#         active = False
#         for line in resoluIDX:
#             if line.startswith('-'):
#                 active = True
#                 continue
#             if active and len(line.strip()) > 0:
#                 data = [x.strip() for x in line.split(';')]
#                 if len(data[1]) > 0:
#                     SBIglobals.alert('debug', self, '\tResolution for {0[0]} is {0[1]}...'.format(data))
#                     # if resolution_threshold is None:
#                     resolutions[data[0]] = data[1]
#
#         #rsync is accumulative, we might have structures that are not in the residu.idx anymore.. must check
#         for pdb_file in self.localPDBs:
#             newfile = File(file_name = pdb_file, action = 'r')
#             pdbid   = newfile.prefix.lstrip('pdb').upper()
#             if pdbid not in resolutions:
#                 pdbobj = PDB(pdb_file = pdb_file, header = True, onlyheader = True)
#                 SBIglobals.alert('debug', self, '\tGrabbing Resolution for {0} is {1}...'.format(pdbid, pdbobj.header.resolution))
#                 resolutions[pdbid] = pdbobj.header.resolution
#
#         return resolutions
#
#     def get_PDB(self, pdbID):
#         if self.has_local:
#             rootdir = os.path.join(self.local,pdbID.lower()[1:3])
#             for pdb_file in Path.list_files(root = rootdir, pattern = '*.ent.gz'):
#                 newfile = File(file_name = pdb_file, action = 'r')
#                 if newfile.prefix.lstrip('pdb').upper() == pdbID.upper():
#                     return pdb_file
#
#         #If we do not find it in local (or we do not have a local) we search it on the FTP
#         pdb_file = 'pdb' + pdbID.lower() + '.ent.gz'
#         source = 'ftp://' + PDBftp['address'] + os.path.join(PDBftp['structures'], pdbID[1:3].lower(), pdb_file)
#         try:
#             urllib.urlretrieve(source, pdb_file)
#         except:
#             return False
#         return os.path.abspath(pdb_file)
#
#     def get_PDBs(self, pdbIDset):
#         if isintance(pdbIDset, str):
#             warnings.warn('For single PDB search the get_PDB function is recomended.')
#             yield self.get_PDB(pdbIDset)
#         else:
#             pdbIDset = set([x.upper() for x in pdbIDset])
#
#         if self.has_local:
#             for pdb_file in self.localPDBs:
#                 newfile = File(file_name = pdb_file, action = 'r')
#                 if newfile.prefix.lstrip('pdb').upper() in pdbIDset:
#                     yield pdb_file
#         else:
#             for pdbID in pdbIDset:
#                 yield self.get_PDB(pdbID)
#
#     def get_FASTA_IDX_by_names_to_file(self, names, outfile):
#
#
#         fastafile     = Fasta(self.PDBseq)
#         selectedfasta = fastafile.retrieve(copy.deepcopy(names))
#         output_fasta  = File(outfile,'w')
#         for sequence in selectedfasta:
#             output_fasta.write(sequence.format('FASTA') + "\n")
#         output_fasta.close()
#         idxfile       = self.PDBseq + '.idx'
#         output_idx    = File(outfile + '.idx','w')
#         input_idx     = File(idxfile,'r')
#         for line in input_idx.descriptor:
#             info    = line.split()
#             pdbname = info[0][1:]
#             if pdbname in names:
#                 output_idx.write(line)
#         input_idx.close()
#         output_idx.close()




