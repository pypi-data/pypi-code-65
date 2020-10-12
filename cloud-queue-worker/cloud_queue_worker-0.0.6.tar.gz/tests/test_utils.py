from unittest.mock import Mock
from cloud_queue_worker.utils import get_client


def test_get_client(monkeypatch):
    mock_boto_client = Mock()
    mock_config = {
        "aws_access_key_id": "mock_aws_access_key_id",
        "aws_secret_access_key": "mock_aws_secret_access_key",
        "region_name": "mock_region_name",
    }
    monkeypatch.setattr("cloud_queue_worker.utils.boto3.client", mock_boto_client)
    get_client(mock_config)
    mock_boto_client.assert_called_once_with(
        "sqs",
        aws_secret_access_key="mock_aws_secret_access_key",
        aws_access_key_id="mock_aws_access_key_id",
        region_name="mock_region_name",
        endpoint_url="https://sqs.mock_region_name.amazonaws.com"
    )
