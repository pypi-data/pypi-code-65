"""
Pydebuggerconfig specific exceptions
"""

class PydebuggerconfigError(Exception):
    """
    Base class for all pydebuggerconfig specific exceptions
    """

    def __init__(self, msg=None, code=0):
        super(PydebuggerconfigError, self).__init__(msg)
        self.code = code

class PydebuggerconfigToolConnectionError(PydebuggerconfigError):
    """
    Signals a problem when connecting to a tool/debugger
    """

    def __init__(self, msg=None, code=0):
        super(PydebuggerconfigToolConnectionError, self).__init__(msg)
        self.code = code
