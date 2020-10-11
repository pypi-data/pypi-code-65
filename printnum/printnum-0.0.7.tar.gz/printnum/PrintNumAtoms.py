'''
Printing number of atoms in molecule
'''
import numpy as np

def __init__(smiles):
    
    a = np.array([1, 2, 3])
    print("inisial step", a)

#    from rdkit import Chem
#    try:
#        mol = Chem.AddHs(Chem.MolFromSmiles(smiles))
#        mol = Chem.MolFromSmiles(smiles)
#        NumberAtoms = mol.GetNumAtoms()
#        
#        return print(NumberAtoms)
#    except:
#        return None
