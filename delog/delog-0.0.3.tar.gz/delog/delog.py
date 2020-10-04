#region imports
import time

from delog.graphql import (
    RECORD,
    client,
)

from delog.constants import (
    GROUND_LEVEL,
    FORMAT,
    ENDPOINT,
    TOKEN,
    PROJECT,
    SPACE,
    delog_levels,
)

from delog.caller import (
    get_caller,
)
#endregion imports



#region module
def delog(
    text: str,

    #  Log level:
    #  + FATAL: 6;
    #  + ERROR: 5;
    #  + WARN: 4;
    #  + INFO: 3;
    #  + DEBUG: 2;
    #  + TRACE: 1;
    level: int = delog_levels["info"],

    endpoint: str = ENDPOINT,
    token: str = TOKEN,

    format: str = FORMAT,

    project: str = PROJECT,
    space: str = SPACE,

    # Name of the method from where the log originates.
    method: str = "",

    error = "",

    # Arbitrary data: a simple string, stringified JSON or deon.
    extradata: str = "",

    context: dict = {},
):
    if not endpoint:
        print("Delog Error :: An endpoint is required.")
        return

    if not token:
        print("Delog Error :: A token is required.")
        return

    if GROUND_LEVEL > level:
        return

    graphql_client = client(
        endpoint=endpoint,
        token=token,
    )

    if not context:
        context = {}

    call_context = get_caller(
        call=context.get("call"),
    )

    log_time = int(time.time())
    error_string = repr(error)
    input_context = {
        "mode": context.get("mode", "LOGGING"),
        "scenario": context.get("scenario", ""),
        "suite": context.get("suite", ""),
        "shared_id": context.get("shared_id", ""),
        "shared_order": context.get("shared_order", ""),
        "call": call_context,
    };

    variables = {
        "input": {
            "text": text,
            "time": log_time,
            "level": level,

            "project": project,
            "space": space,

            "format": format,

            "method": method,
            "error": error_string,
            "extradata": extradata,
            "context": input_context,
        }
    }

    graphql_client.execute(
        query=RECORD,
        variables=variables,
    )
#endregion module
