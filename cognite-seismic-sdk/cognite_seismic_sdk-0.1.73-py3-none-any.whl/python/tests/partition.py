from uuid import uuid4

import pytest
from cognite.seismic import CogniteSeismicClient


def get_client() -> CogniteSeismicClient:
    return CogniteSeismicClient(api_key=None, base_url="localhost", port=50052, insecure=True)


def test_search_partitions():
    client = get_client()
    assert len(list(client.partition.search(name="test"))) > 0


def test_create_partition():
    client = get_client()
    extid = str(uuid4())
    partition = client.partition.create(external_id=extid)
    assert partition.external_id == extid


def test_list_partitions():
    client = get_client()
    assert len(list(client.partition.list())) > 0
