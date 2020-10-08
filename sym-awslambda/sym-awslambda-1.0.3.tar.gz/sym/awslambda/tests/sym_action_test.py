import pytest

from sym.awslambda.decorators import sym_action
from sym.awslambda.dispatch import is_registered, reset
from sym.awslambda.errors import SymError


@pytest.fixture
def reset_dispatch():
    reset()


def test_approve_action(reset_dispatch):

    assert not is_registered("approve")

    @sym_action("approve")
    def fn():
        print("Approve handler")

    assert is_registered("approve")


def test_already_registered_action(reset_dispatch):
    @sym_action("approve")
    def fn():
        print("Approve handler")

    with pytest.raises(SymError):

        @sym_action("approve")
        def fn():
            print("Approve handler")


def test_unsupported_action(reset_dispatch):

    assert not is_registered("foo")

    with pytest.raises(SymError):

        @sym_action("foo")
        def fn():
            print("Foo handler")
