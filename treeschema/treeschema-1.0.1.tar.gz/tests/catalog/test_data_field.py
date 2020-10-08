import unittest

import mock
import pytest
import treeschema
from treeschema.catalog import DataField, TreeSchemaUser

from . import TEST_USER

class TestDataField(unittest.TestCase):

    data_field_inputs = {
        'created_ts': '2020-01-01 00:00:00',
        'description_markup': None,
        'description_raw': None,
        'data_type': 'string',
        'data_format': 'YYYY-MM-DD',
        'field_id': 1,
        'full_path_name': 'full.path.field.name',
        'name': str,
        'nullable': bool,
        'parent_path': None,
        'steward': TEST_USER,
        'tech_poc': TEST_USER,
        'type': 'table',
        'updated_ts': '2020-01-01 00:00:00'
    }

    def test_data_field_fields(self):
        assert sorted(list(self.data_field_inputs.keys())) == sorted(list(DataField.__FIELDS__.keys()))
    
    def test_create_data_field(self):
        DataField(self.data_field_inputs, data_store_id=1, data_schema_id=1)

    def test_schemas_access(self):
        df = DataField(self.data_field_inputs, data_store_id=1, data_schema_id=1)
        df._field_values_by_id is df.field_values

    def test_add_remove_field_values(self):
        df = DataField(self.data_field_inputs, data_store_id=1, data_schema_id=1)
        
        m = mock.Mock()
        m.id = 3
        m.field_value = 'field_value'

        assert df.field_values == {}
        assert df._field_values_by_id == {}
        assert df._field_values_by_value == {}

        df._add_field_value(m)

        assert 3 in df._field_values_by_id.keys()
        assert 'field_value' in df._field_values_by_value.keys()

        df._remove_field_value(3)

        assert df.field_values == {}
        assert df._field_values_by_id == {}
        assert df._field_values_by_value == {}
