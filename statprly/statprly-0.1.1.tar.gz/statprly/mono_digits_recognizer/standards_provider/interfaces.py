"""
Provide interfaces for digit standards provider.
"""
from abc import (
    ABC,
    abstractmethod,
)

from numpy import array


class BaseStandardsProvider(ABC):
    """
    Implementation of the basic standards provider.
    """

    @abstractmethod
    def get_scaled_standard_with_noise(
        self,
        digit_data: list,
        vertical_scale: int,
        horizontal_scale: int,
        noise_probability: float,
    ) -> array:
        """
        Get scaled digit standard with `Bernoulli` noise.

        :param digit_data: the digit to be data retrieved.
        :param vertical_scale: the amount by which the digit will be scaled vertically.
        :param horizontal_scale: the amount by which the digit will be scaled horizontally.
        :param noise_probability: the probability of noise to be applied to the digit.
        :return: digit standard.
        """

    @abstractmethod
    def get_scaled_standard(
        self,
        digit_data: list,
        vertical_scale: int,
        horizontal_scale: int,
    ) -> array:
        """
        Get scaled digit standard.

        :param digit_data: the digit to be data retrieved.
        :param vertical_scale: the amount by which the digit will be scaled vertically.
        :param horizontal_scale: the amount by which the digit will be scaled horizontally.
        :return: digit standard.
        """
