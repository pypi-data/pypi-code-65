import spglib as spg
import numpy as np
import brille as br

from readers.castep import _read_cell_symmetry

class BrilleInterpolator(object):
    """
    Brillebrillebrille
    """
    def __init__(self, force_constants, castep_file=None, grid_type='mesh', **brille_kwargs):

        if castep_file is None:
            dataset = spg.get_symmetry_dataset(fc.crystal.to_spglib_cell())
            rotations = dataset['rotations'] # in fractional
            translations = dataset['translations'] # in fractional
        else:
            data = _read_cell_symmetry(castep_file)
            translations = data['symmetry_disps'] # in fractional
            rots_cart = data['symmetry_operations'] # in cartesian
            cv_t = np.transpose(force_constants.crystal.cell_vectors.magnitude) # Units don't matter
            rotations = np.einsum('ij,xjk,kl->xil',
                                  np.linalg.inv(cv_t), rots_cart, cv_t)


        symmetry = br.Symmetry(ops, disps)
        direct = br.Direct(*cell)
        direct.spacegroup = symmetry
        bz = br.BrillouinZone(direct.star)
        #recip = br.Reciprocal(fc.crystal.cell_vectors.to('angstrom').magnitude)
        #bz = br.BrillouinZone(recip)
