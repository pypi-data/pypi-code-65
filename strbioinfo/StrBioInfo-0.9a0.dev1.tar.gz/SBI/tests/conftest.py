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
import pytest

# This Library


class SharedData( object ):
    def __init__( self ):
        dpath = os.path.join(os.path.dirname(__file__), 'data')
        self.data = {
            ('pdbsample', 'cif'): os.path.join(dpath, 'sample_cif.txt'),
            ('pdbsample', 'pdb'): os.path.join(dpath, 'sample_pdb.txt'),
            ('pdbsample', 'xml'): os.path.join(dpath, 'sample_xml.txt'),
        }


@pytest.fixture(scope="session")
def shared():
    return SharedData()
