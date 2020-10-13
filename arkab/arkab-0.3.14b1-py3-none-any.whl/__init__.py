import arkab.nlp as nlp
from arkab.nlp.knowledge import KnowledgeKit

from arkab.trainer import Trainable
from typing import Literal

__all__ = ['nlp', 'Trainable', '__version__', 'version', 'KnowledgeKit', 'MODE']

__version__ = '0.3.14beta1'

MODE = Literal['train', 'valid', 'test']


def version():
    return __version__
