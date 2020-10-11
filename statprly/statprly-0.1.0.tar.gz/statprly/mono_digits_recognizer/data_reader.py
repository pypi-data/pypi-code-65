"""
Provide implementation of the DataReader.
"""
import json

import numpy

from statprly.constants import SUPPORTED_DIMENSION_OF_STANDARDS
from statprly.errors import ValidationDataError


class DataReader:
    """
    Implementation of the DataReader.
    """

    def __init__(self, digit_standards_path):
        self.digit_standards_path = digit_standards_path

    def get_digit_standards_dict(self) -> dict:
        """
        Read data from `seed_data_path`.

        Read data from `digit_standards_path` and transform it into `dictionary` object
        where the key is the digit, value is the array of digit image data (array of `1` and `0`).
        """
        with open(self.digit_standards_path) as f:
            standards = json.loads(f.read())

        self.__validate_data(standards)
        return standards

    @staticmethod
    def __validate_data(data: dict):
        """
        Digit standards data validation.

        :param data: digit data to be validated
        """
        base_shape = numpy.array(data["0"]).shape
        if len(base_shape) != SUPPORTED_DIMENSION_OF_STANDARDS:
            raise ValidationDataError("Data shape validation error.")

        base_digit_pixels_sum = base_shape[1]

        for digit in data.values():
            digit_data = numpy.array(digit)
            digit_shape = digit_data.shape

            if base_shape != digit_shape:
                raise ValidationDataError("Data shape validation error.")

            for pixels in digit:
                sum_of_pixels = sum(pixels)

                if sum_of_pixels > base_digit_pixels_sum:
                    raise ValidationDataError("Invalid pixel in data.")
