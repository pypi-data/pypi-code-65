import pytest

from sym.awslambda import dispatch
from sym.awslambda.decorators import sym_action
from sym.awslambda.errors import SymError


@pytest.fixture
def reset_dispatch():
    dispatch.reset()


APPROVAL = {
    "action": "approve",
    "payload": {
        "schema": {"version": 1},
        "request": {
            "schema": {"version": 1},
            "target": {
                "user": {
                    "identities": [
                        {"service": 2, "id": "requester+okta@example.com"},
                        {"service": 1, "id": "requester+slack@example.com"},
                    ]
                },
                "resource": {"service": 4, "id": "staging"},
            },
            "meta": {"reason": "Foo"},
        },
        "meta": {
            "approver": {
                "identities": [
                    {"service": 2, "id": "approver+okta@example.com"},
                    {"service": 1, "id": "approver+slack@example.com"},
                ]
            }
        },
        "@type": "type.googleapis.com/sym.messages.Approval",
    },
}


def test_approve_action(reset_dispatch):
    message = None

    def fn(m, c):
        nonlocal message

        message = m

    dispatch.register("approve", fn)

    dispatch.dispatch(APPROVAL, None)

    assert message is not None
    assert message.request.meta.reason == "Foo"
