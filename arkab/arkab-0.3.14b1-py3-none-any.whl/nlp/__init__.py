from arkab.nlp.knowledge import PATTERNS, KnowledgeKit
from arkab.nlp.sequence import Corpus

CHAR_ALPHABET = 'abcdefghijklmnopqrstuvwxyz0123456789-,;.!?:\'"/\\|_@#$%^&*~`+-=<>()[]{} '
char2id = {c: i for i, c in enumerate(CHAR_ALPHABET)}

__all__ = ['Corpus', 'PATTERNS', 'KnowledgeKit', 'CHAR_ALPHABET']
