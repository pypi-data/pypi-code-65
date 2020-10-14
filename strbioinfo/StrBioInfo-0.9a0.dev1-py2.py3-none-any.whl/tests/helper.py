# -*- coding: utf-8 -*-
"""
.. codeauthor:: Jaume Bonet <jaume.bonet@gmail.com>

.. affiliation::
    Structural BioInformatics Lab <sbi.upf.edu>
    Baldo Oliva <baldo.oliva@upf.edu>
"""
# Standard Libraries
import os

# External Libraries

# This Library
from SBI.structure import PDB


__all__ = ['str_test_data']


class LoadData( object ):
    """This object takes care that the coordinate entities are only read once.
    """
    __instance = None

    def __new__(cls, val):
        if LoadData.__instance is None:
            LoadData.__instance = object.__new__(cls)
        LoadData.__instance.val = val
        return LoadData.__instance

    def __init__( self, dirpath ):
        self._data = {}
        self._data.setdefault('5WN0', {}).setdefault('cif', PDB(os.path.abspath(os.path.join(dirpath, '5wn0.cif.gz'))))
        self._data.setdefault('5WN0', {}).setdefault('pdb', PDB(os.path.abspath(os.path.join(dirpath, '5wn0.pdb.gz'))))
        self._data.setdefault('5WN0', {}).setdefault('xml', PDB(os.path.abspath(os.path.join(dirpath, '5wn0.xml.gz'))))
        self._data.setdefault('4OO9', {}).setdefault('cif', PDB(os.path.abspath(os.path.join(dirpath, '4OO9.cif.gz'))))
        self._data.setdefault('1IGY', {}).setdefault('cif', PDB(os.path.abspath(os.path.join(dirpath, '1IGY.cif.gz'))))
        self._data.setdefault('3CKR', {}).setdefault('cif', PDB(os.path.abspath(os.path.join(dirpath, '3CKR.cif.gz'))))
        self._data.setdefault('6DSL', {}).setdefault('cif', PDB(os.path.abspath(os.path.join(dirpath, '6DSL.cif.gz'))))
        self._data.setdefault('6FYW', {}).setdefault('cif', PDB(os.path.abspath(os.path.join(dirpath, '6FYW.cif.gz'))))

    def get_structure( self, strID, formatID ):
        return PDB(self._data[strID][formatID])


str_test_data = LoadData(os.path.join(os.path.dirname(__file__), 'data'))
