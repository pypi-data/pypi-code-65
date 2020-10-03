from typing import Iterable, Optional


def array_query_param(inputs: Optional[Iterable[str]]) -> Optional[str]:
    if inputs:
        return ",".join(inputs)
    return None
