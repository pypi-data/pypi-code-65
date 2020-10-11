import numpy as np


def check_orthonormality(C,S,Tol=10**-6):
    """
    Revisa la ortonormalidad de los orbitales moleculares mediante CTSC = I.
    C: Matriz de Coeficientes de los Orbitales Moleculares
    S: Matriz de Traslape
    Tol: Tolerancia numérica para asumir que la integral del prododucto de orbitales es cero
    Devuelve
    orthonormality: (True/False) Si los MO son ortonormales
    num_deviations: Cuantos elementos de CTSC son distintos de la matriz identidad.
    max_deviation: La máxima diferencia de CTSC respecto a la matriz identidad.
    """

    nmo = len(C)

    CTSC = np.matmul(np.matmul(np.transpose(C),S),C)
    ortho_deviation = np.abs(CTSC - np.identity(nmo))

    orthonormality = True
    if (np.any(ortho_deviation > Tol)):
        orthonormality = False

    num_deviations = (ortho_deviation > 10**-6).sum()
    max_deviation = ortho_deviation.max()

    return orthonormality, num_deviations, max_deviation
