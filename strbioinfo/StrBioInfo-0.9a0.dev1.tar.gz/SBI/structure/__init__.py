import six

if six.PY2:
    from .atom     import Atom,           AtomOfAminoAcid,    AtomOfNucleotide

    from .residue  import Residue,        ResidueOfAminoAcid, ResidueOfNucleotide

    from .chain    import Chain,          ChainOfProtein,     ChainOfNucleotide

    from .contacts import PPInterface,    PNInterface,        PHInterface
    from .contacts import PPInnerContact, PHInnerContact
    from .contacts import Complex,        InnerContacts

    from .protein  import Arch

    from ._PDB      import _PDB

else:
    from .selectors import *
    from .header import *
    from .Frame3D import *
    from .PDBContainer import *
    from .chain import *
    from .residue import *
    from .atom import *
