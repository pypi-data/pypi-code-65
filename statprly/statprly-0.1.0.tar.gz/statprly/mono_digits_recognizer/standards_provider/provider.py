"""
Provide implementation of the digit standards provider.
"""
import numpy as np

from statprly.mono_digits_recognizer.standards_provider.interfaces import BaseStandardsProvider


class StandardsProvider(BaseStandardsProvider):
    """
    Implementation of the digit standards provider.
    """

    def get_scaled_standard(
        self,
        digit_data: list,
        vertical_scale: int,
        horizontal_scale: int,
    ) -> np.array:
        """
        Get scaled digit standard.

        :param digit_data: the digit to be data retrieved.
        :param vertical_scale: the amount by which the digit will be scaled vertically.
        :param horizontal_scale: the amount by which the digit will be scaled horizontally.
        :return: digit standard.
        """
        scaled_standards = self.get_scaled_standard_with_noise(
            digit_data=digit_data,
            vertical_scale=vertical_scale,
            horizontal_scale=horizontal_scale,
            noise_probability=0,
        )
        return scaled_standards

    def get_scaled_standard_with_noise(
        self,
        digit_data: list,
        vertical_scale: int,
        horizontal_scale: int,
        noise_probability: float,
    ) -> np.array:
        """
        Get scaled digit standard with `Bernoulli` noise.

        :param digit_data: the digit to be data retrieved.
        :param vertical_scale: the amount by which the digit will be scaled vertically.
        :param horizontal_scale: the amount by which the digit will be scaled horizontally.
        :param noise_probability: the probability of noise to be applied to the digit.
        :return: digit standard.
        """
        if vertical_scale == 0 and horizontal_scale == 0:
            for i in range(len(digit_data)):
                for pixel in range(len(digit_data[i])):
                    pixel_to_add = self._apply_noise_to_element(
                        element=digit_data[i][pixel],
                        noise_probability=noise_probability,
                    )
                    digit_data[i][pixel] = pixel_to_add
            return digit_data

        scaled_standards = []
        for i, row in enumerate(digit_data):

            for h in range(horizontal_scale):
                scaled_standards.append([])

                for j in range(len(row)):
                    for w in range(vertical_scale):

                        pixel_to_add = self._apply_noise_to_element(
                            element=digit_data[i][j],
                            noise_probability=noise_probability,
                        )
                        scaled_standards[i * vertical_scale + h].append(pixel_to_add)

        return scaled_standards

    @staticmethod
    def _apply_noise_to_element(element: int, noise_probability: float) -> int:
        return element ^ (np.random.random() < noise_probability)

    def __repr__(self):
        """
        Printable representation of the StandardsProvider.
        """
        return f"{self.__class__.__name__}"
