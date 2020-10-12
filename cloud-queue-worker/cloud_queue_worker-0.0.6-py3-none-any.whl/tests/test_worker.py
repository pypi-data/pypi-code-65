from multiprocessing import Queue, Value
from unittest.mock import Mock, MagicMock
import pytest
from cloud_queue_worker.worker.worker import Worker, ReadWorker, ExecutorWorker


def test_worker():
    with pytest.raises(TypeError):
        Worker(
            Queue(),
            {
                "cloud_provider": "aws",
                "aws_access_key_id": "mock_aws_access_key_id",
                "aws_access_key_secret": "mock_aws_access_key_secret",
                "region_name": "mock_region_name",
            },
        )


def test_read_worker_fetch_messages():
    worker = ReadWorker(
        Queue(),
        {
            "cloud_provider": "aws",
            "aws_access_key_id": "mock_aws_access_key_id",
            "aws_access_key_secret": "mock_aws_access_key_secret",
            "region_name": "mock_region_name",
        },
        "mock_queue_url",
        Value("i", 0),
    )
    mock_messages = Mock(return_value={"Messages": ["test"]})
    mock_client = Mock(receive_message=mock_messages)
    result = worker._fetch_messages(mock_client)
    mock_client.receive_message.assert_called_once_with(
        QueueUrl="mock_queue_url",
        MaxNumberOfMessages=10,
        WaitTimeSeconds=20,
    )
    assert result == ["test"]


def test_send_messages_to_executor():
    mock_put_in_queue = Mock()
    mock_queue = Mock(put=mock_put_in_queue)
    worker = ReadWorker(
        mock_queue,
        {
            "cloud_provider": "aws",
            "aws_access_key_id": "mock_aws_access_key_id",
            "aws_access_key_secret": "mock_aws_access_key_secret",
            "region_name": "mock_region_name",
        },
        "mock_queue_url",
        Value("i", 0),
    )
    worker._send_messages_to_executor(["message1"])
    mock_put_in_queue.assert_called_once_with({"message": "message1", "queue_url": "mock_queue_url"})
    assert worker.internal_queue_size.value == 1


def test_executor_worker_fetch_message():
    executor_queue = Queue()
    try:
        executor_queue.put("message")
        worker = ExecutorWorker(
            {"mock_queue_url": "mock_method"},
            executor_queue,
            {
                "cloud_provider": "aws",
                "aws_access_key_id": "mock_aws_access_key_id",
                "aws_access_key_secret": "mock_aws_access_key_secret",
                "region_name": "mock_region_name",
            },
            Value("i", 1),
        )
        result = worker._fetch_message()
        assert result == "message"
        assert worker.internal_queue_size.value == 0
    finally:
        executor_queue.close()


def test_executor_worker_fetch_message_without_message_in_internal_queue():
    executor_queue = Queue()
    try:
        worker = ExecutorWorker(
            {"mock_queue_url": "mock_method"},
            executor_queue,
            {
                "cloud_provider": "aws",
                "aws_access_key_id": "mock_aws_access_key_id",
                "aws_access_key_secret": "mock_aws_access_key_secret",
                "region_name": "mock_region_name",
            },
            Value("i", 0),
        )
        result = worker._fetch_message()
        assert result is None
    finally:
        executor_queue.close()


def test_acknowledge():
    mock_client = Mock()
    worker = ExecutorWorker(
        {"mock_queue_url": "mock_method"},
        Queue(),
        {
            "cloud_provider": "aws",
            "aws_access_key_id": "mock_aws_access_key_id",
            "aws_access_key_secret": "mock_aws_access_key_secret",
            "region_name": "mock_region_name",
        },
        Value("i", 1),
    )
    worker._acknowledge({"queue_url": "mock_queue_url", "message": {"ReceiptHandle": "mockReceiptHandle"}}, mock_client)
    mock_client.delete_message.assert_called_once_with(QueueUrl="mock_queue_url", ReceiptHandle="mockReceiptHandle")


def test_handle_message(monkeypatch):
    worker = ExecutorWorker(
        {"mock_queue_url": "mymockmodule.mock_method"},
        Queue(),
        {
            "cloud_provider": "aws",
            "aws_access_key_id": "mock_aws_access_key_id",
            "aws_access_key_secret": "mock_aws_access_key_secret",
            "region_name": "mock_region_name",
        },
        Value("i", 0),
    )
    mock_method = Mock()
    mock_import_module = MagicMock()
    mock_import_module["mock_method"] = "oui"
    monkeypatch.setattr(
        "cloud_queue_worker.worker.worker.importlib", Mock(import_module=Mock(return_value=mock_import_module))
    )
    worker._handle_message({"queue_url": "mock_queue_url", "message": {"ReceiptHandle": "mockReceiptHandle"}})
    mock_import_module.mock_method.assert_called_once_with({"ReceiptHandle": "mockReceiptHandle"})
