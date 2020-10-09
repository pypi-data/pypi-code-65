#!/usr/bin/python
# coding: utf-8

"""
Small module for random functions
"""

import numpy as np


def simplifyAngle(angle: float) -> None:

    """
    Simplify an angle. Ex: -90 -> 270°
                           360° -> 0°
                           540° -> 180°
    All negative angles will be transformed to their positive equivalent.
    https://stackoverflow.com/questions/31428250/how-to-simplify-angles-in-degrees-in-r

    Needed to make sure angles in scad files have reproducible values
    (ex: -90 and 270 are equivalent, but will give different scad files
    and will trigger unecessary rendering)

    Arguments:
        angle {float} -- [description]

    Returns:
        None
    """

    angle = ((angle * np.pi / 360) % np.pi) * 360 / np.pi

    return angle


if __name__ == "__main__":
    pass
