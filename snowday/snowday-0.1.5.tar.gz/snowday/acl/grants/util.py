import re


def get_priv_from_cls(class_name: str, start_pos: int, stop_pos: int):
    """A helper function for turning CamelCase class names
    into snake_case names, splitting said name on the underscore,
    and getting the appropriate grant privilege.
    """
    s = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", class_name)
    camelcase_name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s).lower()
    return " ".join(camelcase_name.split("_")[start_pos:stop_pos])


def get_privilege(class_name: str):
    """A helper function for getting the name of a
    class's privilege, based on the assumption that
    the privilege will be included in the name.
    ie:
        AllGrant -> "all"
        SelectGrant -> "select"
    """
    return get_priv_from_cls(class_name, 0, -1)


def get_future_privilege(class_name: str):
    """A helper function for getting the name of a
    class's future privilege, based on the assumption
    that the privilege will be included in the name
    and sandwiched between "future" and "grant".
    ie:
        FutureApplyGrant -> "apply"
        FutureAllGrant -> "all"
    """
    return get_priv_from_cls(class_name, 1, -1)
