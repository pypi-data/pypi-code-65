import pytest

from spacy import util
from spacy.util import dot_to_object, SimpleFrozenList
from thinc.api import Config, Optimizer, ConfigValidationError
from spacy.training.batchers import minibatch_by_words
from spacy.lang.en import English
from spacy.lang.nl import Dutch
from spacy.language import DEFAULT_CONFIG_PATH
from spacy.schemas import ConfigSchemaTraining

from .util import get_random_doc


@pytest.mark.parametrize(
    "doc_sizes, expected_batches",
    [
        ([400, 400, 199], [3]),
        ([400, 400, 199, 3], [4]),
        ([400, 400, 199, 3, 200], [3, 2]),
        ([400, 400, 199, 3, 1], [5]),
        ([400, 400, 199, 3, 1, 1500], [5]),  # 1500 will be discarded
        ([400, 400, 199, 3, 1, 200], [3, 3]),
        ([400, 400, 199, 3, 1, 999], [3, 3]),
        ([400, 400, 199, 3, 1, 999, 999], [3, 2, 1, 1]),
        ([1, 2, 999], [3]),
        ([1, 2, 999, 1], [4]),
        ([1, 200, 999, 1], [2, 2]),
        ([1, 999, 200, 1], [2, 2]),
    ],
)
def test_util_minibatch(doc_sizes, expected_batches):
    docs = [get_random_doc(doc_size) for doc_size in doc_sizes]
    tol = 0.2
    batch_size = 1000
    batches = list(
        minibatch_by_words(docs, size=batch_size, tolerance=tol, discard_oversize=True)
    )
    assert [len(batch) for batch in batches] == expected_batches

    max_size = batch_size + batch_size * tol
    for batch in batches:
        assert sum([len(doc) for doc in batch]) < max_size


@pytest.mark.parametrize(
    "doc_sizes, expected_batches",
    [
        ([400, 4000, 199], [1, 2]),
        ([400, 400, 199, 3000, 200], [1, 4]),
        ([400, 400, 199, 3, 1, 1500], [1, 5]),
        ([400, 400, 199, 3000, 2000, 200, 200], [1, 1, 3, 2]),
        ([1, 2, 9999], [1, 2]),
        ([2000, 1, 2000, 1, 1, 1, 2000], [1, 1, 1, 4]),
    ],
)
def test_util_minibatch_oversize(doc_sizes, expected_batches):
    """ Test that oversized documents are returned in their own batch"""
    docs = [get_random_doc(doc_size) for doc_size in doc_sizes]
    tol = 0.2
    batch_size = 1000
    batches = list(
        minibatch_by_words(docs, size=batch_size, tolerance=tol, discard_oversize=False)
    )
    assert [len(batch) for batch in batches] == expected_batches


def test_util_dot_section():
    cfg_string = """
    [nlp]
    lang = "en"
    pipeline = ["textcat"]

    [components]

    [components.textcat]
    factory = "textcat"

    [components.textcat.model]
    @architectures = "spacy.TextCatBOW.v1"
    exclusive_classes = true
    ngram_size = 1
    no_output_layer = false
    """
    nlp_config = Config().from_str(cfg_string)
    en_nlp = util.load_model_from_config(nlp_config, auto_fill=True)
    default_config = Config().from_disk(DEFAULT_CONFIG_PATH)
    default_config["nlp"]["lang"] = "nl"
    nl_nlp = util.load_model_from_config(default_config, auto_fill=True)
    # Test that creation went OK
    assert isinstance(en_nlp, English)
    assert isinstance(nl_nlp, Dutch)
    assert nl_nlp.pipe_names == []
    assert en_nlp.pipe_names == ["textcat"]
    # not exclusive_classes
    assert en_nlp.get_pipe("textcat").model.attrs["multi_label"] is False
    # Test that default values got overwritten
    assert en_nlp.config["nlp"]["pipeline"] == ["textcat"]
    assert nl_nlp.config["nlp"]["pipeline"] == []  # default value []
    # Test proper functioning of 'dot_to_object'
    with pytest.raises(KeyError):
        dot_to_object(en_nlp.config, "nlp.pipeline.tagger")
    with pytest.raises(KeyError):
        dot_to_object(en_nlp.config, "nlp.unknownattribute")
    T = util.registry.resolve(nl_nlp.config["training"], schema=ConfigSchemaTraining)
    assert isinstance(dot_to_object({"training": T}, "training.optimizer"), Optimizer)


def test_simple_frozen_list():
    t = SimpleFrozenList(["foo", "bar"])
    assert t == ["foo", "bar"]
    assert t.index("bar") == 1  # okay method
    with pytest.raises(NotImplementedError):
        t.append("baz")
    with pytest.raises(NotImplementedError):
        t.sort()
    with pytest.raises(NotImplementedError):
        t.extend(["baz"])
    with pytest.raises(NotImplementedError):
        t.pop()
    t = SimpleFrozenList(["foo", "bar"], error="Error!")
    with pytest.raises(NotImplementedError):
        t.append("baz")


def test_resolve_dot_names():
    config = {
        "training": {"optimizer": {"@optimizers": "Adam.v1"}},
        "foo": {"bar": "training.optimizer", "baz": "training.xyz"},
    }
    result = util.resolve_dot_names(config, ["training.optimizer"])
    assert isinstance(result[0], Optimizer)
    with pytest.raises(ConfigValidationError) as e:
        util.resolve_dot_names(config, ["training.xyz", "training.optimizer"])
    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0]["loc"] == ["training", "xyz"]
