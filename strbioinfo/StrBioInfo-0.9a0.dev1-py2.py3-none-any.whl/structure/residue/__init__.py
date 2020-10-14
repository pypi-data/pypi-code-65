import six

if six.PY2:
    from Residue             import Residue
    from ResidueOfNucleotide import ResidueOfNucleotide
    from ResidueOfAminoAcid  import ResidueOfAminoAcid

from .ResidueFrame import *
