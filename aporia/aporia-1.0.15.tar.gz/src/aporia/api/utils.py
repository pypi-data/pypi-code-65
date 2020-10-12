import collections.abc
from typing import Any, Iterable, List, Tuple, Union


def convert_scalar_to_iterable(data: Any) -> Iterable[Any]:
    """Converts a scalar to an iterable.

    Args:
        data (Any): Python or numpy scalar

    Raises:
        RuntimeError: If data cannot be converted

    Returns:
        Iterable[Any]: An iterable containing the input scalar
    """
    # Input is already iterable, do nothing
    if isinstance(data, collections.abc.Iterable):
        return data
    # Python scalar (using type instead of isinstance, because bool is a subclass of int)
    elif type(data) in (int, float):
        return [data]
    # Numpy scalar
    elif hasattr(data, "tolist"):
        return [data.tolist()]

    raise RuntimeError("Unsupported input scalar type {}".format(type(data)))


def convert_to_list(data: Any) -> List[Any]:
    """Converts an object to a list.

    Args:
        data (Any): A list, numpy array or pandas DataFrame

    Raises:
        RuntimeError: If data cannot be converted

    Returns:
        List[Any]: The original data, converted to a python list
    """
    # Data is already a list, do nothing
    if isinstance(data, list):
        return data
    # Numpy ndarray
    elif hasattr(data, "tolist"):
        return data.tolist()
    # Pandas DataFrame, Series, Index
    elif hasattr(data, "values") and hasattr(data.values, "tolist"):
        return data.values.tolist()

    raise RuntimeError("Unsupported input type {}".format(type(data)))


def convert_list_members_to_lists(data: List[Any]) -> List[List[Any]]:
    """Converts the members of a list to lists.

    Args:
        data (List[Any]): List whose members should be converted

    Returns:
        List[List[Any]]: A list containing the converted members of data.
    """
    # To avoid a high computational overhead, we assume all list members are of the same type
    if not isinstance(data[0], list):
        return [convert_to_list(member) for member in data]

    return data


def convert_iterable_to_list_of_specified_types(
    iterable: Iterable[Any], name: str, types: Union[type, Tuple[type, ...]]
) -> List[Any]:
    """Converts an iterable to a list, with type validation.

    Args:
        iterable (Iterable[Any]): Iterable to convert.
        name (str): Name of the iterable, for error messages.
        types (Union[type, Tuple[type]]): Expected types for elements in the iterable.

    Raises:
        RuntimeError: If the input is not an iterable.
        RuntimeError: If the elements of the iterable are not of the expected types.

    Returns:
        List[Any]: A list containing the elements from the iterable.
    """
    if not isinstance(iterable, collections.abc.Iterable):
        raise RuntimeError("Invalid input: {} must be iterable".format(name))

    if not all(isinstance(member, types) for member in iterable):
        raise RuntimeError(
            "Invalid input: {} must only contain elements of types {}".format(name, types)
        )

    return list(iterable)
