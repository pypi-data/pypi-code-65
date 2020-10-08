from datetime import datetime, timezone

import pytest

from anyscale.client.openapi_client.models.cloud import Cloud  # type: ignore
from anyscale.client.openapi_client.models.project import Project  # type: ignore
from anyscale.client.openapi_client.models.session import Session  # type: ignore
from anyscale.client.openapi_client.models.session_command import SessionCommand  # type: ignore


@pytest.fixture(scope="module")  # type: ignore
def cloud_test_data() -> Cloud:
    return Cloud(
        id="cloud_id_1",
        name="cloud_name_1",
        provider="provider",
        region="region",
        credentials="credentials",
        creator_id="creator_id",
        type="PUBLIC",
    )


@pytest.fixture(scope="module")  # type: ignore
def project_test_data() -> Project:
    return Project(
        name="project_name",
        description="test project",
        cloud_id="cloud_id",
        initial_cluster_config="initial_config",
        id="project_id",
        created_at=datetime.now(tz=timezone.utc),
        creator_id="creator_id",
        is_owner=True,
        directory_name="/directory/name",
    )


@pytest.fixture(scope="module")  # type: ignore
def session_test_data() -> Session:
    return Session(
        id="session_id",
        name="session_name",
        created_at=datetime.now(tz=timezone.utc),
        snapshots_history=[],
        tensorboard_available=False,
        project_id="project_id",
        state="Running",
        last_activity_at=datetime.now(tz=timezone.utc),
    )


@pytest.fixture(scope="module")  # type: ignore
def session_command_test_data() -> SessionCommand:
    return SessionCommand(
        id="session_command_id",
        created_at=datetime.now(tz=timezone.utc),
        name="session_command",
        params="params",
        shell="shell",
        shell_command="shell_command",
    )
