from unittest.mock import Mock

from anyscale.client.openapi_client.models.cloud import Cloud  # type: ignore
from anyscale.client.openapi_client.models.cloud_response import CloudResponse  # type: ignore
from anyscale.cloud import get_cloud_json_from_id


def test_get_cloud_json_from_id(cloud_test_data: Cloud) -> None:
    mock_api_client = Mock()
    mock_api_client.get_cloud_api_v2_clouds_cloud_id_get.return_value = CloudResponse(
        result=cloud_test_data
    )

    cloud_json = get_cloud_json_from_id(cloud_test_data.id, api_client=mock_api_client)
    expected_json = {
        "id": cloud_test_data.id,
        "name": cloud_test_data.name,
        "provider": cloud_test_data.provider,
        "region": cloud_test_data.region,
        "credentials": cloud_test_data.credentials,
    }
    assert cloud_json == expected_json
    mock_api_client.get_cloud_api_v2_clouds_cloud_id_get.assert_called_once_with(
        cloud_id=cloud_test_data.id
    )
