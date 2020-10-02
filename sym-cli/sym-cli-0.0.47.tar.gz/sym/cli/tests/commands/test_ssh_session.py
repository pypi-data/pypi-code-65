import pytest

from sym.cli.errors import SuppressedError
from sym.cli.tests.helpers.capture import CaptureCommand

INSTANCE_ID = "123"
SESSION_ID = "456"


def start_session_stub(make_stub):
    ssm = make_stub("ssm")
    ssm.add_response("start_session", {"SessionId": SESSION_ID})
    ssm.add_response(
        "terminate_session", {"SessionId": SESSION_ID}, {"SessionId": SESSION_ID}
    )


@pytest.fixture
def ssh_session_tester(command_tester):
    return command_tester(["ssh-session", "test", "--instance", INSTANCE_ID])


def test_ssh_session(ssh_session_tester, capture_command: CaptureCommand):
    def setup(make_stub):
        start_session_stub(make_stub)

    with ssh_session_tester(setup=setup):
        capture_command.assert_command(
            ["exec", "true"],
            ["session-manager-plugin"],
        )


def test_ssh_session_error(ssh_session_tester, capture_command: CaptureCommand):
    def setup(make_stub):
        start_session_stub(make_stub)
        capture_command.register_output(r"session-manager-plugin", "timeout", exit_code=1)

    with ssh_session_tester(setup=setup, exception=SuppressedError):
        capture_command.assert_command(
            ["exec", "true"],
            ["session-manager-plugin"],
        )
