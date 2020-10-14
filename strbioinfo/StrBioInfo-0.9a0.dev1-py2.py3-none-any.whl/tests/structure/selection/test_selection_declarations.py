# -*- coding: utf-8 -*-
"""
.. codeauthor:: Jaume Bonet <jaume.bonet@gmail.com>

.. affiliation::
    Structural BioInformatics Lab <sbi.upf.edu>
    Baldo Oliva <baldo.oliva@upf.edu>
"""
# Standard Libraries

# External Libraries
import pytest

# This Library
import SBI.structure.selectors as selectors
from SBI.data import alphabet


class TestSelectionDeclaration( object ):
    """Test that selections are created as expected depending on the input.
    """
    def test_chain_selector_construction( self ):
        """Chain selectors are the most global ones.
        """
        # Do 1 chain
        sele = selectors.Selector('Chain:A')
        assert sele._selection == ['A']
        assert isinstance(sele, selectors.Chain)
        # Do +1 chains
        sele = selectors.Selector('Chain:A,C')
        assert sele._selection == ['A', 'C']
        assert isinstance(sele, selectors.Chain)

        # Negative selection
        sele = selectors.Selector('~Chain:A')
        assert isinstance(sele, selectors.NotSelector)
        assert isinstance(sele.selector, selectors.Chain)
        assert sele.selector._selection == ['A']

    def test_chaintype_selector_construction( self ):
        """ChainType basically refers to selecting protein, nucleotide or ligand.
        """
        # Select Protein
        sele = selectors.Selector('ChainType:protein')
        assert sele._selection == 'protein'
        assert isinstance(sele, selectors.ChainType)
        # Negative selection
        sele = selectors.Selector('~ChainType:protein')
        assert isinstance(sele, selectors.NotSelector)
        assert isinstance(sele.selector, selectors.ChainType)
        assert sele.selector._selection == 'protein'
        # Select Nucleotide
        sele = selectors.Selector('ChainType:nucleotide')
        assert sele._selection == 'nucleotide'
        assert isinstance(sele, selectors.ChainType)
        # Negative selection
        sele = selectors.Selector('~ChainType:nucleotide')
        assert isinstance(sele, selectors.NotSelector)
        assert isinstance(sele.selector, selectors.ChainType)
        assert sele.selector._selection == 'nucleotide'
        # Select Ligand. This will only provide something if applied
        # on source==label global option, as in source==auth ligands
        # share chain with the binder protein/nucleotide
        sele = selectors.Selector('ChainType:ligand')
        assert sele._selection == 'ligand'
        assert isinstance(sele, selectors.ChainType)
        # Negative selection
        sele = selectors.Selector('~ChainType:ligand')
        assert isinstance(sele, selectors.NotSelector)
        assert isinstance(sele.selector, selectors.ChainType)
        assert sele.selector._selection == 'ligand'

        with pytest.raises(selectors.SelectionFormatError):
            # Other selections are not available and will rise an error
            sele = selectors.Selector('ChainType:nucleoprotein')

    def test_residue_selector_construction( self ):
        """Residue allows to select by residue ranges/positions.
        """
        # One Residue
        sele = selectors.Selector('Residue:116')
        assert sele._selection == [116]
        assert isinstance(sele, selectors.Residue)
        sele = selectors.Selector('Residue:116A')
        assert sele._selection == ['116A']
        assert isinstance(sele, selectors.Residue)
        sele = selectors.Selector('Residue:-6')  # with negatives
        assert sele._selection == [-6]
        assert isinstance(sele, selectors.Residue)
        # Negative selection
        sele = selectors.Selector('~Residue:116')
        assert isinstance(sele, selectors.NotSelector)
        assert isinstance(sele.selector, selectors.Residue)
        assert sele.selector._selection == [116]

        with pytest.raises(selectors.SelectionFormatError):
            sele = selectors.Selector('Residue:166AB')

        # Range
        sele = selectors.Selector('Residue:116-138')
        assert sele._selection == [[116, 138]]
        assert isinstance(sele, selectors.Residue)
        sele = selectors.Selector('Residue:116-138A')
        assert sele._selection == [[116, '138A']]
        assert isinstance(sele, selectors.Residue)
        sele = selectors.Selector('Residue:-6--1')  # with negatives
        assert sele._selection == [[-6, -1]]
        assert isinstance(sele, selectors.Residue)
        sele = selectors.Selector('Residue:15B--1')  # with negatives
        assert sele._selection == [['15B', -1]]
        assert isinstance(sele, selectors.Residue)
        # Negative selection
        sele = selectors.Selector('~Residue:116-138')
        assert isinstance(sele, selectors.NotSelector)
        assert isinstance(sele.selector, selectors.Residue)
        assert sele.selector._selection == [[116, 138]]

        with pytest.raises(selectors.SelectionFormatError):
            sele = selectors.Selector('Residue:116-138-150')

        # Multiple ranges
        sele = selectors.Selector('Residue:116-138,245')
        assert sele._selection == [[116, 138], 245]
        assert isinstance(sele, selectors.Residue)
        sele = selectors.Selector('Residue:116-138,245-372')
        assert sele._selection == [[116, 138], [245, 372]]
        assert isinstance(sele, selectors.Residue)
        with pytest.raises(selectors.SelectionFormatError):
            sele = selectors.Selector('Residue:116-138-150,245A')

    def test_residuetype_selector_construction( self ):
        """ResidueType aims to pick particular residues.
        Can be used to pick particular HETATM.
        """
        # Protein Residues
        sele = selectors.Selector('ResidueType:ARG,TYR,CYS')
        assert sele._selection == ['ARG', 'TYR', 'CYS']
        assert isinstance(sele, selectors.ResidueType)
        # Negative selection
        sele = selectors.Selector('~ResidueType:ARG,TYR,CYS')
        assert isinstance(sele, selectors.NotSelector)
        assert isinstance(sele.selector, selectors.ResidueType)
        assert sele.selector._selection == ['ARG', 'TYR', 'CYS']
        # Nucleotide Residues
        sele = selectors.Selector('ResidueType:DC,DA,DT')
        assert sele._selection == ['DC', 'DA', 'DT']
        assert isinstance(sele, selectors.ResidueType)
        # Negative selection
        sele = selectors.Selector('~ResidueType:DC,DA,DT')
        assert isinstance(sele, selectors.NotSelector)
        assert isinstance(sele.selector, selectors.ResidueType)
        assert sele.selector._selection == ['DC', 'DA', 'DT']
        # Ligand Residues
        sele = selectors.Selector('ResidueType:CA')
        assert sele._selection == ['CA']
        assert isinstance(sele, selectors.ResidueType)
        # Negative selection
        sele = selectors.Selector('~ResidueType:CA')
        assert isinstance(sele, selectors.NotSelector)
        assert isinstance(sele.selector, selectors.ResidueType)
        assert sele.selector._selection == ['CA']

    def test_atom_selector_construction( self ):
        """Select by atom number or range
        """
        # One atom
        sele = selectors.Selector('Atom:12')
        assert sele._selection == [12]
        assert isinstance(sele, selectors.Atom)
        # Negative selection
        sele = selectors.Selector('~Atom:12')
        assert isinstance(sele, selectors.NotSelector)
        assert isinstance(sele.selector, selectors.Atom)
        assert sele.selector._selection == [12]

        with pytest.raises(selectors.SelectionFormatError):
            # Atoms DO NOT have insertion codes.
            sele = selectors.Selector('Atom:12A')
        with pytest.raises(selectors.SelectionFormatError):
            # Atoms DO NOT have negative values
            sele = selectors.Selector('Atom:-12')
        # Ranges
        sele = selectors.Selector('Atom:12-35')
        assert sele._selection == [[12, 35]]
        assert isinstance(sele, selectors.Atom)
        # Negative selection
        sele = selectors.Selector('~Atom:12-35')
        assert isinstance(sele, selectors.NotSelector)
        assert isinstance(sele.selector, selectors.Atom)
        assert sele.selector._selection == [[12, 35]]

        with pytest.raises(selectors.SelectionFormatError):
            # Atoms DO NOT have negative values
            sele = selectors.Selector('Atom:-12-35')
        with pytest.raises(selectors.SelectionFormatError):
            # Atoms DO NOT have negative values
            sele = selectors.Selector('Atom:12--35')
        sele = selectors.Selector('Atom:12-35,245-500')
        assert sele._selection == [[12, 35], [245, 500]]
        assert isinstance(sele, selectors.Atom)

    def test_atomtype_selector_construction( self ):
        """Select by the type of atoms.
        """
        # one atom
        sele = selectors.Selector('AtomType:CA')
        assert sele._selection == ['CA']
        assert isinstance(sele, selectors.AtomType)
        # +1 atoms
        sele = selectors.Selector('AtomType:CA,N,O,C')
        assert sele._selection == ['CA', 'N', 'O', 'C']
        assert isinstance(sele, selectors.AtomType)
        # Negative selection
        sele = selectors.Selector('~AtomType:CA,N,O,C')
        assert isinstance(sele, selectors.NotSelector)
        assert isinstance(sele.selector, selectors.AtomType)
        assert sele.selector._selection == ['CA', 'N', 'O', 'C']

    def test_atomtask_selector_construction( self ):
        """Select by the task the atom is suposed to have.
        """
        # select protein backbones
        sele = selectors.Selector('AtomTask:PROTEINBACKBONE')
        assert sorted(sele._selection) == sorted(alphabet.protein_backbone)
        assert isinstance(sele, selectors.AtomTask)
        # Negative selection
        sele = selectors.Selector('~AtomTask:PROTEINBACKBONE')
        assert isinstance(sele, selectors.NotSelector)
        assert isinstance(sele.selector, selectors.AtomTask)
        assert sorted(sele.selector._selection) == sorted(alphabet.protein_backbone)
        # select nucleotide backbones
        sele = selectors.Selector('AtomTask:NUCLEOTIDEBACKBONE')
        assert sorted(sele._selection) == sorted(alphabet.nucleotide_backbone)
        assert isinstance(sele, selectors.AtomTask)
        # Negative selection
        sele = selectors.Selector('~AtomTask:NUCLEOTIDEBACKBONE')
        assert isinstance(sele, selectors.NotSelector)
        assert isinstance(sele.selector, selectors.AtomTask)
        assert sorted(sele.selector._selection) == sorted(alphabet.nucleotide_backbone)
        # select all backbones
        sele = selectors.Selector('AtomTask:BACKBONE')
        assert sorted(sele._selection) == sorted(alphabet.nucleotide_backbone + alphabet.protein_backbone)
        assert isinstance(sele, selectors.AtomTask)
        # Negative selection
        sele = selectors.Selector('~AtomTask:BACKBONE')
        assert isinstance(sele, selectors.NotSelector)
        assert isinstance(sele.selector, selectors.AtomTask)
        assert sorted(sele.selector._selection) == sorted(alphabet.nucleotide_backbone + alphabet.protein_backbone)

        with pytest.raises(selectors.SelectionFormatError):
            # Non-defined tasks will rise an error.
            sele = selectors.Selector('AtomTask:BINDERS')

    def test_unknown_selectors( self ):
        """Calling random selector identifiers will rise errors.
        This also applies to not keeping a CamelCase naming.
        """
        sele = None
        with pytest.raises(selectors.SelectionTypeError):
            sele = selectors.Selector('chain:A')
        with pytest.raises(selectors.SelectionTypeError):
            sele = selectors.Selector('chaintype:A')
        with pytest.raises(selectors.SelectionTypeError):
            sele = selectors.Selector('residue:A')
        with pytest.raises(selectors.SelectionTypeError):
            sele = selectors.Selector('residuetype:A')
        with pytest.raises(selectors.SelectionTypeError):
            sele = selectors.Selector('atom:A')
        with pytest.raises(selectors.SelectionTypeError):
            sele = selectors.Selector('atomtype:A')
        with pytest.raises(selectors.SelectionTypeError):
            sele = selectors.Selector('atomtask:A')
        with pytest.raises(selectors.SelectionFormatError):
            sele = selectors.Selector('all')
        with pytest.raises(selectors.SelectionTypeError):
            sele = selectors.Selector('all:buried')
        with pytest.raises(selectors.SelectionTypeError):
            sele = selectors.Selector('~all:buried')
        assert sele is None
