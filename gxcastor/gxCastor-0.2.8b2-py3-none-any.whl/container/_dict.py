def merge(*args) -> dict:
    """
    Merge multi dicts

    :param args: multi dicts.
    :return: merge result
    """
    result = dict()
    for i in args:
        result = {**i, **result}
    return result


def swap_kv(src: dict):
    """
    Swap key and value and return new dict
    Args:
        src: Source dict

    Returns:
        Dict of <v:k>
    """
    return {v: k for k, v in src.items()}


def view(d: dict):
    """
    Censor the dict

    :param d: source dict
    :return: None
    """
    for k, v in d.items():
        print(f"Key: {k} / ValueType: {type(v)}")
