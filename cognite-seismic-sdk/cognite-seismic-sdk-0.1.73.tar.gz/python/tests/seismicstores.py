import pytest
from cognite.seismic import BinaryHeader, CogniteSeismicClient, TextHeader


def get_client() -> CogniteSeismicClient:
    return CogniteSeismicClient(api_key=None, base_url="localhost", port=50052, insecure=True)


def test_list_seismicstores():
    client = get_client()
    assert len([x for x in client.seismicstores.list()]) > 0
