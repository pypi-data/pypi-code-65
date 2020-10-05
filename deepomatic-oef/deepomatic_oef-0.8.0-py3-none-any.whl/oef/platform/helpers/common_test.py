import pytest
from .common import CHECK_TYPE, CHECK_LIST, CHECK_DICT, BadType

def test_checktype():
    CHECK_TYPE(0.5, float)
    CHECK_TYPE(0.5, (int, float))
    CHECK_TYPE(Exception('foo'), Exception)

    with pytest.raises(BadType):
        CHECK_TYPE(0.5, int)

    CHECK_TYPE(False, int)   # a bool is a int
    CHECK_TYPE(0.5, (int, float), exclude_types=bool)
    with pytest.raises(BadType):
        CHECK_TYPE(False, int, exclude_types=bool)

def test_checklist():
    CHECK_LIST([0.5], float)

    with pytest.raises(BadType):
        CHECK_LIST(["foo"], float)

    with pytest.raises(BadType):
        CHECK_LIST({0.5}, float)

    assert CHECK_LIST(None, float) == []

def test_checkdict():
    CHECK_DICT({"bar": 0.5}, float)

    with pytest.raises(BadType):
        CHECK_DICT({"foo": "bar"}, float)

    with pytest.raises(BadType):
        CHECK_DICT([0.5], float)

    assert CHECK_DICT(None, float) == {}
