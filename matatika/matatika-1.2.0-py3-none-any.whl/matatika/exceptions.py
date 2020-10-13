'''exceptions module'''

import textwrap


class MatatikaException(Exception):
    """Class to handle custom Matatika exceptions"""

    def __init__(self, message=None):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class ContextNotSetError(Exception):
    """Class to raise an exception when a config context is not set"""

    def __init__(self, context, set_local_scope, set_global_scope):
        super().__init__()
        self.context = context
        self.set_local_scope = set_local_scope
        self.set_global_scope = set_global_scope

    def __str__(self):

        message = """{} context not set\nYou can provide {} context scoped to a single command with
         the '{}' option, or set a command-wide default using '{}' (see '{} --help')""" \
            .format(self.context[0].upper() + self.context[1:], self.context, self.set_local_scope,
                    self.set_global_scope, self.set_global_scope)
        return textwrap.dedent(message)


class WorkspaceContextNotSetError(ContextNotSetError):
    """Class to raise an exception when workspace context is not set"""

    def __init__(self):
        super().__init__("workspace", "--workspace / -w", "matatika use")


class EndpointURLContextNotSetError(ContextNotSetError):
    """Class to raise an exception when endpoint URL context is not set"""

    def __init__(self):
        super().__init__("endpoint URL", "--endpoint-url / -e", "matatika login")


class AuthContextNotSetError(ContextNotSetError):
    """Class to raise an exception when authentication token context is not set"""

    def __init__(self):
        super().__init__("authentication token", "--auth-token / -a", "matatika login")


class WorkspaceNotFoundError(Exception):
    """Class to raise an exception when a workspace is not found"""

    def __init__(self, workspace_id):
        super().__init__()
        self.workspace_id = workspace_id

    def __str__(self):
        message = """Workspace {} does not exist within the current authorisation context""" \
            .format(self.workspace_id)
        return textwrap.dedent(message)
