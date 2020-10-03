import copy
from re import finditer


ATTRS_TO_EXCLUDE = [
    "database",
    "schema",
    "name",
    "or_replace",
    "if_not_exists",
    "transient",
]


def get_resource_type(obj):
    matches = finditer(
        ".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)", obj.__class__.__name__
    )
    case_delineated_words = [m.group(0).lower() for m in matches]
    return " ".join(case_delineated_words)


def settings_str_from(obj, exclude_attrs=ATTRS_TO_EXCLUDE):
    d = copy.deepcopy(obj.__dict__)
    settings = []
    for k, v in d.items():
        if k not in exclude_attrs and k[0] != "_":
            if v:
                if isinstance(v, str):
                    settings.append(f"{k}='{v}'")
                elif isinstance(v, list):
                    vals_str = ", ".join([f"'{val}'" for val in v])
                    settings.append(f"{k}=({vals_str})")
                elif isinstance(v, (bool, int)):
                    settings.append(f"{k}={v}")
                else:
                    settings.append(f"{k}='{v.name.upper()}'")
    return " ".join(settings)
