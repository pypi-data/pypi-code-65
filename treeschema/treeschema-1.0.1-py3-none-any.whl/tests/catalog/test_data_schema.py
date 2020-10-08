import unittest

import mock
import pytest
import treeschema
from treeschema.catalog import DataSchema, TreeSchemaUser

from . import TEST_USER

class TestDataSchema(unittest.TestCase):

    data_schema_inputs = {
        'created_ts': '2020-01-01 00:00:00',
        'data_schema_id': 1,
        'description_markup': None,
        'description_raw': None,
        'name': 'Test DS',
        'schema_loc': None,
        'type': 'table',
        'steward': TEST_USER,
        'tech_poc': TEST_USER,
        'updated_ts': '2020-01-01 00:00:00'
    }

    def test_data_schema_fields(self):
        assert sorted(list(self.data_schema_inputs)) == sorted(list(DataSchema.__FIELDS__.keys()))
    
    def test_create_data_schema(self):
        DataSchema(self.data_schema_inputs, data_store_id=1)

    def test_schemas_access(self):
        ds = DataSchema(self.data_schema_inputs, data_store_id=1)
        ds._fields_by_id is ds.fields

    def test_add_remove_schemas(self):
        ds = DataSchema(self.data_schema_inputs, data_store_id=1)
        
        m = mock.Mock()
        m.id = 3
        m.name = 'field_name'

        assert ds.fields == {}
        assert ds._fields_by_id == {}
        assert ds._fields_by_name == {}

        ds._add_data_field(m)

        assert 3 in ds._fields_by_id.keys()
        assert 'field_name' in ds._fields_by_name.keys()

        ds._remove_data_field(3)

        assert ds.fields == {}
        assert ds._fields_by_id == {}
        assert ds._fields_by_name == {}
