from typing import List, Union, Optional

FeatureValue = Union[float, int, bool, str]
PredictionIdentifier = Union[int, str]


def is_valid_predict_param_list(data: Union[List[List[float]], List[List[FeatureValue]]]) -> bool:
    """Verify input data list is in valid input format.

    Args:
        data (Union[List[List[float]], List[List[FeatureValue]]]): Data list

    Returns:
        bool: True if the data list is in valid input format, False otherwise
    """
    if not isinstance(data, list):
        return False

    if len(data) == 0:
        return False

    if not all((isinstance(data_point, list) and len(data_point) > 0) for data_point in data):
        return False

    return True


def is_valid_ids(
    data: Optional[Union[List[PredictionIdentifier], List[int]]] = None,
    expected_length: Optional[int] = None,
) -> bool:
    """Verify input identifiers list is in valid input format.

    Args:
        data (Union[List[PredictionIdentifier], List[int]], optional): Input list of identifiers. Defaults to None.
        expected_length (int, optional): The expected length of the list. Defaults to None.

    Returns:
        bool: True if the identifiers list is in valid input format, False otherwise
    """
    if data is None:
        return False

    if not isinstance(data, list):
        return False

    if expected_length is not None and len(data) != expected_length:
        return False

    if not all((isinstance(data_point, int) or isinstance(data_point, str)) for data_point in data):
        return False

    return True
