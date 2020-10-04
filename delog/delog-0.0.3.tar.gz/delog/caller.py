#region imports
import inspect

from delog.constants import (
    CALL_CONTEXT,
    CODE_PROVIDER,
    REPOSITORY_NAME,
    REPOSITORY_BASEPATH,
)
#endregion imports



#region module
def get_caller(
    call: dict = {},
):
    if not bool(call) and not CALL_CONTEXT:
        return None

    if not call:
        call = {}

    provider = call.get("code_provider", CODE_PROVIDER)
    repository_name = call.get("repository_name", REPOSITORY_NAME)
    repository_basepath = call.get("repository_basepath", REPOSITORY_BASEPATH)

    stack = inspect.stack()

    file = stack[2][1]
    line = int(stack[2][2])

    filepath = file.replace(repository_basepath, "", 1)

    caller = {
        "provider": provider,
        "repository": repository_name,
        "caller": {
            "file": filepath,
            "line": line,
            "column": 0,
        },
    }

    return caller
#endregion module
