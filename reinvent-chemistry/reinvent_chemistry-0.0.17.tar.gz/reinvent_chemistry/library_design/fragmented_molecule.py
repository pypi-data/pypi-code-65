from collections import OrderedDict
from typing import Dict

from rdkit.Chem.rdchem import Mol

from reinvent_chemistry import Conversions, TransformationTokens, MolecularTransformations


class FragmentedMolecule:

    def __init__(self, scaffold: Mol, decorations, original_smiles: str):
        """
        Represents a molecule as a scaffold and the decorations associated with each attachment point.
        :param scaffold: A Mol object with the scaffold.
        :param decorations: Either a list or a dict with the decorations as Mol objects.
        """
        self._tockens = TransformationTokens()
        self._transformations = MolecularTransformations()
        self._conversions = Conversions()
        self.scaffold = scaffold
        self.decorations = decorations
        self.original_smiles = original_smiles
        self.scaffold_smiles = self._conversions.mol_to_smiles(self.scaffold)
        self.re_label()
        self.decorations_smiles = self._create_decorations_string()
        # if isinstance(decorations, list):
        #     decorations = [self._conversions.copy_mol(dec) for dec in decorations]
        #     nums = [self._transformations.get_first_attachment_point(dec) for dec in decorations]
        #     self.decorations = {num: self._transformations.remove_attachment_point_numbers_from_mol(dec)
        #                         for num, dec in zip(nums, decorations)}
        # else:
        #     self.decorations = {num: self._transformations.remove_attachment_point_numbers_from_mol(self._conversions.copy_mol(dec))
        #                         for num, dec in decorations.items()}

        # self._normalize()

    def __eq__(self, other):
        return self.original_smiles == other.original_smiles and self.scaffold_smiles == other.scaffold_smiles
        # return self.to_smiles() == other_sliced_mol.to_smiles()

    def __hash__(self):
        smi = self.to_smiles()
        return tuple([smi[0], *(smi[1].items())]).__hash__()

    def add_decorations(self, decorations: Dict):
        # purged = {num: self._transformations.remove_attachment_point_numbers_from_mol(self._conversions.copy_mol(dec))
        #            for num, dec in decorations.items()}
        self.decorations.update(decorations)
        # self._normalize()

    def decorations_count(self) -> int:
        return len(self.decorations)

    def re_label(self):
        labels = self._transformations.get_attachment_points(self.scaffold_smiles)
        decorations = OrderedDict()
        for i, v in enumerate(labels):
            decorations[i] = self.decorations[v]
        self.decorations = decorations

    def _create_decorations_string(self):
        values = [self._conversions.mol_to_smiles(smi) for num, smi in self.decorations.items()]
        decorations = '|'.join(values)
        return decorations

    def _normalize(self):
        """
        Normalizes the scaffold, given that the canonicalization algorithm uses the atom map number to canonicalize.
        """
        #TODO: Try renumbering the scaffold. Consider using self._transformations.get_attachment_points()

        for atom in self.scaffold.GetAtoms():
            if atom.HasProp("molAtomMapNumber") and atom.GetSymbol() == self._tockens.ATTACHMENT_POINT_TOKEN:
                num = atom.GetProp("molAtomMapNumber")
                atom.ClearProp("molAtomMapNumber")
                atom.SetProp("_idx", num)

        _ = self._conversions.mol_to_smiles(self.scaffold)
        atom_ordering = eval(self.scaffold.GetProp("_smilesAtomOutputOrder"))  # pylint: disable= eval-used

        curr2can = {}
        curr_idx = 0
        for atom_idx in atom_ordering:
            atom = self.scaffold.GetAtomWithIdx(atom_idx)
            if atom.HasProp("_idx") and atom.GetSymbol() == self._tockens.ATTACHMENT_POINT_TOKEN:
                num = int(atom.GetProp("_idx"))
                atom.ClearProp("_idx")
                atom.SetProp("molAtomMapNumber", str(curr_idx))
                curr2can[num] = curr_idx
                curr_idx += 1

        self.decorations = {curr2can[num]: dec for num, dec in self.decorations.items()}

    def to_smiles(self):
        """
        Calculates the SMILES representation of the given variant of the scaffold and decorations.
        :param variant: SMILES variant to use (see to_smiles)
        :return: A tuple with the SMILES of the scaffold and a dict with the SMILES of the decorations.
        """
        return (self._conversions.mol_to_smiles(self.scaffold),
                {num: self._conversions.mol_to_smiles(dec) for num, dec in self.decorations.items()})

    def to_random_smiles(self):
        """
        Calculates the SMILES representation of the given variant of the scaffold and decorations.
        :param variant: SMILES variant to use (see to_smiles)
        :return: A tuple with the SMILES of the scaffold and a dict with the SMILES of the decorations.
        """
        return (self._conversions.mol_to_random_smiles(self.scaffold),
                {num: self._conversions.mol_to_random_smiles(dec) for num, dec in self.decorations.items()})