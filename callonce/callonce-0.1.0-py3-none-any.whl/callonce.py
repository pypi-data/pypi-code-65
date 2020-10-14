import functools
import inspect
from typing import Dict, NamedTuple, TypeVar


class Position(NamedTuple):
    filename: str
    lineno: int


_POSITIONS: Dict[Position, int] = {}
_TIMES = 'times'
T = TypeVar('T')


def callonce(func: T) -> T:

    @functools.wraps(func)  # type: ignore
    def wrapper(*args, **kwargs):
        frame_infos = inspect.stack()
        previous_frame_info = frame_infos[1]  # get called position
        position = Position(
            previous_frame_info.filename,
            previous_frame_info.lineno,
        )
        times: int = kwargs.pop(_TIMES, 1)  # call once by default

        if position not in _POSITIONS:
            _POSITIONS[position] = times - 1  # called once
            return func(*args, **kwargs)
        else:
            # check rest times
            if _POSITIONS[position] > 0:
                _POSITIONS[position] -= 1
                return func(*args, **kwargs)

    return wrapper  # type: ignore


@callonce
def printonce(*args, **kwargs):
    """
    Only print once or N times
    """
    print(*args, **kwargs)
