from unittest.mock import Mock
import pytest
from cloud_queue_worker.orchestrator import Orchestrator
from cloud_queue_worker.errors import ConfigError


def test_check_queue_mapping(monkeypatch):
    monkeypatch.setattr(
        "cloud_queue_worker.orchestrator.get_client",
        Mock(return_value=Mock(list_queues=Mock(return_value={"QueueUrls": ["mock_queue_url"]}))),
    )
    Orchestrator(
        {"mock_queue_url": "mock_method"},
        5,
        {
            "cloud_provider": "aws",
            "aws_access_key_id": "mock_aws_access_key_id",
            "aws_access_key_secret": "mock_aws_access_key_secret",
            "region_name": "mock_region_name",
        },
    )


def test_check_queue_mapping_with_error(monkeypatch):
    monkeypatch.setattr(
        "cloud_queue_worker.orchestrator.get_client",
        Mock(return_value=Mock(list_queues=Mock(return_value={"QueueUrls": ["invalid_queue"]}))),
    )
    with pytest.raises(ConfigError):
        Orchestrator(
            {"mock_queue_url": "mock_method"},
            5,
            {
                "cloud_provider": "aws",
                "aws_access_key_id": "mock_aws_access_key_id",
                "aws_access_key_secret": "mock_aws_access_key_secret",
                "region_name": "mock_region_name",
            },
        )


def test_initialize_workers(monkeypatch):
    monkeypatch.setattr(
        "cloud_queue_worker.orchestrator.get_client",
        Mock(return_value=Mock(list_queues=Mock(return_value={"QueueUrls": ["mock_queue_url"]}))),
    )
    orchestrator = Orchestrator(
        {"mock_queue_url": "mock_method"},
        5,
        {
            "cloud_provider": "aws",
            "aws_access_key_id": "mock_aws_access_key_id",
            "aws_access_key_secret": "mock_aws_access_key_secret",
            "region_name": "mock_region_name",
        },
    )
    assert len(orchestrator.read_workers) == 1
    assert len(orchestrator.executor_workers) == 5


def test_run(monkeypatch):
    mock_read_worker_start = Mock()
    mock_read_worker = Mock(return_value=mock_read_worker_start)
    mock_executor_worker_start = Mock()
    mock_executor_worker = Mock(return_value=mock_executor_worker_start)
    monkeypatch.setattr(
        "cloud_queue_worker.orchestrator.get_client",
        Mock(return_value=Mock(list_queues=Mock(return_value={"QueueUrls": ["mock_queue_url"]}))),
    )
    monkeypatch.setattr("cloud_queue_worker.orchestrator.ReadWorker", mock_read_worker)
    monkeypatch.setattr("cloud_queue_worker.orchestrator.ExecutorWorker", mock_executor_worker)
    orchestrator = Orchestrator(
        {"mock_queue_url": "mock_method"},
        5,
        {
            "cloud_provider": "aws",
            "aws_access_key_id": "mock_aws_access_key_id",
            "aws_access_key_secret": "mock_aws_access_key_secret",
            "region_name": "mock_region_name",
        },
    )
    orchestrator._is_running = False
    orchestrator.run()
    assert mock_read_worker_start.start.call_count == 1
    assert mock_executor_worker_start.start.call_count == 5


def test_stop(monkeypatch):
    mock_read_worker_join = Mock()
    mock_read_worker_exit_set = Mock(set=Mock())
    mock_read_worker_exit = Mock(exit=mock_read_worker_exit_set, join=mock_read_worker_join)
    mock_read_worker = Mock(return_value=mock_read_worker_exit)
    mock_executor_worker_join = Mock()
    mock_executor_worker_exit_set = Mock(set=Mock())
    mock_executor_worker_exit = Mock(exit=mock_executor_worker_exit_set, join=mock_executor_worker_join)
    mock_executor_worker = Mock(return_value=mock_executor_worker_exit)
    mock_close_queue = Mock(close=Mock())
    mock_queue = Mock(return_value=mock_close_queue)
    monkeypatch.setattr(
        "cloud_queue_worker.orchestrator.get_client",
        Mock(return_value=Mock(list_queues=Mock(return_value={"QueueUrls": ["mock_queue_url"]}))),
    )
    monkeypatch.setattr("cloud_queue_worker.orchestrator.ReadWorker", mock_read_worker)
    monkeypatch.setattr("cloud_queue_worker.orchestrator.ExecutorWorker", mock_executor_worker)
    monkeypatch.setattr("cloud_queue_worker.orchestrator.Queue", mock_queue)
    orchestrator = Orchestrator(
        {"mock_queue_url": "mock_method"},
        5,
        {
            "cloud_provider": "aws",
            "aws_access_key_id": "mock_aws_access_key_id",
            "aws_access_key_secret": "mock_aws_access_key_secret",
            "region_name": "mock_region_name",
        },
    )
    orchestrator._stop()
    assert mock_read_worker_exit_set.set.call_count == 1
    assert mock_executor_worker_exit_set.set.call_count == 5
    assert mock_executor_worker_join.call_count == 5
    assert mock_read_worker_join.call_count == 1
    mock_close_queue.close.assert_called_once_with()
