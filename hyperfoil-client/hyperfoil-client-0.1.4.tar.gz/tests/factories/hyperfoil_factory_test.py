from io import StringIO

import pytest

from hyperfoil.factories import HyperfoilFactory


@pytest.fixture(scope='function')
def file():
    file = StringIO()
    file.write("foo")
    file.seek(0)
    return file


def test_close_streams_with(file, client):
    with HyperfoilFactory(client) as factory:
        factory.benchmark({'name': 'test'}) \
            .file('test.txt', file)
    assert file.closed


def test_close_streams(file, client):
    factory = HyperfoilFactory(client)
    factory.benchmark({'name': 'test'}) \
        .file('test.txt', file)
    assert not file.closed
    factory.close()
    assert file.closed
