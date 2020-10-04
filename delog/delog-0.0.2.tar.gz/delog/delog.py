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

    format: str = FORMAT,

    endpoint: str = ENDPOINT,
    token: str = TOKEN,

    project: str = PROJECT,
    space: str = SPACE,

    #  Log level:
    #  + FATAL: 6;
    #  + ERROR: 5;
    #  + WARN: 4;
    #  + INFO: 3;
    #  + DEBUG: 2;
    #  + TRACE: 1;
    level: int = delog_levels["info"],

    # Name of the method from where the log originates.
    method: str = "",

    # ID shared by multiple logs, used to identify a request spanning multiple services.
    shared_id: str = "",

    # If using the `shared_id`, the logs can be assigned an ordering number.
    # If not given, the logs will be ordered by time.
    #
    # The value should be greater than 0. If two or more logs have the same value,
    # they will be ordered by time.
    shared_order: int = -1,

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
        "call": call_context,
    };

    variables = {
        "input": {
            "format": format,

            "project": project,
            "space": space,

            "level": level,
            "method": method,
            "sharedID": shared_id,
            "sharedOrder": shared_order,
            "error": error_string,
            "extradata": extradata,

            "context": input_context,

            "text": text,

            "time": log_time,
        }
    }

    graphql_client.execute(
        query=RECORD,
        variables=variables,
    )
#endregion module
