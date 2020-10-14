# -*- coding: utf-8 -*-
"""
.. codeauthor:: Jaume Bonet <jaume.bonet@gmail.com>

.. affiliation::
    Structural BioInformatics Lab <sbi.upf.edu>
    Baldo Oliva <baldo.oliva@upf.edu>

.. class:: DSSPExe
"""
# Standard Libraries
import os

# External Libraries

# This Library
from ..ExeBase import ExeBase
from .DSSP import read_dssp

__all__ = ['DSSPExe']


class DSSPExe( ExeBase ):
    """Manage [DSSP](https://github.com/cmbi/xssp) execution and processing.

    .. note::
        Depends on global configuration option ``bin.dssp`` to locate the DSSP executable.

    Generates a :class:`.DSSPFrame` containing the data of the provided protein structure.

    :param str pdb: PDB input file name.
    :param str dssp: DSSP output file name.
    :param bool cleanpdb: Remove PDB file after execution.
    :param bool cleandssp: Remove DSSP file after execution.
    :param bool minimize: If :data:`True`, ignore data from DSSP output that is not
        secondary structure assignation or accessibility.

    :raises:
        :SystemError: If an error occurs during DSSP execution.
    """
    def __init__( self, pdb, dssp, cleanpdb=False, cleandssp=False, minimize=False ):
        super(DSSPExe, self).__init__()
        self._pdbfile  = pdb
        self._dsspfile = dssp
        self._dsspdata = []
        self._gapped   = False

        self._set_default_executable('dssp')

        self._execute()
        self._dsspdata = read_dssp(self._dsspfile, minimize)
        self._clean(cleanpdb, cleandssp)

    # ATTRIBUTES
    @property
    def dsspdata(self):
        """Obtain the parsed DSSP data.

        :returns: :class:`.DSSPFrame`
        """
        return self._dsspdata

    # PRIVATE METHODS
    def _execute(self):
        """Execute the DSSP call.
        """
        self._EXE.add_parameter(self._pdbfile)
        self._EXE.add_parameter(self._dsspfile)
        try:
            self._EXE.execute()
        except SystemError as e:
            raise SystemError('Some error occurred while executing DSSP\n{0}\n'.format(e))
        self._EXE.clean_command()

    def _clean( self, cleanpdb, cleandssp ):
        """Clean files after execution.

        :param bool cleanpdb: Remove PDB input file.
        :param bool cleandssp: Remove output DSSP file.
        """
        if cleanpdb:
            os.unlink(self._pdbfile)
        if cleandssp:
            os.unlink(self._dsspfile)
