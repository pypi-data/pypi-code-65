from math import nan
import secrets

from . import data_type as dt


def generate_integer(num_of_bytes):
    """Generates a cryptographically secure, random integer.

    :param num_of_bytes: number of bytes
    :type num_of_bytes: int
    :return: random integer
    :rtype: number
    """
    if num_of_bytes <= 0:
        raise ValueError("number of digits must be positive")

    return secrets.randbits(num_of_bytes * 8)


def generate_float(num_of_bytes):
    """Generates a cryptographically secure, random floating point.

    :param num_of_bytes: number of decimal places
    :type num_of_bytes: int
    :return: random float
    :rtype: float
    """
    if num_of_bytes <= 0:
        raise ValueError("number of decimal places must be positive")
    exclusive_upper_bound = 2 ** (num_of_bytes * 8)

    return secrets.randbelow(exclusive_upper_bound) / exclusive_upper_bound


def generate_token(num_of_bytes):
    """Generates a cryptographically secure, random (URL safe) token.

    :param num_of_bytes: number of bytes
    :type num_of_bytes: int
    :return: random token
    :rtype: str
    """

    if num_of_bytes <= 0:
        raise ValueError("number of bytes must be positive")

    return secrets.token_urlsafe(num_of_bytes)


def generator_factory(data_type):
    """Factory function, returns the result of correct value generator.

    :param data_type: data type of value
    :type data_type: str
    :raises ValueError: Data type must be one of: str, int, float.
    :return: generator function
    :rtype: function
    """
    if data_type == dt.DataType.token.value:
        return generate_token
    elif data_type == dt.DataType.floating_point.value:
        return generate_float
    elif data_type == dt.DataType.integer.value:
        return generate_integer
    else:
        raise ValueError(
            "data type must be one of: str, int, float"
        )


def generate_value(all_value_types_sorted, data_types, byte_size):
    """Generic value generator.

    :param all_value_types_sorted: list of tuples containing value types sorted by frequency
    :type all_value_types_sorted: List[Tuple]
    :param data_types: list of the desired sata types
    :type data_types: List[String]
    :param byte_size: number of bytes
    :type byte_size: int
    :raises ValueError: Value must be either NaN, "empty", or a valid data type (regular value).
    :return: random value
    :rtype: Union[String, Number, Float]
    """
    numerator = secrets.randbelow(100000000)
    generate_number = numerator / 100000000
    left_boundary = 0
    for item in all_value_types_sorted:
        right_boundary = item[1] + left_boundary
        if left_boundary <= generate_number < right_boundary:
            # 0 = value
            # 1 = nan
            # 2 = empty
            if item[0] == 0:
                # this is a regular number, so randomly select one
                generator = generator_factory(secrets.choice(data_types))
                return generator(byte_size)
            elif item[0] == 1:
                # this is a NaN value
                return nan
            elif item[0] == 2:
                # this is an empty value
                return None
            else:
                # this must be an empty value
                raise ValueError(
                    'value must be either nan, empty, or a valid data type'
                )

        left_boundary = right_boundary
