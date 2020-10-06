#!/usr/bin/env python

__all__ = ['FieldValidationError', 'NodeError']

class FieldValidationError(Exception):
    '''Base error for field validation. Type or content constraint not met.'''

class NodeError(Exception):
    '''Base error for the nodes in this module.'''

    def __init__(self, message, err_value="", *args):
        self.message = message
        self.err_value = err_value
        super().__init__(message, err_value, *args)
