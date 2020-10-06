#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
This file contains helpful functions and classes for testing operations.
"""

import pandas as pd

from mitosheet.example import sheet, MitoWidget

class MitoWidgetTestWrapper:
    """
    This class adds some simple wrapper functions onto the MitoWidget 
    to make interacting with it easier for testing purposes.

    It allows you to create just the backend piece of Mito, create columns,
    set formulas, and get values to check the result.
    """

    def __init__(self, mito_widget: MitoWidget):
        self.mito_widget = mito_widget

    def add_column(self, column_header: str):
        """
        Adds a column.
        """
        self.mito_widget.receive_message(self.mito_widget, {
            'event': 'edit_event',
            'type': 'add_column',
            'id': '123',
            'timestamp': '456',
            'column_header': column_header
        })
    
    def set_formula(self, formula: str, column_header: str, add_column=False):
        """
        Sets the given column to have formula, and optionally
        adds the column if it does not already exist.
        """
        if add_column:
            self.add_column(column_header)
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'edit_event',
                'type': 'cell_edit',
                'id': '123',
                'timestamp': '456',
                'address': column_header,
                'new_formula': formula,
            }
        )

    def get_formula(self, column_header: str):
        """
        Gets the formula for a given column. Returns an empty
        string if nothing exists.
        """
        if column_header not in self.mito_widget.column_spreadsheet_code:
            return ''
        return self.mito_widget.column_spreadsheet_code[column_header]

    def get_value(self, column_header: str, row: int):
        """
        Returns a value in a given dataframe at the a given
        index in a column. NOTE: the row is 1 indexed!

        Errors if the value does not exist
        """
        return self.mito_widget.df.at[row - 1, column_header]

    def get_column(self, column_header: str, as_list: bool):
        """
        Returns a series object of the given column, or a list if
        as_list is True. 

        Errors if the column does not exist. 
        """
        if as_list:
            return self.mito_widget.df[column_header].tolist()
        return self.mito_widget.df[column_header]

def create_mito_wrapper(column_A_data) -> MitoWidgetTestWrapper:
    """
    Returns a MitoWidgetTestWrapper instance wrapped around a MitoWidget
    that contains just a column A, containing column_A_data
    """
    df = pd.DataFrame(data={'A': column_A_data})
    mito_widget = sheet(df)
    return MitoWidgetTestWrapper(mito_widget)