def check_type(obj: object, type_class, can_be_none=False):
    """
        Description: Utility method to check if v derives from typeClass

        Args:
            obj: Object instance to check
            type_class: Base class to check if v derives from
            can_be_none: True if allow obj to be None, default to False
        Return:
            True if v derives from type_class
    """

    if obj is None and not can_be_none:
        raise TypeError(f"{obj} cannot be None")

    if not can_be_none and not isinstance(obj, type_class):
        raise TypeError(f"{obj} must derived from {type_class}")


def clean_dict_recursive(o: dict):

    if (o is None or
            isinstance(o, str) or
            isinstance(o, int) or
            isinstance(o, float)):
        return o

    for k in list(o):  # .keys():
        # print("{} -- {} -- {}".format(k, o[k], type(o[k])))
        if type(o[k]) is dict:
            o[k] = clean_dict_recursive(o[k])

        if type(o[k]) is list:
            for idx in range(len(o[k])):
                o[k][idx] = clean_dict_recursive(o[k][idx])

        if (type(o[k]) is str and len(o[k]) == 0) or o[k] is None:
            del o[k]

    return o
