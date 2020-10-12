import ngsl
from ngsl.dictionary import DICTIONARY


def test_include():
    assert ngsl.include('smile')
    assert ngsl.include('smiles')


def test_get_infinitiv():
    assert ngsl.get_infinitiv('smiles') == 'smile'


def test_get_infinitiv_list():
    assert ngsl.get_infinitiv_list(['smiles', 'quarterback']) == ['smile']


def test_all_infinitiv():
    assert ngsl.all_infinitiv() == DICTIONARY.keys()


def test_get_rank():
    assert ngsl.get_rank("and") == 3


def test_classify():
    words = ["and", "the", "snapback"]
    result = ngsl.classify(words=words)
    assert result.ngsl_words == ["the", "and"]
    assert result.not_ngsl_words == ["snapback"]
