#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

import pandas as pd
import pytest
import json

from ..errors import EditError
from ..widget_state_container import WidgetStateContainer
from ..utils import empty_column_python_code


def test_create_widget_state_container():
    df = pd.DataFrame(data={'A': [123]})
    wsc = WidgetStateContainer(df)
    assert wsc.column_metatype == {'A': 'value'}
    assert wsc.column_evaluation_graph == {'A': set()}
    assert wsc.column_spreadsheet_code == {'A': ''}
    assert wsc.column_python_code == {'A': empty_column_python_code()}

# We assume only column A exists
CELL_EDIT_ERRORS = [
    ('=HI()', 'unsupported_function_error'),
    ('=UPPER(HI())', 'unsupported_function_error'),
    ('=UPPER(HI())', 'unsupported_function_error'),
    ('=C', 'no_column_error'),
    ('=C + D', 'no_column_error'),
    ('=ABCDEFG', 'no_column_error'),
    ('=UPPER(C)', 'no_column_error'),
    ('UPPER(A)', 'invalid_formula_error'),
    ('10', 'invalid_formula_error'),
    ('=B', 'circular_reference_error'),
    ('=UPPER(A, 100)', 'execution_error'),
    ('=UPPER(LOWER(A, 100))', 'execution_error')
]

@pytest.mark.parametrize("formula,error_type", CELL_EDIT_ERRORS)
def test_widget_state_container_cell_edit_errors(formula,error_type):
    df = pd.DataFrame(data={'A': [123]})
    wsc = WidgetStateContainer(df)
    wsc.add_column('B')
    with pytest.raises(EditError) as e_info:
        wsc.handle_edit_event({
            'event': 'edit_event',
            'type': 'cell_edit',
            'id': '123',
            'timestamp': '456',
            'address': 'B',
            'old_formula': '=0',
            'new_formula': formula
        })
    assert e_info.value.type_ == error_type

def test_column_exists_error():
    df = pd.DataFrame(data={'A': [123]})
    wsc = WidgetStateContainer(df)
    wsc.add_column('B')
    with pytest.raises(EditError) as e_info:
        wsc.add_column('B')
    assert e_info.value.type_ == 'column_exists_error'

def test_wrong_column_metatype():
    df = pd.DataFrame(data={'A': [123]})
    wsc = WidgetStateContainer(df)
    wsc.add_column('B')
    with pytest.raises(EditError) as e_info:
        wsc.handle_edit_event({
            'event': 'edit_event',
            'type': 'cell_edit',
            'id': '123',
            'timestamp': '456',
            'address': 'A',
            'old_formula': '=0',
            'new_formula': '=1'
        })
    assert e_info.value.type_ == 'wrong_column_metatype_error'