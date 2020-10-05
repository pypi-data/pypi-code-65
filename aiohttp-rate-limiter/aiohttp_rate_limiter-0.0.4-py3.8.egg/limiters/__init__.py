from enum import Enum

from .fixed_window import FixedWindow
from .sliding_log import SlidingLog


class methods(Enum):
    FIXED_WINDOW = FixedWindow
    SLIDING_LOG = SlidingLog
