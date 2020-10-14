'''
Printing number of atoms in molecule / but not now
'''
import numpy as np
from rdkit import Chem

def PrintNumAtoms(smiles):
    a = np.array([1, 2, 3])
    mol = Chem.MolFromSmiles(smiles)
    return a, mol
    