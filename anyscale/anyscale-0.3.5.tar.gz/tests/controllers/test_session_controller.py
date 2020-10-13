from datetime import datetime, timezone
from unittest.mock import call, Mock, patch

import pytest

from anyscale.client.openapi_client import (  # type: ignore
    Session,
    SessionListResponse,
    StopSessionOptions,
)
from anyscale.controllers.session_controller import SessionController


@pytest.fixture()  # type: ignore
def mock_api_client(mock_api_client_with_session: Mock) -> Mock:
    mock_api_client = mock_api_client_with_session
    mock_api_client.stop_session_api_v2_sessions_session_id_stop_post.return_value = (
        None
    )

    return mock_api_client


def test_stop_single_session(session_test_data: Session, mock_api_client: Mock) -> None:
    session_controller = SessionController(api_client=mock_api_client)

    mock_project_definition = Mock()
    mock_project_definition.root = "/some/directory"
    mock_load_project_or_throw = Mock(return_value=mock_project_definition)

    mock_get_project_id = Mock(return_value=session_test_data.project_id)

    with patch.multiple(
        "anyscale.controllers.session_controller",
        load_project_or_throw=mock_load_project_or_throw,
        get_project_id=mock_get_project_id,
    ):
        session_controller.stop(
            "test-name",
            terminate=False,
            delete=False,
            workers_only=False,
            keep_min_workers=False,
        )

    mock_api_client.stop_session_api_v2_sessions_session_id_stop_post.assert_called_once_with(
        session_test_data.id,
        StopSessionOptions(
            terminate=False, delete=False, workers_only=False, keep_min_workers=False
        ),
    )

    mock_load_project_or_throw.assert_called_once_with()
    mock_get_project_id.assert_called_once_with("/some/directory")


@pytest.fixture()  # type: ignore
def mock_api_client_multiple_sessions(base_mock_api_client: Mock) -> Mock:
    base_mock_api_client.list_sessions_api_v2_sessions_get.return_value = SessionListResponse(
        results=[
            Session(
                id="ses_1",
                name="session_name",
                created_at=datetime.now(tz=timezone.utc),
                snapshots_history=[],
                tensorboard_available=False,
                project_id="project_id",
                state="Running",
                last_activity_at=datetime.now(tz=timezone.utc),
            ),
            Session(
                id="ses_2",
                name="session_name2",
                created_at=datetime.now(tz=timezone.utc),
                snapshots_history=[],
                tensorboard_available=False,
                project_id="project_id",
                state="Running",
                last_activity_at=datetime.now(tz=timezone.utc),
            ),
        ]
    )
    base_mock_api_client.stop_session_api_v2_sessions_session_id_stop_post.return_value = (
        None
    )

    return base_mock_api_client


def test_stop_multiple_sessions(mock_api_client_multiple_sessions: Mock) -> None:
    mock_api_client = mock_api_client_multiple_sessions
    session_controller = SessionController(api_client=mock_api_client)

    mock_project_definition = Mock()
    mock_project_definition.root = "/some/directory"
    mock_load_project_or_throw = Mock(return_value=mock_project_definition)

    mock_get_project_id = Mock(return_value="project_id")

    with patch.multiple(
        "anyscale.controllers.session_controller",
        load_project_or_throw=mock_load_project_or_throw,
        get_project_id=mock_get_project_id,
    ):
        session_controller.stop(
            "ses_?",
            terminate=True,
            delete=True,
            workers_only=True,
            keep_min_workers=True,
        )

    mock_api_client.stop_session_api_v2_sessions_session_id_stop_post.assert_has_calls(
        [
            call(
                "ses_1",
                StopSessionOptions(
                    terminate=True,
                    delete=True,
                    workers_only=True,
                    keep_min_workers=True,
                ),
            ),
            call(
                "ses_2",
                StopSessionOptions(
                    terminate=True,
                    delete=True,
                    workers_only=True,
                    keep_min_workers=True,
                ),
            ),
        ]
    )

    mock_load_project_or_throw.assert_called_once_with()
    mock_get_project_id.assert_called_once_with("/some/directory")
