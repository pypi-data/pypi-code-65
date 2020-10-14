# -*- coding: utf-8 -*-
"""
.. codeauthor:: Jaume Bonet <jaume.bonet@gmail.com>

.. affiliation::
    Structural BioInformatics Lab <sbi.upf.edu>
    Baldo Oliva <baldo.oliva@upf.edu>
"""
# Standard Libraries

# External Libraries

# This Library
from SBI.structure import PDBFrame
from SBI.structure.chain import (ChainFrame,
                                 ProteinChainFrame,
                                 NucleotideChainFrame)
import SBI.structure.selectors as selectors
import SBI.core as core
from SBI.tests.helper import str_test_data


class TestChainSelection( object ):
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
        self.dfnmrmc = str_test_data.get_structure('6DSL', 'cif')
        self.dflignt = str_test_data.get_structure('6FYW', 'cif')
        core.set_option('structure', 'source', 'label')

    def test_noNMR_withFabric( self ):
        """Test **Chain Selector** in non-NMR coordinate entities.
        """
        assert self.dftypes.chain_identifiers == ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']

        # Select 1 chain
        sele = selectors.Selector('Chain:A')
        assert isinstance(sele, selectors.Chain)
        dfA = sele.selection(self.dftypes)
        assert isinstance(dfA, ProteinChainFrame)
        assert dfA.chain == 'A'
        # Unselect 1 chain
        sele = selectors.Selector('~Chain:A')
        assert isinstance(sele, selectors.NotSelector)
        dfA = sele.selection(self.dftypes)
        assert isinstance(dfA, PDBFrame)
        assert dfA.chain_identifiers == ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
        assert dfA.chain_count == 8

        # Select 2 chains
        sele = selectors.Selector('Chain:A,C')
        assert isinstance(sele, selectors.Chain)
        dfA = sele.selection(self.dftypes)
        assert isinstance(dfA, PDBFrame)
        assert dfA.chain_identifiers == ['A', 'C']
        assert dfA.chain_count == 2
        # Unselect 2 chains
        sele = selectors.Selector('~Chain:A,C')
        assert isinstance(sele, selectors.NotSelector)
        dfA = sele.selection(self.dftypes)
        assert isinstance(dfA, PDBFrame)
        assert dfA.chain_identifiers == ['B', 'D', 'E', 'F', 'G', 'H', 'I']
        assert dfA.chain_count == 7

        # Select unexisting chain
        sele = selectors.Selector('Chain:N')
        assert isinstance(sele, selectors.Chain)
        dfA = sele.selection(self.dftypes)
        assert isinstance(dfA, ChainFrame)
        assert len(dfA) == 0
        # Unelect unexisting chain
        sele = selectors.Selector('~Chain:N')
        assert isinstance(sele, selectors.NotSelector)
        dfA = sele.selection(self.dftypes)
        assert isinstance(dfA, PDBFrame)
        assert dfA.chain_identifiers == ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
        assert dfA.chain_count == 9

        # Unselect all but one
        sele = selectors.Selector('~Chain:B,C,D,E')
        assert isinstance(sele, selectors.NotSelector)
        dfA = sele.selection(self.dftypes)
        assert isinstance(dfA, PDBFrame)
        assert dfA.chain_identifiers == ['A', 'F', 'G', 'H', 'I']

        sele = selectors.Selector('~Chain:B,C,D,E,F,G,H,I')
        assert isinstance(sele, selectors.NotSelector)
        dfA = sele.selection(self.dftypes)
        assert isinstance(dfA, ProteinChainFrame)
        assert dfA.chain == 'A'
        # Unselect all
        sele = selectors.Selector('~Chain:A,B,C,D,E,F,G,H,I')
        assert isinstance(sele, selectors.NotSelector)
        dfA = sele.selection(self.dftypes)
        assert isinstance(dfA, PDBFrame)
        assert dfA.chain_identifiers == []
        assert dfA.chain_count == 0

        # Select by type: protein
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

        # Select by type: nucleotide
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

        # Get individual ligands (only in label)
        sele = selectors.Selector('ChainType:ligand')
        dfL = sele.selection(self.dftypes)
        assert isinstance(dfL, PDBFrame)
        assert dfL.chain_identifiers == ['F', 'G', 'H', 'I']
        assert dfL.chain_count == 4

        # Negative selections by type
        sele = selectors.Selector('~ChainType:protein')
        assert isinstance(sele, selectors.NotSelector)
        dfnotP = sele.selection(self.dftypes)
        assert isinstance(dfnotP, PDBFrame)
        dfnotP == self.dftypes['Chain:C,D,E,F,G,H,I']
        sele = selectors.Selector('~ChainType:nucleotide')
        assert isinstance(sele, selectors.NotSelector)
        dfnotN = sele.selection(self.dftypes)
        assert isinstance(dfnotN, PDBFrame)
        dfnotN == self.dftypes['Chain:A,B,F,G,H,I']
        sele = selectors.Selector('~ChainType:ligand')
        assert isinstance(sele, selectors.NotSelector)
        dfnotL = sele.selection(self.dftypes)
        assert isinstance(dfnotL, PDBFrame)
        dfnotL == self.dftypes['Chain:A,B,C,D,E']

    def test_noNMR_withObject( self ):
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

    def test_noNMR_withString( self ):
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

    def test_NMR( self ):

        # Alternative select each model.
        for model in self.dfnmrmc.NMR_ids:
            core.set_option('structure', 'model', model)

            dfA = self.dfnmrmc['Chain:A']
            assert isinstance(dfA, ProteinChainFrame)
            assert dfA.chain == 'A'
            assert dfA.NMR_ids == [model]
            assert dfA.NMR_count == 1
            assert dfA.residue_count == 33

        # Pick them all
        core.set_option('structure', 'model', 0)
        dfA = self.dfnmrmc['Chain:A']
        assert isinstance(dfA, ProteinChainFrame)
        assert dfA.chain == 'A'
        assert dfA.NMR_ids == self.dfnmrmc.NMR_ids
        assert dfA.NMR_count == 20
        assert dfA.residue_count == 33

        # Reset default model.
        core.set_option('structure', 'model', 1)
