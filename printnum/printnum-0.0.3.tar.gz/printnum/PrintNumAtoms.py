'''
Printing number of atoms in molecule
'''
from rdkit import Chem

def PrintNumAtoms(smiles):
    try:
#        mol = Chem.AddHs(Chem.MolFromSmiles(smiles))
        mol = Chem.MolFromSmiles(smiles)
        NumberAtoms = mol.GetNumAtoms()
        
        return print(NumberAtoms)
    except:
        return None
