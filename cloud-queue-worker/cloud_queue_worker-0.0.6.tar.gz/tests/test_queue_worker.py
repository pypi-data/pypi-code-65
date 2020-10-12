from unittest.mock import Mock
import pytest
from marshmallow.exceptions import ValidationError
from cloud_queue_worker.queue_worker import CloudQueueWorker


def test_update_config():
    new_config = {
        "queue_mapping": {"mock_queue_url": "function_to_call"},
        "concurrency": 3,
        "cloud_provider_config": {
            "cloud_provider": "aws",
            "aws_access_key_id": "mock_aws_access_key_id",
            "aws_access_key_secret": "mock_aws_access_key_secret",
            "region_name": "mock_region_name",
        },
    }
    cloud_queue_worker = CloudQueueWorker()
    cloud_queue_worker.update_config(new_config)
    assert vars(cloud_queue_worker) == new_config


@pytest.mark.parametrize(
    "config",
    [
        {
            "queue_mapping": {"mock_queue_url": "function_to_call"},
            "cloud_provider_config": {
                "cloud_provider": "aws",
                "aws_access_key_id": "mock_aws_access_key_id",
                "aws_access_key_secret": "mock_aws_access_key_secret",
                "region_name": "mock_region_name",
            },
        },
        {
            "concurrency": 2,
            "cloud_provider_config": {
                "cloud_provider": "aws",
                "aws_access_key_id": "mock_aws_access_key_id",
                "aws_access_key_secret": "mock_aws_access_key_secret",
                "region_name": "mock_region_name",
            },
        },
        {
            "queue_mapping": {"mock_queue_url": "function_to_call"},
            "concurrency": 2,
        },
        {
            "queue_mapping": {"mock_queue_url": "function_to_call"},
            "cloud_provider_config": {
                "cloud_provider": "invalid_cloud_provider",
                "aws_access_key_id": "mock_aws_access_key_id",
                "aws_access_key_secret": "mock_aws_access_key_secret",
                "region_name": "mock_region_name",
            },
        },
        {
            "queue_mapping": {"mock_queue_url": "function_to_call"},
            "cloud_provider_config": {
                "cloud_provider": "aws",
                "aws_access_key_id": "mock_aws_access_key_id",
                "aws_access_key_secret": "mock_aws_access_key_secret",
            },
        },
    ],
)
def test_run_with_invalid_config(config):
    cloud_queue_worker = CloudQueueWorker()
    cloud_queue_worker.update_config(config)
    with pytest.raises(ValidationError):
        cloud_queue_worker.run()


def test_run(monkeypatch):
    mock_run = Mock()
    mock_orchestrator = Mock(return_value=mock_run)
    new_config = {
        "queue_mapping": {"mock_queue_url": "function_to_call"},
        "concurrency": 3,
        "cloud_provider_config": {
            "cloud_provider": "aws",
            "aws_access_key_id": "mock_aws_access_key_id",
            "aws_secret_access_key": "mock_aws_access_key_secret",
            "region_name": "mock_region_name",
        },
    }
    cloud_queue_worker = CloudQueueWorker()
    cloud_queue_worker.update_config(new_config)
    monkeypatch.setattr("cloud_queue_worker.queue_worker.Orchestrator", mock_orchestrator)
    cloud_queue_worker.run()
    mock_run.run.assert_called_once_with()
