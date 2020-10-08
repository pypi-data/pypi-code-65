import unittest

import mock
import pytest
import treeschema
from treeschema.catalog import DataStore, TreeSchemaUser

from . import TEST_USER

class TestDataStore(unittest.TestCase):

    data_store_inputs = {
        'created_ts': '2020-01-01 00:00:00',
        'data_store_id': 1,
        'description_markup': None,
        'description_raw': None,
        'details': {},
        'name': 'Test DS',
        'other_type': None,
        'steward': TEST_USER,
        'tech_poc': TEST_USER,
        'type': 'kafka',
        'updated_ts': '2020-01-01 00:00:00'
    }

    def test_data_store_fields(self):
        assert sorted(list(self.data_store_inputs)) == sorted(list(DataStore.__FIELDS__.keys()))
    
    def test_create_data_store(self):
        DataStore(self.data_store_inputs)

    def test_schemas_access(self):
        ds = DataStore(self.data_store_inputs)
        ds._schemas_by_id is ds.schemas

    def test_add_remove_schemas(self):
        ds = DataStore(self.data_store_inputs)
        
        m = mock.Mock()
        m.id = 3
        m.name = 'schema_name'

        assert ds.schemas == {}
        assert ds._schemas_by_id == {}
        assert ds._schemas_by_name == {}

        ds._add_data_schema(m)

        assert 3 in ds._schemas_by_id.keys()
        assert 'schema_name' in ds._schemas_by_name.keys()

        ds._remove_data_schema(3)

        assert ds.schemas == {}
        assert ds._schemas_by_id == {}
        assert ds._schemas_by_name == {}
