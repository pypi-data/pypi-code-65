

import six

if six.PY2:
    __all__ = ['Atom', 'AtomSerie', 'AtomOfAminoAcid', 'AtomOfNucleotide']
    from Atom             import Atom
    from AtomOfAminoAcid  import AtomOfAminoAcid
    from AtomOfNucleotide import AtomOfNucleotide
else:
    from .AtomSeries import *
