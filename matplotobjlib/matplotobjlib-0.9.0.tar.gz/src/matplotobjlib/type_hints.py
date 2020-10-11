import datetime
from typing import Tuple, Union

Value = Union[int, float, datetime.date, datetime.datetime]
Range = Union[int, float, datetime.timedelta]
Color = Union[str, Tuple[float, float, float]]
