import re
from functools import reduce


def recursive_get(d: dict, keys, default=None):
    """Apply a get recursive to the dictionary.

    Args:
        d (dict): Dictionary.
        keys (str|list|tuple): If is a str keyA.keyB => [keyA, keyB].
        default (mixed): Not required.

    Returns:
        The return value.

    Examples:
        Run function.

        >>> recursive_get({'NUMBER': {'ONE': 1 }}, 'NUMBER.ONE')
        1
    """
    if isinstance(keys, str):
        keys = keys.split('.')
    result = reduce(lambda c, k: c.get(k, {}), keys, d)
    if default is not None and result == {}:
        return default
    return result


def kebab_case(string: str) -> str:
    """Convert string into kebab case or slug.

    Args:
        string (str): String to convert.

    Returns:
        str: String en kebab-case.

    Examples:
        Run function.

        >>> kebab_case('Hello world')
        'hello-world'
    """
    components = string.split(' ')
    string = '-'.join([str(elem) for elem in components])
    return string.lower()


def camel_to_snake(string: str):
    """Convert a string from camel case to snake case.

    Args:
        string (str): String to convert.

    Returns:
        str: String value.

    Examples:
        Run function.

        >>> camel_to_snake('HelloWorld')
        'hello_world'
    """
    string = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', string).lower()


def dict_keys_to_snake(d: dict) -> dict:
    """Convert the keys from camel case dictionary to snake case.

    Args:
        d (dict): dictionay to convert.

    Returns:
        dict: dictionary converted.

    Examples:
        Run function.

        >>> d = {'HelloWorld': 'message'}
        >>> dict_keys_to_snake(d)
        {'hello_world': 'message'}
    """
    return dict(
        zip([camel_to_snake(k) for k in d.keys()], list(d.values()))
    )


def setter_object_attrs(obj, keys: list, data: dict) -> None:
    """Assign the value of a dictionary to an object,
    according to the list of keys.
    Dictionary keys must be the same as the object

    Args:
        obj: Object to which the values will be assigned
        keys (list): key list to assign
        data (dict): Dictionary of origin of the values
    """
    for key in keys:
        if key in data:
            setattr(obj, key, data.get(key))
