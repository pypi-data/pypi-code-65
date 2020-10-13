def dict_extract(dic, fields, *args):
    from .zfunction import list_or_args
    fields = list_or_args(fields, args)
    new_dic = {}
    for k, v in dic.items():
        if k in fields:
            new_dic[k] = v
    return new_dic


def dict_recursive_get(dic, key, default_value=None):
    d = dic
    for k in key.split("."):
        if not d:
            return default_value
        if not isinstance(d, dict):
            return default_value
        d = d.get(k)
    return d if d else default_value
