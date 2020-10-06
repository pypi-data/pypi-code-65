#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.
import pandas as pd
import pytest

from ..example import df_to_json, MitoWidget, sheet
from ..utils import get_invalid_headers


def test_example_creation_blank():
    df = pd.DataFrame()
    sheet_json = df_to_json(df)
    w = MitoWidget(analysis_name='analysis', df=df)
    assert w.sheet_json == sheet_json


VALID_DATAFRAMES = [
    (pd.DataFrame()),
    (pd.DataFrame(data={'A': [1, 2, 3]})),
    (pd.DataFrame(data={'A0123': [1, 2, 3]})),
]
@pytest.mark.parametrize("df", VALID_DATAFRAMES)
def test_sheet_creates_valid_dataframe(df):
    mito = sheet(df)
    assert mito is not None

NON_STRING_HEADER_DATAFRAMES = [
    (pd.DataFrame(data={0: [1, 2, 3]})),
    (pd.DataFrame(data=[1, 2, 3])),
    (pd.DataFrame(data={'A': [1, 2, 3], 0: [1, 2, 3]})),
    (pd.DataFrame(data={'A': [1, 2, 3], '000': [1, 2, 3]}))
]
@pytest.mark.parametrize("df", NON_STRING_HEADER_DATAFRAMES)
def test_sheet_errors_during_non_string_headers(df):
    assert len(get_invalid_headers(df)) != 0
    with pytest.raises(Exception) as e_info:
        sheet(df)



