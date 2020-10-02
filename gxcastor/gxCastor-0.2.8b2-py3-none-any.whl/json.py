import json


def load(fl: str, converted_int: bool = True):
    """
    Load json from given file name

    :param fl: file name
    :param converted_int: if you want a int key, please set true
    :return:
    """
    def convert_int(d: dict) -> dict:
        r = dict()
        for k, v in d.items():
            if isinstance(v, dict):
                v = convert_int(v)
            try:
                k = int(k)
                r[k] = v
            except ValueError:
                r[k] = v
        return r
    _result = json.load(open(fl))

    if converted_int:
        if isinstance(_result, list):
            res = []
            for item in _result:
                if isinstance(item, dict):
                    res.append(convert_int(item))
                else:
                    res.append(item)
        else:
            return convert_int(_result)


def dump(obj, fn: str, ensure_ascii: bool = False, indent: str = None):
    return json.dump(obj, fp=open(fn, 'w'), ensure_ascii=ensure_ascii, indent=indent)
