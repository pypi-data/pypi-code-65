#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
Contains helpful utility functions
"""

import pandas as pd

from string import ascii_letters, digits

def empty_column_python_code():
    """
    Helper functions for creating an empty entry
    for column_python_code - which can then be filled 
    in later (or left empty for an unedited column)
    """
    return {
        'column_name_change': None,
        'column_type_change': None,
        'column_value_changes': {},
        'column_formula_changes': ''
    }

def code_container(code):
    """
    Returns the code block with
    # MITO CODE START
    and
    # MITO CODE END

    SAME FUNCTION IN PLUGIN.ts
    """

    return f'# MITO CODE START\n\n{code}\n\n# MITO CODE END'


def get_invalid_headers(df: pd.DataFrame):
    """
    Given a dataframe, returns a list of all the invalid headers this list has. 

    A header is valid if:
    1. It is a string
    2. It only contains alphanumber characters, or - or _
    3. It has at least one non-numeric character.

    Valid examples: A, ABC, 012B, 213_bac, 123-123
    Invalid examples: 123, 123!!!, ABC!

    This is a result of not being able to distingush column headers from constants
    otherwise, and would not be necessary if we had a column identifier!
    """
    valid_columns = [
        header for header in df.columns.tolist()
        if isinstance(header, str) and ( # Condition (1)
            set(header).issubset(set(ascii_letters).union(set(digits)).union(set(['-', '_']))) and # Condition (2)
            not header.isdigit() # Condition (3)
        )
    ]

    return [
        header for header in df.columns.tolist()
        if header not in valid_columns
    ]


