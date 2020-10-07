import rich
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


def extract(src: dict, keys) -> list:
    """Extract contents of given keys"""
    result = list()
    for k in keys:
        result.append(src[k])
    return result


def dump_text(src: dict, filename: str, sep: str = '\t', keeplen: bool = False):
    """Dump dict to key sep value type text

    :param src: source dict
    :param filename: filename
    :param sep: char
    :param keeplen if true, the first line will be the length
    """
    fp = open(filename, 'w')
    length = len(src)
    rich.print(f"[Castor.mapping] Writing file to {filename}")
    if keeplen:
        print(length, file=fp)
    for k, v in src.items():
        print(f"{k}{sep}{v}", file=fp)
    fp.close()
    rich.print(f"[Castor.mapping] DONE.")

