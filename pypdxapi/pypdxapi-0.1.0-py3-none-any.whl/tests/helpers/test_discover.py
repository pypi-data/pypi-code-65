"""The tests for the Paradox Module discover."""
from pypdxapi.helpers import discover


# def test_discover_modules():


def test_parse_response():
    data = 'paradoxip!type=a&ip=b&name=c'
    result = discover._parse_response(data)

    assert result == {'type': 'a', 'ip': 'b', 'name': 'c'}


def test_parse_modules():
    data = [
        {'type': 'a1', 'ip': 'b1', 'name': 'c1'},
        {'type': 'a2', 'ip': 'b2', 'name': 'c2'},
        {'type': 'a1', 'ip': 'b1', 'name': 'c1'},
    ]
    result = discover._parse_modules(data)

    assert len(result) == 2
