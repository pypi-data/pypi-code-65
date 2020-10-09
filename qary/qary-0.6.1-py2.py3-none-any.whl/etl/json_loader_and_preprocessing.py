""" process words and add them to a json file  """

import re
import gzip
import json
import pathlib
from tqdm import tqdm
from collections import Counter

from qary import constants
from qary.etl.netutils import download_if_necessary
from qary.spacy_language_model import nlp


def process_words_wiki():
    '''extract words as keys and word count as values

    >>> WORDS_FILEPATH = pathlib.Path(constants.DATA_DIR, 'corpora', 'wiki_titles_words.json')
    >>> vocab = open(WORDS_FILEPATH, 'r')
    >>> words = json.load(vocab)
    >>> words['page']
    2
    >>> vocab.close()
    '''
    filepath = download_if_necessary("wikipedia-titles")
    WORDS_FILEPATH = pathlib.Path(constants.DATA_DIR, 'corpora', 'wiki_titles_words.json')

    with gzip.open(filepath) as fin:
        titles = fin.read()

    titles = titles.decode().split('\n')
    titles = titles[:1000]

    wiki_titles_words = Counter()
    i=0
    while i != len(titles):
        batch = 0
        for title in tqdm(titles[i:i + 100]):
            batch += 1
            title = title.replace('_', ' ')
            title = " ".join(re.findall(r'\w+', title.lower()))
            title_words = [token.text for token in nlp(title) if token.like_num == False
                           and token.is_alpha == True and token.is_ascii == True]
            for word in title_words:
                wiki_titles_words[word] += 1
        i += batch

    with open(WORDS_FILEPATH, 'w') as vocab:
        json.dump(wiki_titles_words, vocab, indent=2)  # optional argument: , sort_keys=True)
        # should this have its own function?


def process_words_big():
    '''extract words as keys and word count as values

    >>> WORDS_FILEPATH = pathlib.Path(constants.DATA_DIR, 'corpora', 'big.json')
    >>> vocab = open(WORDS_FILEPATH, 'r')
    >>> words = json.load(vocab)
    >>> words['the']
    79809
    >>> vocab.close()
    '''
    VOCABULARY_FILEPATH = pathlib.Path(constants.DATA_DIR, 'corpora', 'big.txt')
    WORDS_FILEPATH = pathlib.Path(constants.DATA_DIR, 'corpora', 'big.json')

    with open(VOCABULARY_FILEPATH) as vocabulary:
        words = vocabulary.read()

    words = re.findall(r'\w+', words.lower())
    big_vocab = Counter()
    i=0
    while i != len(words):
        batch = 0
        for word in tqdm(words):
            batch += 1
            big_vocab[word] += 1
        i += batch

    with open(WORDS_FILEPATH, 'w') as vocab:
        json.dump(big_vocab, vocab, indent=2)  # optional argument: , sort_keys=True)


# How to test speed if I have mulitple ways of solving a problem.
# Is speed the most important factor or is memory usage etc.
# will sorting the json file by highest to lowest value(count) make it run faster?
# wiki titles has spanish titles - is there a list of English only titles
