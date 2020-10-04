# Gary Koplik
# gary<dot>koplik<at>geomdata<dot>com
# August, 2020
# utils.py

"""
Utility functions for building hive plots.
"""

import numpy as np
from typing import List


def cartesian2polar(x: np.ndarray or float, y: np.ndarray or float):
    """
    Convert cartesian coordinates e.g. (x, y) to polar coordinates e.g. (rho, phi), where rho is distance from
    origin, and phi is counterclockwise angle off of x axis in degrees

    :param x:
    :param y:
    :return: (rho, phi) polar coordinates
    """
    rho = np.sqrt(x**2 + y**2)
    phi = np.degrees(np.arctan2(y, x))
    return rho, phi


def polar2cartesian(rho: np.ndarray or float, phi: np.ndarray or float):
    """
    Convert polar coordinates e.g. (rho, phi) to cartesian coordinates e.g. (x, y)

    :param rho: distance from origin
    :param phi: counterclockwise angle off of x axis in degrees (not radians)
    :return: (x, y) cartesian coordinates
    """
    x = rho * np.cos(np.radians(phi))
    y = rho * np.sin(np.radians(phi))
    return x, y


def bezier(start: float, end: float, control: float, num_steps: int = 100):
    """
    Calculate bezier curve values between `start` and `end` with curve based on `control`.
    Note, this function is hardcoded for exactly 1 control point.

    :param start: starting point
    :param end: ending point
    :param control: "pull" point
    :param num_steps: number of points on bezier curve
    :return: (`num_steps`, ) sized np.ndarray of 1-dimensional discretized bezier curve output
    """
    steps = np.linspace(0, 1, num_steps)
    return (1 - steps) ** 2 * start + 2 * (1 - steps) * steps * control + steps ** 2 * end


def bezier_all(start_arr: List, end_arr: List, control_arr: List, num_steps: int = 100):
    """
    Calculate bezier curve between multiple start and end values.
    Note, this function is hardcoded for exactly 1 control point per curve.

    :param start_arr: starting point of each curve
    :param end_arr: corresponding ending point of each curve
    :param control_arr: corresponding "pull" points for each curve
    :param num_steps: number of points on each bezier curve
    :return: (`start_arr` * `num_steps`, ) sized np.ndarray of 1-dimensional discretized bezier curve output.
        Note, every `num_steps` chunk of the output corresponds to a different bezier curve
    """

    assert np.array(start_arr).size == np.array(end_arr).size == np.array(control_arr).size, \
        "params `start_arr`, `end_arr`, and `control_arr` must be the same size"

    # each curve will be represented by the partitioning of the result by every `num_steps` index vals
    steps = np.tile(np.linspace(0, 1, num_steps), np.array(start_arr).size)

    # repeat each start, stop, and control value to multiply pointwise in one line
    start = np.repeat(start_arr, num_steps)
    end = np.repeat(end_arr, num_steps)
    control = np.repeat(control_arr, num_steps)

    return (1 - steps) ** 2 * start + 2 * (1 - steps) * steps * control + steps ** 2 * end
