from datetime import datetime
from typing import List
from unittest.mock import Mock, PropertyMock

import pytest
from freezegun import freeze_time
from moto import mock_s3

from dli.aws import create_refreshing_session, _meets_partition_params, \
    match_partitions

path = 'prefix/as_of_date=2020-01-23/a=2/b=4/c=6/file.ext'


@mock_s3
def test_session_refreshes():
    dli_client = Mock()
    # This is how you give an attribute a side effect
    auth_key = PropertyMock(return_value='abc')
    type(dli_client.session).auth_key = auth_key 

    dli_client.session.token_expires_on = datetime(2000, 1, 2, 0, 0, 0)
    session = create_refreshing_session(dli_client.session).resource('s3')

    with freeze_time(datetime(2000, 1, 1, 0, 0, 0)):
        assert auth_key.call_count == 1
        session.meta.client.list_buckets()
        assert auth_key.call_count == 1
        session.meta.client.list_buckets()
        assert auth_key.call_count == 1

    with freeze_time(datetime(2000, 1, 3, 0, 0, 0)):
        dli_client.session.token_expires_on = datetime(2000, 1, 4, 0, 0, 0)
        assert auth_key.call_count == 1
        session.meta.client.list_buckets()
        assert auth_key.call_count == 2
        session.meta.client.list_buckets()
        assert auth_key.call_count == 2


@pytest.mark.parametrize(
    'partition_query',
    [
        [
            {'partition': 'a', 'operator': '>', 'value': '3'},
        ],
        [
            {'partition': 'c', 'operator': "<", 'value': '5'},
        ],
        [
            {'partition': 'as_of_date', 'operator': '<',
             'value': '2020-01-23'},
        ],
        [
            {'partition': 'as_of_date', 'operator': '>',
             'value': '2020-01-23'},
        ],
    ],
)
def test_fails_partition_params(partition_query: List):
    assert not _meets_partition_params(path, partition_query)


@pytest.mark.parametrize(
    'partition_query', [
        [{'partition': 'as_of_date', 'operator': '=',
          'value': '2020-01-23'}],
    ],
)
def test_meets_date_supported_partition_params(partition_query: List):
    assert _meets_partition_params(path, partition_query)


@pytest.mark.parametrize(
    'partition_query', [
        [
            {'partition': 'a', 'operator': '<', 'value': '3'},
        ],
        [
            {'partition': 'b', 'operator': '=', 'value': '4'},
        ],
        [
            {'partition': 'c', 'operator': ">", 'value': '5'},
        ],
        [
            {'partition': 'd', 'operator': "!=", 'value': '5'},
        ],
        [
            {'partition': 'as_of_date', 'operator': '=',
             'value': '2020-01-23'},
        ],
        # Combination of all filters.
        [
            {'partition': 'a', 'operator': '<', 'value': '3'},
            {'partition': 'b', 'operator': '=', 'value': '4'},
            {'partition': 'c', 'operator': ">", 'value': '5'},
            {'partition': 'as_of_date', 'operator': '=',
             'value': '2020-01-23'},
        ],
    ],
)
def test_meets_partition_params(
        partition_query: List
):
    assert _meets_partition_params(path, partition_query)


@pytest.mark.parametrize(
    'path,partitions', [
        [
            path, ['a<3']
        ],
        [
            path, ['b=4']
        ],
        [
            path, ['c>5']
        ],
        [
            path, ['d!=5']
        ],
        [
            path, ['as_of_date=2020-01-23']
        ],
        # Combination of all filters.
        [
            path, ['a<3', 'b=4', 'c>5', 'd!=5', 'as_of_date=2020-01-23']
        ],
        [
            'prefix/export_region=NorthAmerica/file.ext',
            ['export_region=NorthAmerica']
        ],
        [
            'prefix/export_region=North_America/file.ext',
            ['export_region=North_America']
        ],
        [
            'prefix/export_region=North America/file.ext',
            ['export_region=North America']
        ],
        [
            'prefix/export region=North America/file.ext',
            ['export region=North America']
        ],
    ],
)
def test_match_partitions(path: str, partitions: List[str]):
    assert match_partitions(path, partitions)


def test_raises_error_with_malformed_date():
    partition_query = [{
        'partition': 'as_of_date',
        'operator': '=',
        'value': '202-01-23'
    }]

    with pytest.raises(ValueError):
        _meets_partition_params(path, partition_query)


def test_false_when_as_of_date_is_invalid():
    partition_query = [{
        'partition': 'as_of_date',
        'operator': '=',
        'value': '2020-01-23'
    }]

    invalid_path = 'b=4/c=6/as_of_date=ABC/file.ext'

    assert not _meets_partition_params(invalid_path, partition_query)
