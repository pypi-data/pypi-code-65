from typing import NamedTuple, Union


def tp_to_dict(n: Union[NamedTuple, tuple]) -> dict:
    """
    Convert Namedtuple to dict
    Args:
        n:

    Returns: dict type

    """
    result = dict()
    for k in n._fields:
        val = getattr(n, k)
        if isinstance(val, tuple):
            result[f"{k}"] = tp_to_dict(val)
        else:
            result[f"{k}"] = val
    return result


def dict_to_namedtuple(d: dict, np):
    kwargs = dict()
    annos = np.__annotations__
    for k, val in d.items():
        if isinstance(val, dict) and issubclass(annos[k], tuple):
            kwargs[k] = dict_to_namedtuple(val, annos[k])
        else:
            kwargs[k] = val
    return np(**kwargs)
