"""ngsl

  * New Service General List(NGSL)
  * Using this module, you can check if the word is NGSL or not, etc.
"""
from typing import Optional, List
from ngsl.rank import RANK_DICT
from ngsl.inverted_supplemental import INVERTED_SUPPLEMENTAL
from ngsl.inverted_dictionary import INVERTED_DICTIONARY
from ngsl.dictionary import DICTIONARY
from ngsl.result import Result


def include(word: str, include_supplemental: bool = False) -> bool:
    """
    Return if word is in NGSL

    Args:
        word (str) : word
    Returns:
        bool: return True if word in NGSL
    Example:
        >>> ngsl.include("smiles")
            True
    """
    if include_supplemental and word in INVERTED_SUPPLEMENTAL:
        return True
    return word in INVERTED_DICTIONARY


def get_infinitiv(
        word: str,
        include_supplemental: bool = False) -> Optional[str]:
    """
    Return the infinitiv of the word

    Args:
        word (str) : word
    Returns:
        Optional[str]: infinitiv
    Example:
        >>> ngsl.infinitiv("smiles")
            smile
    """
    if not include(word=word, include_supplemental=include_supplemental):
        return None
    if word in INVERTED_SUPPLEMENTAL:
        return INVERTED_SUPPLEMENTAL[word]
    return INVERTED_DICTIONARY[word]


def classify(words: List[str], include_supplemental: bool = False) -> Result:
    """
    Classify args to the word list of NGSL, the one of NOT NGSL

    Args:
        words (List[str]) : Word list
    Returns:
        Result: Result has fields, ngsl_words, not_ngsl_words
    Example:
        >>> ngsl.classify(["smile", "snapback"])
            Result(ngsl_words=["smile"], not_ngsl_words=["snapback"])
    """
    ngsl_words, not_ngsl_words = [], []
    for word in words:
        if include(word=word, include_supplemental=include_supplemental):
            ngsl_words.append([word, get_rank(word=word)])
        else:
            not_ngsl_words.append(word)
    return Result(
        ngsl_words=ngsl_words,
        not_ngsl_words=not_ngsl_words)


def get_infinitiv_list(
        words: List[str],
        include_supplemental: bool = False) -> List[str]:
    """
    Return the infinitiv of the word

    Args:
        words (List[str]) : Word list
    Returns:
        List[str] : infinitiv words
    Example:
        >>> ngsl.get_infinitiv_list(["smiles", "am", "snapback"])
            ["smile", "be"]
    """
    result = list(set(_sub_get_infinitiv_list(words, include_supplemental)))
    return list(filter(lambda r: r is not None, result))


def _sub_get_infinitiv_list(words, include_supplemental):
    for word in words:
        yield get_infinitiv(word=word, include_supplemental=include_supplemental)


def all_infinitiv() -> List[str]:
    """
    Return all word that belongs to NGSL.

    Returns:
        List[str] : NGSL words
    Example:
        >>> ngsl.all_infinitiv()
            ["the", "be", "and", ...]
    """
    return DICTIONARY.keys()


def get_rank(word: str) -> int:
    """
    Return the NGSL rank

    Returns:
        int : return -1 if the word is not in NGSL
    Example:
        >>> ngsl.get_rank("and")
            3
    """
    return RANK_DICT[word] if word in RANK_DICT else -1
