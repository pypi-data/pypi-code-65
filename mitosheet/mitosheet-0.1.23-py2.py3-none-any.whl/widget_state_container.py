#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

from typing import Dict, Union
import pandas as pd
import json

from mitosheet.sheet_functions import FUNCTIONS
from mitosheet.topological_sort import creates_circularity, topological_sort_columns
from mitosheet.evaluate import parse_formula
from mitosheet.utils import empty_column_python_code
from mitosheet.errors import (
    make_column_exists_error,
    make_no_column_error,
    make_wrong_column_metatype_error,
    make_unsupported_function_error,
    make_circular_reference_error,
    make_execution_error
)


class WidgetStateContainer():
    """
    Holds all private widget state used by the evaluator and transpiler. 

    Is responsible for updating this state and maintaining correctness, 
    even in the case of invalid updates.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.column_metatype = {key: 'value' for key in self.df.keys()}
        self.column_spreadsheet_code = {key: '' for key in self.df.keys()}
        self.column_python_code = {
            key: empty_column_python_code() for key in self.df.keys()
        }
        self.column_evaluation_graph = {key: set() for key in self.df.keys()}

    def handle_edit_event(self, edit_event):
        """
        Updates the widget state with the edit_event, and errors
        if the event is invalid. 
        """
        if edit_event['type'] == 'cell_edit':
            column_header = edit_event['address']
            old_formula = edit_event['old_formula']
            new_formula = edit_event['new_formula']
            self.set_column_formula(column_header, old_formula, new_formula)
        elif edit_event['type'] == 'add_column':
            column_header = edit_event['column_header']
            self.add_column(column_header)   
        else:
            raise Exception(f'{edit_event} is not an edit event!')

    def handle_sheet_update_event(self, sheet_update_event):
        """
        Updates the widget state with the sheet_update_event, and errors
        if the event is invalid. 
        """
        if sheet_update_event['type'] == 'column_spreadsheet_code':
            column_spreadsheet_code = json.loads(sheet_update_event['column_spreadsheet_code'])
            self.set_column_spreadsheet_code(column_spreadsheet_code)
        else:
            raise Exception(f'{sheet_update_event} is not a sheet update event!')

    def set_column_spreadsheet_code(self, column_spreadsheet_code: Dict[str, str]):
        """
        If an analysis has already been run, then there are existing spreadsheet
        formulas in columns that are not known at the creation of this object.

        Thus, we update them after the fact!

        NOTE: we don't re-evaluate the JSON, as we assume it is matched up with the DF.
        TODO: this might be a bug, if you change the df before rerunning the analysis...
        """

        for column_header, spreadsheet_code in column_spreadsheet_code.items():
            print("updating", column_header, spreadsheet_code)
            # Skip columns without a formula!
            if spreadsheet_code == '':
                continue

            self.column_metatype[column_header] = 'formula'
            # TODO: old formula is weird here; should actually be None?
            self.set_column_formula(
                column_header, 
                None, 
                spreadsheet_code,
                evaluate=False
            )

    def add_column(self, column_header: str):
        """
        Adds a column. Errors if the column already exists
        """
        if column_header in self.column_metatype:
            raise make_column_exists_error(column_header)

        # Update the state variables
        self.column_metatype[column_header] = 'formula'
        self.column_spreadsheet_code[column_header] = '=0'
        self.column_python_code[column_header] = empty_column_python_code()
        self.column_python_code[column_header]['column_formula_changes'] = f'df[\'{column_header}\'] = 0'
        self.column_evaluation_graph[column_header] = set()

        # Update the dataframe; this cannot cause an error!
        self.df[column_header] = 0

    def set_column_formula(
            self, 
            column_header: str, 
            old_formula: Union[str, None], 
            new_formula: str,
            evaluate: bool = True
        ):
        """
        Sets the column with column_header to have the new_formula, and 
        updates the dataframe as a result.

        Errors if:
        - The given column_header is not a column. 
        - The new_formula introduces a circular reference.
        - The new_formula causes an execution error in any way. 

        In the case of an error, this function rolls back all variables
        variables to their state at the start of this function.
        """

        # TODO: we need to make a column does not exist error, for this edit!

        # First, we check the column_metatype, and make sure it's a formula
        if self.column_metatype[column_header] != 'formula':
            raise make_wrong_column_metatype_error(column_header)

        # If nothings changed, there's no work to do
        if (old_formula == new_formula):
            return

        # Then we try and parse the formula
        new_python_code, new_functions, new_dependencies = parse_formula(new_formula, column_header)

        # We check that the formula doesn't reference any columns that don't exist
        missing_columns = new_dependencies.difference(self.column_metatype.keys())
        if any(missing_columns):
            raise make_no_column_error(missing_columns)

        # The formula can only reference known formulas
        missing_functions = new_functions.difference(set(FUNCTIONS.keys()))
        if any(missing_functions):
            raise make_unsupported_function_error(missing_functions)

        # Then, we get the list of old column dependencies and new dependencies
        # so that we can update the graph
        old_python_code, old_functions, old_dependencies = parse_formula(old_formula, column_header)

        # Before changing any variables, we make sure this edit didn't
        # introduct any circularity
        circularity = creates_circularity(
            self.column_evaluation_graph, 
            column_header,
            old_dependencies,
            new_dependencies
        )
        if circularity:
            raise make_circular_reference_error()

        # Update the variables based on this new formula
        self.column_spreadsheet_code[column_header] = new_formula
        self.column_python_code[column_header]['column_formula_changes'] = new_python_code

        # Update the column dependency graph
        for old_dependency in old_dependencies:
            self.column_evaluation_graph[old_dependency].remove(column_header)
        for new_dependency in new_dependencies:
            self.column_evaluation_graph[new_dependency].add(column_header)

        # If we don't evaluate, we just return here...
        # TODO: maybe we should break the above out into it's own function?
        if not evaluate:
            return

        # Then we update the dataframe, first by executing on a fake dataframe
        df_copy = self.df.copy()
        try:
            # We execute on the copy first to see if there will be errors
            self._execute(df_copy)
        except Exception as e:
            # If there is an error during executing, we roll back all the changes we made
            self.column_spreadsheet_code[column_header] = old_formula
            self.column_python_code[column_header]['column_formula_changes'] = old_python_code

            # Update the column dependency graph back to what it was.
            for new_dependency in new_dependencies:
                self.column_evaluation_graph[new_dependency].remove(column_header)
            for old_dependency in old_dependencies:
                self.column_evaluation_graph[old_dependency].add(column_header)
            
            # And then we bubble the error up!
            # TODO: case on what sort of error it was
            raise make_execution_error()
            
        # However, if there was no error in execution on the copy, we can execute on 
        # the real dataframe!
        self._execute(self.df)

    def _execute(self, df):
        """
        Executes the given state variables for  
        """
        topological_sort = topological_sort_columns(self.column_evaluation_graph)

        for column_header in topological_sort:
            # Exec the code, where the df is the original dataframe
            # See explination here: https://www.tutorialspoint.com/exec-in-python
            exec(
                self.column_python_code[column_header]['column_formula_changes'],
                {'df': df}, 
                FUNCTIONS
            )










