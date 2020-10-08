from unittest.mock import Mock

from anyscale.client.openapi_client.models.project import Project  # type: ignore
from anyscale.client.openapi_client.models.project_response import ProjectResponse  # type: ignore
from anyscale.client.openapi_client.models.session import Session  # type: ignore
from anyscale.client.openapi_client.models.session_list_response import SessionListResponse  # type: ignore
from anyscale.project import (
    get_proj_name_from_id,
    get_project_session,
    get_project_sessions,
)


def test_get_project_sessions(session_test_data: Session) -> None:
    mock_api_client = Mock()
    mock_api_client.list_sessions_api_v2_sessions_get.return_value = SessionListResponse(
        results=[session_test_data]
    )

    sessions = get_project_sessions(session_test_data.project_id, None, mock_api_client)

    assert sessions == [session_test_data]
    mock_api_client.list_sessions_api_v2_sessions_get.assert_called_once_with(
        project_id=session_test_data.project_id, name_match=None, active_only=True
    )


def test_get_project_session(session_test_data: Session) -> None:
    mock_api_client = Mock()
    mock_api_client.list_sessions_api_v2_sessions_get.return_value = SessionListResponse(
        results=[session_test_data]
    )

    session = get_project_session(session_test_data.project_id, None, mock_api_client)

    assert session == session_test_data
    mock_api_client.list_sessions_api_v2_sessions_get.assert_called_once_with(
        project_id=session_test_data.project_id, name_match=None, active_only=True
    )


def test_get_proj_name_from_id(project_test_data: Project) -> None:
    mock_api_client = Mock()
    mock_api_client.get_project_api_v2_projects_project_id_get.return_value = ProjectResponse(
        result=project_test_data
    )
    project_name = get_proj_name_from_id(project_test_data.id, mock_api_client)

    assert project_name == project_test_data.name
    mock_api_client.get_project_api_v2_projects_project_id_get.assert_called_once_with(
        project_id=project_test_data.id
    )
