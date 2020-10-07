def as_list(val):
    """
    Converts val to a list of one if not already a list

    Does not support dict conversion, returns False
    """
    if type(val) == dict:
        return False

    if type(val) != list:
        return [val]

    return val
