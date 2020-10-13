from typing import Any, Dict

from click import ClickException
from openapi_client.rest import ApiException  # type: ignore

from anyscale.client.openapi_client.api.default_api import DefaultApi  # type: ignore


def get_cloud_json_from_id(cloud_id: str, api_client: DefaultApi) -> Dict["str", Any]:
    try:
        cloud = api_client.get_cloud_api_v2_clouds_cloud_id_get(
            cloud_id=cloud_id
        ).result
    except ApiException:
        raise ClickException(
            f"The cloud with id, {cloud_id} has been deleted. Please create a new cloud with `anyscale cloud setup`."
        )
    return {
        "id": cloud.id,
        "name": cloud.name,
        "provider": cloud.provider,
        "region": cloud.region,
        "credentials": cloud.credentials,
    }
