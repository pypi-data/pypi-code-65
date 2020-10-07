#region imports
import inspect

from delog.constants import (
    CALL_CONTEXT,
    REPOSITORY_PROVIDER,
    REPOSITORY_NAME,
    REPOSITORY_BRANCH,
    REPOSITORY_COMMIT,
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

    call_repository = call.get("repository", {})

    if not call_repository:
        return None

    provider = call_repository.get("provider", REPOSITORY_PROVIDER)
    repository_name = call_repository.get("name", REPOSITORY_NAME)
    repository_branch = call_repository.get("branch", REPOSITORY_BRANCH)
    repository_commit = call_repository.get("commit", REPOSITORY_COMMIT)
    repository_basepath = call_repository.get("basepath", REPOSITORY_BASEPATH)

    stack = inspect.stack()

    file = stack[2][1]
    line = int(stack[2][2])

    filepath = file.replace(repository_basepath, "", 1)

    caller = {
        "repository": {
            "provider": provider,
            "name": repository_name,
            "branch": repository_branch,
            "commit": repository_commit,
            "basePath": repository_basepath,
        },
        "caller": {
            "file": filepath,
            "line": line,
            "column": 0,
        },
    }

    return caller
#endregion module
