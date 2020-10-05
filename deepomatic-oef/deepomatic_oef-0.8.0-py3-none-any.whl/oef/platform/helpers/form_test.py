import pytest
from .form import Form
from .tags import ViewType

def test_fail_if_non_existing_model():
    def get_backend_fn():
        raise NotImplemented

    with pytest.raises(AssertionError):
        Form({
            ViewType.CLASSIFICATION: ('prefix.', ['foo', 'bar'], 'other')
        })
