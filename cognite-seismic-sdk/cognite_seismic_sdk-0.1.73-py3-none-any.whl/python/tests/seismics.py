from uuid import uuid4

import pytest
from cognite.seismic import BinaryHeader, CogniteSeismicClient, TextHeader


def get_client() -> CogniteSeismicClient:
    return CogniteSeismicClient(api_key=None, base_url="localhost", port=50052, insecure=True)


def test_create_seismic():
    client = get_client()
    extid = str(uuid4())
    seismic = client.seismics.create(external_id=extid, partition_identifier=3, seismic_store_id=6)


def test_create_seismic_with_header():
    client = get_client()
    extid = str(uuid4())
    textheader = TextHeader(header="sdk test header")
    binaryheader = BinaryHeader(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    client.seismics.create(
        external_id=extid,
        partition_identifier=3,
        seismic_store_id=6,
        text_header=textheader,
        binary_header=binaryheader,
    )
    seismic = client.seismics.get(external_id=extid)
    assert seismic.external_id == extid
    assert seismic.text_header.header == "sdk test header"


def test_edit_seismic():
    client = get_client()
    extid = str(uuid4())
    client.seismics.create(external_id=extid, partition_identifier=3, seismic_store_id=6)
    seismic = client.seismics.edit(external_id=extid, name="newname")
    assert seismic.name == "newname"


def test_list_seismics():
    client = get_client()
    assert len([x for x in client.seismics.list()]) > 0
