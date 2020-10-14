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


class TestSelection( object ):
    """Test selection actions over structure.

    Basically assert that:
        1) Selection declarations are OK.
        2) Result from selection is as expected in content and class.
        3) Selection respond to changes in options.structure.source (``auth`` vs ``label``)
        4) Different approaches to the same selection behave the same.
    """
    def setup_method( self, method ):
        # Start by loading the PDBs we are going to use.
        # We load the .CIF version to be able to switch options.structure.source.
        self.dirpath = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.dftypes = PDB(os.path.join(self.dirpath, '5wn0.cif.gz'))
        self.dforder = PDB(os.path.join(self.dirpath, '4OO9.cif.gz'))
        self.dfinser = PDB(os.path.join(self.dirpath, '1IGY.cif.gz'))
        self.dfnegav = PDB(os.path.join(self.dirpath, '3CKR.cif.gz'))
        core.set_option('structure', 'source', 'label')

    def test_chain_selector_construction( self ):
        core.set_option('structure', 'source', 'auth')
        # Chain Selectors are the most global ones.
        sele = selectors.Selector('Chain:A')
        assert sele._selection == ['A']
        sele = selectors.Selector('Chain:A,C')
        assert sele._selection == ['A', 'C']
        with pytest.raises(selectors.SelectionFormatError):
            # This is how the logic is implemented. Multiple chains are separated
            # by ','. This should be very easy to change if there are good reasons
            # for it.
            sele = selectors.Selector('Chain:AC')

    def test_chaintype_selector_construction( self ):
        core.set_option('structure', 'source', 'auth')
        # ChainType
        sele = selectors.Selector('ChainType:protein')
        assert sele._selection == 'protein'
        sele = selectors.Selector('ChainType:nucleotide')
        assert sele._selection == 'nucleotide'
        with pytest.raises(selectors.SelectionFormatError):
            sele = selectors.Selector('ChainType:nucleoprotein')

    def test_residue_selector_construction( self ):
        core.set_option('structure', 'source', 'auth')
        # Residue
        sele = selectors.Selector('Residue:116')
        assert sele._selection == [116]
        sele = selectors.Selector('Residue:116A')
        assert sele._selection == ['116A']
        sele = selectors.Selector('Residue:-6')
        assert sele._selection == [-6]
        sele = selectors.Selector('Residue:116-138')
        assert sele._selection == [[116, 138]]
        sele = selectors.Selector('Residue:116-138A')
        assert sele._selection == [[116, '138A']]
        sele = selectors.Selector('Residue:-6--1')
        assert sele._selection == [[-6, -1]]
        sele = selectors.Selector('Residue:15B--1')
        assert sele._selection == [['15B', -1]]
        sele = selectors.Selector('Residue:116-138,245-372')
        assert sele._selection == [[116, 138], [245, 372]]

    def test_residuetype_selector_construction( self ):
        core.set_option('structure', 'source', 'auth')
        # ResidueType
        sele = selectors.Selector('ResidueType:ARG,TYR,CYS')
        assert sele._selection == ['ARG', 'TYR', 'CYS']

    def test_atom_selector_construction( self ):
        core.set_option('structure', 'source', 'auth')
        # Atom
        sele = selectors.Selector('Atom:12')
        assert sele._selection == [12]
        with pytest.raises(selectors.SelectionFormatError):
            sele = selectors.Selector('Atom:12A')
        with pytest.raises(selectors.SelectionFormatError):
            sele = selectors.Selector('Atom:-12')
        sele = selectors.Selector('Atom:12-35')
        assert sele._selection == [[12, 35]]
        sele = selectors.Selector('Atom:12-35,245-500')
        assert sele._selection == [[12, 35], [245, 500]]

    def test_atomtype_selector_construction( self ):
        core.set_option('structure', 'source', 'auth')
        # AtomType
        sele = selectors.Selector('AtomType:CA,N,O,C')
        assert sele._selection == ['CA', 'N', 'O', 'C']

    def test_target_basic_assessment( self ):
        core.set_option('structure', 'source', 'auth')
        # Default Values
        assert self.dftypes.chain_identifiers == ['A', 'B', 'C', 'D', 'E']
        assert self.dftypes.chain_count == 5
        assert self.dftypes.NMR_ids == [1]
        assert self.dftypes.NMR_count == 1
        assert self.dftypes.is_NMR is False

    def test_chain_selectors( self ):
        core.set_option('structure', 'source', 'auth')
        # Select 1 chain
        sele = selectors.Selector('Chain:A')
        assert isinstance(sele, selectors.Chain)
        dfA = sele.selection(self.dftypes)
        assert isinstance(dfA, ProteinChainFrame)
        assert dfA.chain == 'A'

        # Select 2 chains
        sele = selectors.Selector('Chain:A,C')
        assert isinstance(sele, selectors.Chain)
        dfA = sele.selection(self.dftypes)
        assert isinstance(dfA, PDBFrame)
        assert dfA.chain_identifiers == ['A', 'C']
        assert dfA.chain_count == 2

        # Select unexisting chain
        sele = selectors.Selector('Chain:N')
        assert isinstance(sele, selectors.Chain)
        dfA = sele.selection(self.dftypes)
        assert isinstance(dfA, ChainFrame)
        assert len(dfA) == 0

    def test_chain_selectors_getitem_object( self ):
        core.set_option('structure', 'source', 'auth')
        # Select 1 chain
        sele = selectors.Selector('Chain:A')
        assert isinstance(sele, selectors.Chain)
        dfA = self.dftypes[sele]
        assert isinstance(dfA, ProteinChainFrame)
        assert dfA.chain == 'A'

        # Select 2 chains
        sele = selectors.Selector('Chain:A,C')
        assert isinstance(sele, selectors.Chain)
        dfA = self.dftypes[sele]
        assert isinstance(dfA, PDBFrame)
        assert dfA.chain_identifiers == ['A', 'C']
        assert dfA.chain_count == 2

        # Select unexisting chain
        sele = selectors.Selector('Chain:N')
        assert isinstance(sele, selectors.Chain)
        dfA = self.dftypes[sele]
        assert isinstance(dfA, ChainFrame)
        assert len(dfA) == 0

    def test_chain_selectors_getitem_string( self ):
        core.set_option('structure', 'source', 'auth')
        # Select 1 chain
        dfA = self.dftypes['Chain:A']
        assert isinstance(dfA, ProteinChainFrame)
        assert dfA.chain == 'A'

        # Select 2 chains
        dfA = self.dftypes['Chain:A,C']
        assert isinstance(dfA, PDBFrame)
        assert dfA.chain_identifiers == ['A', 'C']
        assert dfA.chain_count == 2

        # Select unexisting chain
        dfA = self.dftypes['Chain:N']
        assert isinstance(dfA, ChainFrame)
        assert len(dfA) == 0

    def test_chaintype_selectors( self ):
        core.set_option('structure', 'source', 'auth')
        # Select chains by type: protein
        sele = selectors.Selector('ChainType:protein')
        assert isinstance(sele, selectors.ChainType)
        dfP = sele.selection(self.dftypes)
        assert isinstance(dfP, PDBFrame)
        assert dfP.chain_identifiers == ['A', 'B']
        assert dfP.chain_count == 2
        assert len(list(dfP.proteins)) == 2
        assert len(list(dfP.nucleotides)) == 0
        for protein in dfP.proteins:
            assert isinstance(protein, ProteinChainFrame)

        # Select chains by type: nucleotide
        sele = selectors.Selector('ChainType:nucleotide')
        assert isinstance(sele, selectors.ChainType)
        dfN = sele.selection(self.dftypes)
        assert isinstance(dfN, PDBFrame)
        assert dfN.chain_identifiers == ['C', 'D', 'E']
        assert dfN.chain_count == 3
        assert len(list(dfN.proteins)) == 0
        assert len(list(dfN.nucleotides)) == 3
        for nucleotide in dfN.nucleotides:
            assert isinstance(nucleotide, NucleotideChainFrame)

        # Empty selection by type by selecting the contrary chain
        # type over the previous chain type selection.
        sele = selectors.Selector('ChainType:protein')
        dfNP = sele.selection(dfN)
        assert isinstance(dfNP, ProteinChainFrame)
        assert len(dfNP) == 0
        sele = selectors.Selector('ChainType:nucleotide')
        dfPN = sele.selection(dfP)
        assert isinstance(dfPN, NucleotideChainFrame)
        assert len(dfPN) == 0

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
