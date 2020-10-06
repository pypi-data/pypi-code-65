from copy import deepcopy
from typing import List, Tuple, Set

from rdkit.Chem.rdchem import Mol

from reinvent_chemistry import TransformationTokens, Conversions
from reinvent_chemistry.library_design import FragmentFilter
from reinvent_chemistry.library_design.dtos import FilteringConditionDTO, ReactionDTO
from reinvent_chemistry.library_design.fragment_reactions import FragmentReactions
from reinvent_chemistry.library_design.sliced_molecule import SlicedMol


class FragmentReactionSliceEnumerator:

    def __init__(self, chemical_reactions: List[ReactionDTO],
                 scaffold_conditions: List[FilteringConditionDTO],
                 decoration_conditions: List[FilteringConditionDTO]):
        """
        Class to enumerate slicings given certain conditions.
        :param chemical_reactions: A list of ChemicalReaction objects.
        :param scaffold_conditions: Conditions to use when filtering scaffolds obtained from slicing molecules (see FragmentFilter).
        :param decoration_conditions: Conditions to use when filtering decorations obtained from slicing molecules.
        """
        self._tockens = TransformationTokens()
        self._chemical_reactions = chemical_reactions
        self._scaffold_filter = FragmentFilter(scaffold_conditions)
        self._decoration_filter = FragmentFilter(decoration_conditions)
        self._reactions = FragmentReactions()
        self._conversions = Conversions()

    def enumerate(self, molecule: Mol, cuts: int) -> List[SlicedMol]:
        """
        Enumerates all possible combination of slicings of a molecule given a number of cuts.
        :param molecule: A mol object with the molecule to slice.
        :param cuts: The number of cuts to perform.
        :return : A list with all the possible (scaffold, decorations) pairs as SlicedMol objects.
        """
        sliced_mols = set()
        for cut in range(1, cuts + 1):
            if cut == 1:
                fragment_pairs = self._reactions.slice_molecule_to_fragments(molecule, self._chemical_reactions)
                for pair in fragment_pairs:
                    for indx, _ in enumerate(pair):
                        decorations = self._select_all_except(pair, indx)
                        labeled_decorations = [self._label_scaffold(decoration) for decoration in decorations]

                        labeled_scaffold = self._label_scaffold(pair[indx])
                        # ########
                        #
                        # print(f"preparing scaffold with decorations: {self._conversions.mols_to_smiles(labeled_decorations)}")
                        # print(f"preparing scaffold : {self._conversions.mol_to_smiles(labeled_scaffold)}")
                        # ##############
                        sliced_mols.add(SlicedMol(labeled_scaffold, labeled_decorations))
            else:
                for slice in sliced_mols:
                    to_add = self._scaffold_slicing(slice, cut)
                    sliced_mols = sliced_mols.union(to_add)

        return list(filter(self._filter, sliced_mols))

    def _scaffold_slicing(self, slice: SlicedMol, cut: int) -> Set[SlicedMol]:
        to_add = set()
        if slice.decorations_count() == cut - 1:
            fragment_pairs = self._reactions.slice_molecule_to_fragments(slice.scaffold, self._chemical_reactions)

            for pair in fragment_pairs:
                # sliced_mol = self._identify_scaffold(pair, cut, slice)
                scaffold, decorations = self._split_scaffold_from_decorations(pair, cut)
                if scaffold:
                    labeled_scaffold = self._label_scaffold(scaffold)
                    sliced_mol = self._create_sliced_molecule(slice, labeled_scaffold, decorations)
                    to_add.add(sliced_mol)
        return to_add

    def _select_all_except(self, fragments: Tuple[Mol], to_exclude: int) -> List:
        return [fragment for indx, fragment in enumerate(fragments) if indx != to_exclude]

    def _filter(self, sliced_mol: SlicedMol) -> bool:
        return self._scaffold_filter.filter(sliced_mol.scaffold) \
               and all(self._decoration_filter.filter(dec) for dec in sliced_mol.decorations.values())

    def _split_scaffold_from_decorations(self, pair: Tuple[Mol], cuts: int) -> Tuple[Mol, List[Mol]]:
        decorations = []
        scaffold = None
        for frag in pair:
            num_att = len(
                [atom for atom in frag.GetAtoms() if atom.GetSymbol() == self._tockens.ATTACHMENT_POINT_TOKEN])
            # detect whether there is one fragment with as many attachment points as cuts (scaffold)
            # the rest are decorations
            if num_att == cuts and not scaffold:
                scaffold = frag
            else:
                decorations.append(frag)
        return scaffold, decorations

    def _label_scaffold(self, scaffold: Mol) -> Mol:
        highest_number = self._find_highest_number(scaffold)

        for atom in scaffold.GetAtoms():
            if atom.GetSymbol() == self._tockens.ATTACHMENT_POINT_TOKEN:
                try:
                    atom_number = int(atom.GetProp("molAtomMapNumber"))
                except:
                    highest_number += 1
                    num = atom.GetIsotope()
                    atom.SetIsotope(0)
                    atom.SetProp("molAtomMapNumber", str(highest_number))
        scaffold.UpdatePropertyCache()

        return scaffold

    def _find_highest_number(self, cut_mol: Mol) -> int:
        highest_number = -1

        for atom in cut_mol.GetAtoms():
            if atom.GetSymbol() == self._tockens.ATTACHMENT_POINT_TOKEN:
                try:
                    atom_number = int(atom.GetProp("molAtomMapNumber"))
                    if highest_number < atom_number:
                        highest_number = atom_number
                except:
                    pass
        return highest_number

    def _create_sliced_molecule(self, original_sliced_mol: SlicedMol, scaffold: Mol,
                                decorations: List[Mol]) -> SlicedMol:
        # sliced_mol = SlicedMol(original_sliced_mol.scaffold,original_sliced_mol.decorations)
        sliced_mol = deepcopy(original_sliced_mol)
        sliced_mol.scaffold = scaffold
        for d in decorations:
            sliced_mol.add_decorations({sliced_mol.decorations_count(): d})
        return sliced_mol
