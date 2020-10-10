from datetime import datetime
from typing import Any


def json_converter(o: Any) -> str or None:
    """
    Simple converter for json serialization
    :param o: the object to serialize
    :return: serialized value or None
    """
    if isinstance(o, datetime):
        return o.isoformat()
