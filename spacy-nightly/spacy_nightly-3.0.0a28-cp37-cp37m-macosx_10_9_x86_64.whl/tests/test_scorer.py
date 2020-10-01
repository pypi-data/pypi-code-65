from numpy.testing import assert_almost_equal, assert_array_almost_equal
import pytest
from pytest import approx
from spacy.training import Example
from spacy.training.iob_utils import offsets_to_biluo_tags
from spacy.scorer import Scorer, ROCAUCScore
from spacy.scorer import _roc_auc_score, _roc_curve
from spacy.lang.en import English
from spacy.tokens import Doc


test_las_apple = [
    [
        "Apple is looking at buying U.K. startup for $ 1 billion",
        {
            "heads": [2, 2, 2, 2, 3, 6, 4, 4, 10, 10, 7],
            "deps": [
                "nsubj",
                "aux",
                "ROOT",
                "prep",
                "pcomp",
                "compound",
                "dobj",
                "prep",
                "quantmod",
                "compound",
                "pobj",
            ],
        },
    ]
]

test_ner_cardinal = [
    ["100 - 200", {"entities": [[0, 3, "CARDINAL"], [6, 9, "CARDINAL"]]}]
]

test_ner_apple = [
    [
        "Apple is looking at buying U.K. startup for $1 billion",
        {"entities": [(0, 5, "ORG"), (27, 31, "GPE"), (44, 54, "MONEY")]},
    ]
]


@pytest.fixture
def tagged_doc():
    text = "Sarah's sister flew to Silicon Valley via London."
    tags = ["NNP", "POS", "NN", "VBD", "IN", "NNP", "NNP", "IN", "NNP", "."]
    pos = [
        "PROPN",
        "PART",
        "NOUN",
        "VERB",
        "ADP",
        "PROPN",
        "PROPN",
        "ADP",
        "PROPN",
        "PUNCT",
    ]
    morphs = [
        "NounType=prop|Number=sing",
        "Poss=yes",
        "Number=sing",
        "Tense=past|VerbForm=fin",
        "",
        "NounType=prop|Number=sing",
        "NounType=prop|Number=sing",
        "",
        "NounType=prop|Number=sing",
        "PunctType=peri",
    ]
    nlp = English()
    doc = nlp(text)
    for i in range(len(tags)):
        doc[i].tag_ = tags[i]
        doc[i].pos_ = pos[i]
        doc[i].set_morph(morphs[i])
        if i > 0:
            doc[i].is_sent_start = False
    return doc


@pytest.fixture
def sented_doc():
    text = "One sentence. Two sentences. Three sentences."
    nlp = English()
    doc = nlp(text)
    for i in range(len(doc)):
        if i % 3 == 0:
            doc[i].is_sent_start = True
        else:
            doc[i].is_sent_start = False
    return doc


def test_tokenization(sented_doc):
    scorer = Scorer()
    gold = {"sent_starts": [t.sent_start for t in sented_doc]}
    example = Example.from_dict(sented_doc, gold)
    scores = scorer.score([example])
    assert scores["token_acc"] == 1.0

    nlp = English()
    example.predicted = Doc(
        nlp.vocab,
        words=["One", "sentence.", "Two", "sentences.", "Three", "sentences."],
        spaces=[True, True, True, True, True, False],
    )
    example.predicted[1].is_sent_start = False
    scores = scorer.score([example])
    assert scores["token_acc"] == approx(0.66666666)
    assert scores["token_p"] == 0.5
    assert scores["token_r"] == approx(0.33333333)
    assert scores["token_f"] == 0.4


def test_sents(sented_doc):
    scorer = Scorer()
    gold = {"sent_starts": [t.sent_start for t in sented_doc]}
    example = Example.from_dict(sented_doc, gold)
    scores = scorer.score([example])
    assert scores["sents_f"] == 1.0

    # One sentence start is moved
    gold["sent_starts"][3] = 0
    gold["sent_starts"][4] = 1
    example = Example.from_dict(sented_doc, gold)
    scores = scorer.score([example])
    assert scores["sents_f"] == approx(0.3333333)


def test_las_per_type(en_vocab):
    # Gold and Doc are identical
    scorer = Scorer()
    examples = []
    for input_, annot in test_las_apple:
        doc = Doc(
            en_vocab, words=input_.split(" "), heads=annot["heads"], deps=annot["deps"]
        )
        gold = {"heads": annot["heads"], "deps": annot["deps"]}
        example = Example.from_dict(doc, gold)
        examples.append(example)
    results = scorer.score(examples)

    assert results["dep_uas"] == 1.0
    assert results["dep_las"] == 1.0
    assert results["dep_las_per_type"]["nsubj"]["p"] == 1.0
    assert results["dep_las_per_type"]["nsubj"]["r"] == 1.0
    assert results["dep_las_per_type"]["nsubj"]["f"] == 1.0
    assert results["dep_las_per_type"]["compound"]["p"] == 1.0
    assert results["dep_las_per_type"]["compound"]["r"] == 1.0
    assert results["dep_las_per_type"]["compound"]["f"] == 1.0

    # One dep is incorrect in Doc
    scorer = Scorer()
    examples = []
    for input_, annot in test_las_apple:
        doc = Doc(
            en_vocab, words=input_.split(" "), heads=annot["heads"], deps=annot["deps"],
        )
        gold = {"heads": annot["heads"], "deps": annot["deps"]}
        doc[0].dep_ = "compound"
        example = Example.from_dict(doc, gold)
        examples.append(example)
    results = scorer.score(examples)

    assert results["dep_uas"] == 1.0
    assert_almost_equal(results["dep_las"], 0.9090909)
    assert results["dep_las_per_type"]["nsubj"]["p"] == 0
    assert results["dep_las_per_type"]["nsubj"]["r"] == 0
    assert results["dep_las_per_type"]["nsubj"]["f"] == 0
    assert_almost_equal(results["dep_las_per_type"]["compound"]["p"], 0.666666666)
    assert results["dep_las_per_type"]["compound"]["r"] == 1.0
    assert results["dep_las_per_type"]["compound"]["f"] == 0.8


def test_ner_per_type(en_vocab):
    # Gold and Doc are identical
    scorer = Scorer()
    examples = []
    for input_, annot in test_ner_cardinal:
        doc = Doc(
            en_vocab,
            words=input_.split(" "),
            ents=["B-CARDINAL", "O", "B-CARDINAL"],
        )
        entities = offsets_to_biluo_tags(doc, annot["entities"])
        example = Example.from_dict(doc, {"entities": entities})
        # a hack for sentence boundaries
        example.predicted[1].is_sent_start = False
        example.reference[1].is_sent_start = False
        examples.append(example)
    results = scorer.score(examples)

    assert results["ents_p"] == 1.0
    assert results["ents_r"] == 1.0
    assert results["ents_f"] == 1.0
    assert results["ents_per_type"]["CARDINAL"]["p"] == 1.0
    assert results["ents_per_type"]["CARDINAL"]["r"] == 1.0
    assert results["ents_per_type"]["CARDINAL"]["f"] == 1.0

    # Doc has one missing and one extra entity
    # Entity type MONEY is not present in Doc
    scorer = Scorer()
    examples = []
    for input_, annot in test_ner_apple:
        doc = Doc(
            en_vocab,
            words=input_.split(" "),
            ents=["B-ORG", "O", "O", "O", "O", "B-GPE", "B-ORG", "O", "O", "O"],
        )
        entities = offsets_to_biluo_tags(doc, annot["entities"])
        example = Example.from_dict(doc, {"entities": entities})
        # a hack for sentence boundaries
        example.predicted[1].is_sent_start = False
        example.reference[1].is_sent_start = False
        examples.append(example)
    results = scorer.score(examples)

    assert results["ents_p"] == approx(0.6666666)
    assert results["ents_r"] == approx(0.6666666)
    assert results["ents_f"] == approx(0.6666666)
    assert "GPE" in results["ents_per_type"]
    assert "MONEY" in results["ents_per_type"]
    assert "ORG" in results["ents_per_type"]
    assert results["ents_per_type"]["GPE"]["p"] == 1.0
    assert results["ents_per_type"]["GPE"]["r"] == 1.0
    assert results["ents_per_type"]["GPE"]["f"] == 1.0
    assert results["ents_per_type"]["MONEY"]["p"] == 0
    assert results["ents_per_type"]["MONEY"]["r"] == 0
    assert results["ents_per_type"]["MONEY"]["f"] == 0
    assert results["ents_per_type"]["ORG"]["p"] == 0.5
    assert results["ents_per_type"]["ORG"]["r"] == 1.0
    assert results["ents_per_type"]["ORG"]["f"] == approx(0.6666666)


def test_tag_score(tagged_doc):
    # Gold and Doc are identical
    scorer = Scorer()
    gold = {
        "tags": [t.tag_ for t in tagged_doc],
        "pos": [t.pos_ for t in tagged_doc],
        "morphs": [str(t.morph) for t in tagged_doc],
        "sent_starts": [1 if t.is_sent_start else -1 for t in tagged_doc],
    }
    example = Example.from_dict(tagged_doc, gold)
    results = scorer.score([example])

    assert results["tag_acc"] == 1.0
    assert results["pos_acc"] == 1.0
    assert results["morph_acc"] == 1.0
    assert results["morph_per_feat"]["NounType"]["f"] == 1.0

    # Gold annotation is modified
    scorer = Scorer()
    tags = [t.tag_ for t in tagged_doc]
    tags[0] = "NN"
    pos = [t.pos_ for t in tagged_doc]
    pos[1] = "X"
    morphs = [str(t.morph) for t in tagged_doc]
    morphs[1] = "Number=sing"
    morphs[2] = "Number=plur"
    gold = {
        "tags": tags,
        "pos": pos,
        "morphs": morphs,
        "sent_starts": gold["sent_starts"],
    }
    example = Example.from_dict(tagged_doc, gold)
    results = scorer.score([example])

    assert results["tag_acc"] == 0.9
    assert results["pos_acc"] == 0.9
    assert results["morph_acc"] == approx(0.8)
    assert results["morph_per_feat"]["NounType"]["f"] == 1.0
    assert results["morph_per_feat"]["Poss"]["f"] == 0.0
    assert results["morph_per_feat"]["Number"]["f"] == approx(0.72727272)


def test_roc_auc_score():
    # Binary classification, toy tests from scikit-learn test suite
    y_true = [0, 1]
    y_score = [0, 1]
    tpr, fpr, _ = _roc_curve(y_true, y_score)
    roc_auc = _roc_auc_score(y_true, y_score)
    assert_array_almost_equal(tpr, [0, 0, 1])
    assert_array_almost_equal(fpr, [0, 1, 1])
    assert_almost_equal(roc_auc, 1.0)

    y_true = [0, 1]
    y_score = [1, 0]
    tpr, fpr, _ = _roc_curve(y_true, y_score)
    roc_auc = _roc_auc_score(y_true, y_score)
    assert_array_almost_equal(tpr, [0, 1, 1])
    assert_array_almost_equal(fpr, [0, 0, 1])
    assert_almost_equal(roc_auc, 0.0)

    y_true = [1, 0]
    y_score = [1, 1]
    tpr, fpr, _ = _roc_curve(y_true, y_score)
    roc_auc = _roc_auc_score(y_true, y_score)
    assert_array_almost_equal(tpr, [0, 1])
    assert_array_almost_equal(fpr, [0, 1])
    assert_almost_equal(roc_auc, 0.5)

    y_true = [1, 0]
    y_score = [1, 0]
    tpr, fpr, _ = _roc_curve(y_true, y_score)
    roc_auc = _roc_auc_score(y_true, y_score)
    assert_array_almost_equal(tpr, [0, 0, 1])
    assert_array_almost_equal(fpr, [0, 1, 1])
    assert_almost_equal(roc_auc, 1.0)

    y_true = [1, 0]
    y_score = [0.5, 0.5]
    tpr, fpr, _ = _roc_curve(y_true, y_score)
    roc_auc = _roc_auc_score(y_true, y_score)
    assert_array_almost_equal(tpr, [0, 1])
    assert_array_almost_equal(fpr, [0, 1])
    assert_almost_equal(roc_auc, 0.5)

    # same result as above with ROCAUCScore wrapper
    score = ROCAUCScore()
    score.score_set(0.5, 1)
    score.score_set(0.5, 0)
    assert_almost_equal(score.score, 0.5)

    # check that errors are raised in undefined cases and score is -inf
    y_true = [0, 0]
    y_score = [0.25, 0.75]
    with pytest.raises(ValueError):
        _roc_auc_score(y_true, y_score)

    score = ROCAUCScore()
    score.score_set(0.25, 0)
    score.score_set(0.75, 0)
    assert score.score == -float("inf")

    y_true = [1, 1]
    y_score = [0.25, 0.75]
    with pytest.raises(ValueError):
        _roc_auc_score(y_true, y_score)

    score = ROCAUCScore()
    score.score_set(0.25, 1)
    score.score_set(0.75, 1)
    assert score.score == -float("inf")
