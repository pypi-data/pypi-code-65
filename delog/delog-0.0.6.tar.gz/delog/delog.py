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

    # To be used if the `delog` is meant to be fired only in 'TESTING' `mode` (`context.mode`),
    # and the `mode` is set dinamically/from outside the enclosing function.
    tester: bool = False,

    # Name of the method from where the log originates.
    method: str = None,

    error = None,

    # Arbitrary data: a simple string, stringified JSON or deon.
    extradata: str = None,

    context: dict = {},
):
    if not context:
        context = {}

    if not endpoint:
        print("Delog Error :: An endpoint is required.")
        return

    if not token:
        print("Delog Error :: A token is required.")
        return

    if tester and context.get("mode") != 'TESTING':
        return

    if GROUND_LEVEL > level:
        return

    graphql_client = client(
        endpoint=endpoint,
        token=token,
    )

    call_context = get_caller(
        call=context.get("call"),
    )

    log_time = int(time.time())
    error_string = repr(error)
    input_context = {
        "mode": context.get("mode", "LOGGING"),
        "scenario": context.get("scenario", None),
        "suite": context.get("suite", None),
        "sharedID": context.get("shared_id", None),
        "sharedOrder": context.get("shared_order", None),
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
