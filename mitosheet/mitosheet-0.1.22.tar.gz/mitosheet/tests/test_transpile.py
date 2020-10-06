#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

import pytest

from ..transpile import transpile
from mitosheet.tests.test_utils import create_mito_wrapper


def test_transpile_single_column():
    mito = create_mito_wrapper(['abc'])
    mito.set_formula('=A', 'B', add_column=True)
    code_container = transpile(mito.mito_widget.widget_state_container)
    assert code_container['code'] == ['df[\'B\'] = df[\'A\']']


def test_transpile_multiple_columns_no_relationship():
    mito = create_mito_wrapper(['abc'])
    mito.add_column('B')
    mito.add_column('C')
    code_container = transpile(mito.mito_widget.widget_state_container)
    assert 'df[\'B\'] = 0' in code_container['code']
    assert 'df[\'C\'] = 0' in code_container['code']


def test_transpile_multiple_columns_linear():
    mito = create_mito_wrapper(['abc'])
    mito.set_formula('=A', 'B', add_column=True)
    mito.set_formula('=B', 'C', add_column=True)
    code_container = transpile(mito.mito_widget.widget_state_container)
    assert code_container['code'] == ['df[\'B\'] = df[\'A\']', 'df[\'C\'] = df[\'B\']']

COLUMN_HEADERS = [
    ('ABC'),
    ('ABC_D'),
    ('ABC_DEF'),
    ('ABC_123'),
    ('ABC_HAHA_123'),
    ('ABC_HAHA-123'),
    ('---data---'),
    ('---da____ta---'),
    ('--'),
]
@pytest.mark.parametrize("column_header", COLUMN_HEADERS)
def test_transpile_column_headers_non_alphabet(column_header):
    mito = create_mito_wrapper(['abc'])
    mito.set_formula('=A', column_header, add_column=True)
    code_container = transpile(mito.mito_widget.widget_state_container)
    assert code_container['code'] == [f'df[\'{column_header}\'] = df[\'A\']']