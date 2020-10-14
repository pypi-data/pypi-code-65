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
from SBI.structure import PDB, PDBFrame
from SBI.structure.chain import (ChainFrame,
                                 ProteinChainFrame,
                                 NucleotideChainFrame)
from SBI.structure.residue import (ResidueFrame,
                                   ProteinResidueFrame,
                                   NucleotideResidueFrame)
import SBI.structure.selectors as selectors
import SBI.core as core
from SBI.tests.helper import str_test_data


class TestSelection( object ):
    """Test selection actions over structure.

    Basically assert that:
        1) Result from selection is as expected in content and class.
        2) Selection respond to changes in options.structure.source (``auth`` vs ``label``)
        3) Different approaches to the same selection behave the same.
    """
    def setup_method( self, method ):
        # Start by loading the PDBs we are going to use.
        # We load the .CIF version to be able to switch options.structure.source.
        self.dftypes = str_test_data.get_structure('5WN0', 'cif')
        self.dforder = str_test_data.get_structure('4OO9', 'cif')
        self.dfinser = str_test_data.get_structure('1IGY', 'cif')
        self.dfnegav = str_test_data.get_structure('3CKR', 'cif')
        self.dfnmrmc = str_test_data.get_structure('6DSL', 'cif')
        core.set_option('structure', 'source', 'auth')

    def test_residue_selectors( self ):
        # Easy Selection: over mmcif 'label'
        core.set_option('structure', 'source', 'label')

        # Select one residue; one chain
        sele = selectors.Selector('Residue:116')
        one_res_label = sele.selection(self.dforder)
        assert isinstance(one_res_label, ProteinResidueFrame)
        assert one_res_label.type == 'PHE'
        # Select one residue; two chains
        sele = selectors.Selector('Residue:4')
        two_res_label = sele.selection(self.dfinser)
        assert isinstance(two_res_label, PDBFrame)
        assert sorted(list(two_res_label[two_res_label._current_comp].unique())) == sorted(['HIS', 'GLN'])
        assert len(two_res_label) == 4
        assert two_res_label.chain_identifiers == ['A', 'B', 'C', 'D']
        # Select residues with insertion
        sele = selectors.Selector('Chain:B')
        dfB = sele.selection(self.dfinser)
        ins_seles = []
        ins_types = ['LEU', 'SER', 'SER', 'LEU']
        for i, _ in enumerate(range(82, 86)):
            sele = selectors.Selector('Residue:{}'.format(_))
            ins_seles.append(sele.selection(dfB))
            assert isinstance(ins_seles[-1], ProteinResidueFrame)
            assert ins_seles[-1].type == ins_types[i]
        # Select range of unordered
        sele = selectors.Selector('Residue:113-284')
        range_label = sele.selection(self.dforder)
        assert isinstance(range_label, ProteinChainFrame)
        assert len(range_label) == 164
        assert range_label.iloc[0][range_label._current_atom] == 'N'
        assert range_label.iloc[-1][range_label._current_atom] == 'OG'
        # Select ResidueType
        sele = selectors.Selector('ResidueType:HIS,TYR,ALA,HOH')
        HYA1 = sele.selection(self.dfnegav)
        assert isinstance(HYA1, PDBFrame)
        assert len(HYA1) == 6

        # Tricky Selection: over mmcif 'auth' (default: same as PDB format)
        core.set_option('structure', 'source', 'auth')

        # Select one residue; one chain
        sele = selectors.Selector('Residue:1004')
        one_res_auth = sele.selection(self.dforder)
        assert one_res_label.equals(one_res_auth)
        # Select one residue; two chains
        sele = selectors.Selector('Residue:5')
        two_res_auth = sele.selection(self.dfinser)
        assert isinstance(two_res_auth, PDBFrame)
        assert two_res_label.equals(two_res_auth)
        ins_ids = ['', 'A', 'B', 'C']
        for i, _ in enumerate(ins_ids):
            sele = selectors.Selector('Residue:82{}'.format(_))
            _ = sele.selection(dfB)
            assert ins_seles[i].equals(_)
        # Select range of unordered
        sele = selectors.Selector('Residue:678-689')
        range_auth = sele.selection(self.dforder)
        assert range_label.equals(range_auth)

        # Select ResidueType
        sele = selectors.Selector('ResidueType:HIS,TYR,ALA,HOH')
        HYA2 = sele.selection(self.dfnegav)
        assert isinstance(HYA2, PDBFrame)
        assert len(HYA2) == 3  # Chain discrepance due to structure.source
        assert HYA1.equals(HYA2)

        # Select empty ResidueType
        sele = selectors.Selector('ResidueType:DT')
        DTno = sele.selection(self.dfnegav)
        assert isinstance(DTno, NucleotideResidueFrame)
        assert DTno.shape[0] == 0

    def test_atom_selectors( self ):
        pass

    def test_combined_selectors( self ):
        pass
