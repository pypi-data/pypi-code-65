"""Spelling Corrector based on Peter Norvig's Spelling Corrector"""

import re
import json
from collections import Counter
import pathlib
from qary import constants
from qary.spacy_language_model import nlp

WORDS_FILEPATH = pathlib.Path(constants.DATA_DIR, 'corpora', 'big.json')

with open(WORDS_FILEPATH, 'r') as vocab:
    WORDS = json.load(vocab)

def P(word, N=sum(WORDS.values())):
    "Probability of `word`."
    return WORDS[word] / N

def correction(word):
    "Most probable spelling correction for word."
    return max(candidates(word), key=P)

def candidates(word):
    "Generate possible spelling corrections for word."
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

def known(words):
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word):
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))


def make_spelling_corrections(text):
    """takes a sentence and replaces mispelled words with most probable spelling corrections

    >>> make_spelling_corrections("Corect this speling pleese.")
    'Correct this spelling please.'
    >>> make_spelling_corrections("Sentance korrectud!")
    'Sentence corrected!'
    >>> make_spelling_corrections("Who is Barack Obama?")
    'Who is Barack Obama?'
    """
    nlp_text = [token for token in nlp(text)]
    new_text = text
    for token in nlp_text:
        if not token.is_punct: #and token.pos_ != "PROPN": <-doesn't work if fist word in sentense is caps
            if token.is_title and token.text.lower() != correction(token.text.lower()):
                new_text = new_text.replace(token.text, correction(token.text.lower()).title())
            elif token.text.lower() != correction(token.text.lower()):
                new_text = new_text.replace(token.text, correction(token.text.lower()))
        else:
            pass
    return new_text


def make_corrections_clean(text):
    """takes a sentence removes punctuation lowers,and replaces mispelled words with most probable spelling corrections

    >>> make_corrections_clean("Corect this speling pleese.")
    'correct this spelling please'
    >>> make_corrections_clean("sentance korrectud!")
    'sentence corrected'
    >>> make_corrections_clean("make spellin corectins.")
    'make spelling corrections'
    """
    text = [token.text for token in nlp(text.lower()) if not token.is_punct]
    new_text = []
    for word in text:
        new_text.append(correction(word))
    return " ".join(new_text)
