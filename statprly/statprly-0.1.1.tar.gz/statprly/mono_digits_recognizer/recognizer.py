"""
Provide implementation of the recognition of the monochrome digits.
"""
import math

import numpy as np

from statprly.constants import (
    DIGIT_STANDARDS_PATH,
    LEAST_LIKELY,
    MOST_LIKELY,
    WHITE_PIXEL,
)
from statprly.errors import ValidationDataError
from statprly.mono_digits_recognizer.data_reader import DataReader
from statprly.mono_digits_recognizer.interfaces import BaseRecognizer
from statprly.mono_digits_recognizer.standards_provider import StandardsProvider


class MonoDigitRecognizer(BaseRecognizer):
    """
    Implementation of the monochrome digits recognizer.
    """

    def __init__(
        self,
        data_provider=DataReader,
        digit_standards_path=DIGIT_STANDARDS_PATH,
        standard_provider=StandardsProvider,
    ):
        self._digit_standards_path = digit_standards_path
        self._data_provider = data_provider(
            digit_standards_path=self._digit_standards_path,
        )

        digit_standards_without_scale = self._data_provider.get_digit_standards_dict()

        self._standards_default_scale = len(digit_standards_without_scale.get("0"))
        self._standard_provider = standard_provider()
        # Key scale - value digit standards with scale
        self._digit_standards_cache = {0: digit_standards_without_scale}

    def recognize(
        self,
        digit_to_predict_data: np.array,
        noise_probability: float,
    ) -> int:
        """
        Predict number from `digit_to_predict` matrix.

        :param digit_to_predict_data: displaying an image of a digit to numpy array `1` and `0`.
        :param noise_probability: the probability of the noise in digit_to_predict data array.
        :return: predicted number.
        """
        self.__validate_recognize_data(
            digit_to_predict_data=digit_to_predict_data,
            noise_probability=noise_probability,
        )
        possible_exodus = range(0, 10)
        digits_probabilities = {}

        for exodus in possible_exodus:
            digit_probability = self.get_digit_probability(
                digit_data=digit_to_predict_data,
                digit_to_compare=exodus,
                noise_probability=noise_probability,
            )

            if digit_probability == MOST_LIKELY:
                return exodus

            digits_probabilities[exodus] = digit_probability

        most_likely_outcome = max(digits_probabilities, key=digits_probabilities.get)
        return most_likely_outcome

    def get_digit_probability(
        self,
        digit_data: np.array,
        digit_to_compare: int,
        noise_probability: float,
    ) -> float:
        """
        Get the probability of a digit behind its array.

        :param digit_data: displaying an image of a digit to numpy array `1` and `0`.
        :param digit_to_compare: the number of probability to be obtained.
        :param noise_probability: the probability of the noise in digit_to_predict data array.
        :return: probability.
        """
        self.__validate_recognize_data(
            digit_to_predict_data=digit_data,
            noise_probability=noise_probability,
        )
        probability = 0

        scale = len(digit_data) / self._standards_default_scale
        scale = int(scale)

        digit_to_compare_data = self.__get_digit_to_compare_data(
            digit_to_compare=digit_to_compare,
            scale=scale,
        )

        if digit_data.shape != digit_to_compare_data.shape:
            ValidationDataError("Invalid `digit_to_predict_data` shape.")

        if noise_probability == MOST_LIKELY:
            digit_data = self.__inverse_digit_pixels(digit_data)

        if noise_probability == LEAST_LIKELY or noise_probability == MOST_LIKELY:
            is_same_image = digit_to_compare_data == digit_data
            probability = float(is_same_image.all())

            return probability

        # Iterate through two arrays:
        # https://numpy.org/doc/stable/reference/arrays.nditer.html#broadcasting-array-iteration
        for pixel, pixel_to_compare in np.nditer([digit_data, digit_to_compare_data]):

            is_different_pixels = pixel != pixel_to_compare

            logarithmic_noise = math.log(noise_probability)
            inverse_logarithmic_noise = math.log(MOST_LIKELY - noise_probability)

            is_white_pixel = WHITE_PIXEL != is_different_pixels

            most_likely_outcome_probability = is_different_pixels * logarithmic_noise
            least_likely_outcome_probability = (
                is_white_pixel * inverse_logarithmic_noise
            )

            probability += (
                most_likely_outcome_probability + least_likely_outcome_probability
            )

        return probability

    def __get_digit_to_compare_data(
        self,
        digit_to_compare: int,
        scale: int,
    ) -> np.array:
        """
        Get digit_to_compare numpy array data.

        :param digit_to_compare: the digit to be data retrieved.
        :return: digit data.
        """
        digit_to_compare_key = str(digit_to_compare)
        if scale not in self._digit_standards_cache:
            self._digit_standards_cache[scale] = self.__generate_standards_with_scale(
                scale=scale,
            )

        digit_to_compare_data = self._digit_standards_cache[scale].get(
            digit_to_compare_key,
        )

        return np.array(digit_to_compare_data)

    def __generate_standards_with_scale(self, scale: int) -> dict:
        """
        Generate dictionary of standards with scale.

        :param scale: the amount by which the digit will be scaled
        """
        scaled_standards = {}
        for i in range(10):
            digit_key = str(i)
            scaled_standards[digit_key] = self._standard_provider.get_scaled_standard(
                digit_data=self._digit_standards_cache[0].get(digit_key),
                vertical_scale=scale,
                horizontal_scale=scale,
            )

        return scaled_standards

    @staticmethod
    def __validate_recognize_data(
        digit_to_predict_data: np.array,
        noise_probability: float,
    ):
        """
        Validate recognize data.

        :param digit_to_predict_data: displaying an image of a digit to numpy array `1` and `0`.
        :param noise_probability: the probability of the noise in digit_to_predict data array.
        """
        if not isinstance(digit_to_predict_data, np.ndarray):
            raise ValidationDataError(
                "`digit_to_predict_data` must be a numpy array data.",
            )

        if 0 < noise_probability > 1:
            raise ValidationDataError(
                "`noise_probability` must be a between `0` and `1`.",
            )

    @staticmethod
    def __inverse_digit_pixels(digit_data):
        """
        Invert digit pixels, pixel^1.

        :param digit_data: digit_data to pixels inverse.
        :return: inverted digit_data.
        """
        return digit_data ^ 1

    @property
    def digit_standards_path(self) -> str:
        """
        Get `digit_standards_path` variable.

        :return: `digit_standards_path` string value
        """
        return self._digit_standards_path

    @digit_standards_path.setter
    def digit_standards_path(self, value):
        """
        Set `digit_standards_path` value and get new basic dictionary of standards digits.

        :param value: `digit_standards_path` variable value
        """
        self._digit_standards_path = value
        self._digit_standards_cache = self._data_provider.get_digit_standards_dict()

    @property
    def data_provider(self):
        """
        Get `data_provider` variable.

        :return: `data_provider` instance value
        """
        return self._data_provider

    @data_provider.setter
    def data_provider(self, value):
        """
        Set `data_provider` value and and get new basic dictionary of standards digits.

        :param value: `data_provider` variable value
        """
        self._data_provider = value(self._digit_standards_path)
        self._digit_standards_cache = self._data_provider.get_digit_standards_dict()

    def __repr__(self):
        """
        Printable representation of the MonoDigitRecognizer.
        """
        return (
            f"{self.__class__.__name__}("
            f"{self._digit_standards_cache!r}, "
            f"{self._data_provider!r}, "
            f"{self._digit_standards_path!r}"
            f")"
        )
