from inteliquent import InteliquentClient


def test_initilizing_client():
    client = InteliquentClient()
    assert type(client) == InteliquentClient
