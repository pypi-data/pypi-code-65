import six

if six.PY2:
    from Chain             import Chain
    from ChainOfProtein    import ChainOfProtein
    from ChainOfNucleotide import ChainOfNucleotide

from .ChainFrame import *
