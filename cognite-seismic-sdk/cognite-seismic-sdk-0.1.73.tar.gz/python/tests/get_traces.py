import pytest
from cognite.seismic import CogniteSeismicClient


def get_client() -> CogniteSeismicClient:
    return CogniteSeismicClient(api_key=None, base_url="localhost", port=50052, insecure=True)


def test_get_volume():
    client = get_client()
    assert len([x for x in client.volume_seismic.get_volume(external_id="aaaaaa")]) > 0
