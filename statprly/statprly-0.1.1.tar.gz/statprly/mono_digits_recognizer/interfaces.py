"""
Provide interfaces for monochrome digits recognition.
"""
from abc import (
    ABC,
    abstractmethod,
)

from numpy import array


class BaseRecognizer(ABC):
    """
    Implementation of the basic recognizer.
    """

    @abstractmethod
    def recognize(self, digit_to_predict: array, noise_probability: float) -> int:
        """
        Predict number from `digit_to_predict` matrix.

        :param digit_to_predict: data of displaying an image of a digit to numpy array `1` and `0`.
        :param noise_probability: the probability of the noise in digit_to_predict data array.
        :return: predicted number.
        """

    def get_digit_probability(
        self,
        digit_data: array,
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
