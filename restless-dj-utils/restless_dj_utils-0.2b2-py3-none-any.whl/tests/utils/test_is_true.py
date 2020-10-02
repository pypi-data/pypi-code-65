from restless_dj_utils.utils.is_true import is_true


def test_is_true():
    """Validate is_true return true/false where expected"""
    assert is_true("1") is True
    assert is_true("0") is False

    assert is_true("True") is True
    assert is_true("False") is False

    assert is_true("true") is True
    assert is_true("false") is False

    assert is_true("TRUE") is True
    assert is_true("FALSE") is False
