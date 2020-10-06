#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
Exports the transpile function, which takes the backend widget
container and generates transpiled Python code.
"""

from .topological_sort import topological_sort_columns
from .sheet_functions import FUNCTIONS


def transpile(widget_state_container):

    # TODO: we have to handle the mito.sheet call, etc... in this code
    # We need to take all the existing code as input too!

    topological_sort = topological_sort_columns(widget_state_container.column_evaluation_graph)

    code = []
    for column in topological_sort:
        column_code = widget_state_container.column_python_code[column]['column_formula_changes']
        if column_code != '':
            code.append(
                widget_state_container.column_python_code[column]['column_formula_changes'].strip()
            )

    # Make sure we write a valid python function
    if len(code) == 0:
        code = ['# Edit the sheet to create the analysis!', 'pass']

    functions = ','.join(FUNCTIONS.keys())
    return {
        'imports': f'from mitosheet import {functions}',
        'code': code
    }