#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
Exports an error box that can be used to pass the errors
we need. 

Further exports helper functions for creating errors
of different flavors. We wrap these functions in the same
EditError box to avoid creating too many new classes!

See more about why we use errors here: 
https://stackoverflow.com/questions/16138232/is-it-a-good-practice-to-use-try-except-else-in-python
"""
from typing import Set

class CreationError(Exception):
    """
    An error that occurs during a mito.sheet call, on creation
    of the mito widget. 
    """
    def __init__(self, type_, header, to_fix):
        """
        Creates a creation error. 

        type_: the error id string.
        header: the header of the error message to be displayed.
        to_fix: instructions on how to handle or fix the error.
        """
        self.type_ = type_ # we have an _ to avoid overwriting the build in type
        self.header = header
        self.to_fix = to_fix

class EditError(Exception):
    """
    An error that occurs during the processing of an editing event.
    """
    def __init__(self, type_, header, to_fix):
        """
        Creates a creation error. 

        type_: a string that is the error type. 
        header: the header of the error message to be displayed.
        to_fix: instructions on how to handle or fix the error.
        """
        self.type_ = type_ # we have an _ to avoid overwriting the build in type
        self.header = header
        self.to_fix = to_fix

def make_no_column_error(column_headers: Set[str]):
    """
    Helper function for creating a no_column_error.

    Occurs when a user edits a formula with a reference to a column that does not exist.
    """
    if len(column_headers) == 1:
        to_fix = f'Sorry, there is no column with the name {next(iter(column_headers))}. Did you type it correctly?'
    else:
        to_fix = f'Sorry, there are no column with the names {", ".join(column_headers)}. Did you type them correctly?'

    return EditError(
        'no_column_error', 
        'No Column Exists',
        to_fix
    )

def make_column_exists_error(column_header: str):
    """
    Helper function for creating a column_exists_error.

    Occurs when:
    -  the user adds a column that already exists in the dataframe.
    """
    return EditError(
        'column_exists_error', 
        'Column Already Exists',
        f'Sorry, a column already exists with the name {column_header}. Try picking a different name!'
    )

def make_invalid_formula_error(formula: str):
    """
    Helper function for creating a invalid_formula_error.

    Occurs when:
    -  the user edits a cell to an expression that cannot be parsed.
    """
    return EditError(
        'invalid_formula_error',
        'Invalid Formula',
        f'Sorry, the formula \'{formula}\' is invalid. Did you type it correctly?'
    )

def make_circular_reference_error():
    """
    Helper function for creating a circular_reference_error.

    Occurs when:
    -  an edit introduces a circular reference.
    """
    return EditError(
        'circular_reference_error',
        'Circular Reference',
        f'Sorry, circular references are not supported currently.'
    )

def make_wrong_column_metatype_error(column_header: str):
    """
    Helper function for creating a wrong_column_metatype_error.

    Occurs when:
    -  a user edits a column to a formula when it is not a formula type column.
    """
    return EditError(
        'wrong_column_metatype_error',
        'Wrong Column Type',
        f'Sorry, the column {column_header} is a data column. We don\'t currently support changing it to a formula.'
    )

def make_execution_error():
    """
    Helper function for creating a execution_error.

    Occurs when:
    -  running an existing analysis on the parameters passed to the mito sheet throw an error.
    """
    # TODO: this to_fix message is _just terrible_
    return EditError(
        'execution_error',
        'Execution Error',
        f'Sorry, there was an error during executing this code.'
    )

def make_unsupported_function_error(functions: Set[str]):
    """
    Helper function for creating a unsupported_function_error.

    Occurs when:
    -  the user's new formula containing a function that is not supported by mito.
    """
    # TODO: we could fix up this to_fix, lol.
    if len(functions) == 1:
        to_fix = f'Sorry, mito does not currently support the function {next(iter(functions))}. To request this function, shoot us an email @ aaron@sagacollab.com!'
    else:
        to_fix = f'Sorry, mito does not currently support the functions {", ".join(functions)}. To request these functions, shoot us an email @ aaron@sagacollab.com!'

    return EditError(
        'unsupported_function_error',
        'Unsupported Function',
        to_fix
    )

def make_invalid_column_reference_error():
    """
    Helper function for creating a invalid_column_reference_error.

    Occurs when:
    -  the user makes a reference to A1 instead of A.
    """
    return EditError(
        'invalid_column_reference_error',
        'Invalid Column Reference',
        'Saga only supports a single formula per column. Instead of \'A1\', try referencing just \'A\'.'
    )