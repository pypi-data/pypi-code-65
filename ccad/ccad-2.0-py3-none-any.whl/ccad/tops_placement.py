#!/usr/bin/python
# coding: utf-8

"""
https://en.wikipedia.org/wiki/Circle_packing_in_a_circle
http://www.packomania.com/

enclosing_r is the radius of the circle packing n circles of radius 1.
"""

import numpy as np
from typing import List, Tuple

from .exceptions import *
from .top_in import TopInlet


def check_inlets(r_inlets: float, list_inlets: List[TopInlet]) -> None:

    """
    Check that no inlet has a radius superior to the therotical max radius

    Arguments:
        r_inlets {float} -- [description]
        list_inlets {List[TopInlet]} -- [description]

    Raises:
        ConstraintError -- [description]

    Returns:
        None
    """

    mes = "Inlet {} is too big. Radius should be < {} mm and is {} mm"

    for inlet in list_inlets:
        if inlet.diameter / 2 + inlet.walls > r_inlets:
            raise ConstraintError(
                mes.format(inlet, r_inlets, inlet.diameter / 2 + inlet.walls)
            )


def get_positions_1(R: float, list_inlets: List[TopInlet]) -> List[Tuple[float, float]]:

    """
    [summary]

    Arguments:
        R {float} -- [description]
        list_inlets {List[TopInlet]} -- [description]

    Returns:
        List[Tuple[float, float]] -- [description]
    """

    r_inlets = R

    check_inlets(r_inlets, list_inlets)

    return [(0, 0)]


def get_positions_2(R: float, list_inlets: List[TopInlet]) -> List[Tuple[float, float]]:

    """
    [summary]

    Arguments:
        R {float} -- [description]
        list_inlets {List[TopInlet]} -- [description]

    Returns:
        List[Tuple[float, float]] -- [description]
    """

    enclosing_r = 2

    # Radius of inlet is not 1, so scale it to real radius of top of reactor
    r_inlets = R / enclosing_r

    check_inlets(r_inlets, list_inlets)

    list_pos: List[Tuple[float, float]] = [(-r_inlets, 0), (r_inlets, 0)]

    return list_pos


def get_positions_3(R: float, list_inlets: List[TopInlet]) -> List[Tuple[float, float]]:

    """
    [summary]

    Arguments:
        R {float} -- [description]
        list_inlets {List[TopInlet]} -- [description]

    Returns:
        List[Tuple[float, float]] -- [description]
    """

    enclosing_r = 1 + 2 / np.sqrt(3)

    r_inlets = R / enclosing_r

    check_inlets(r_inlets, list_inlets)

    # Distance origin-center/inlet
    d_inlet = R - r_inlets

    list_pos = list()

    # Create a temporary center for the inlets. It will be rotated
    x_start = d_inlet
    y_start = 0

    # 3 inlets, 3 angles of rotation for temp center
    for a in [30, 150, 270]:
        a = np.deg2rad(a)
        new_x = -y_start * np.sin(a) + x_start * np.cos(a)
        new_y = y_start * np.cos(a) + x_start * np.sin(a)
        list_pos.append((new_x, new_y))

    return list_pos


def get_positions_4(R: float, list_inlets: List[TopInlet]) -> List[Tuple[float, float]]:

    """
    [summary]

    Arguments:
        R {float} -- [description]
        list_inlets {List[TopInlet]} -- [description]

    Returns:
        List[Tuple[float, float]] -- [description]
    """

    enclosing_r = 1 + np.sqrt(2)

    r_inlets = R / enclosing_r

    check_inlets(r_inlets, list_inlets)

    # Distance origin-center/inlet
    d_inlet = R - r_inlets

    list_pos = list()

    # Create a temporary center for the inlets. It will be rotated
    x_start = d_inlet
    y_start = 0

    for a in [45, 135, 225, 315]:
        a = np.deg2rad(a)
        new_x = -y_start * np.sin(a) + x_start * np.cos(a)
        new_y = y_start * np.cos(a) + x_start * np.sin(a)
        list_pos.append((new_x, new_y))

    return list_pos


def get_positions_5(R: float, list_inlets: List[TopInlet]) -> List[Tuple[float, float]]:

    """
    [summary]

    Arguments:
        R {float} -- [description]
        list_inlets {List[TopInlet]} -- [description]

    Returns:
        List[Tuple[float, float]] -- [description]
    """

    enclosing_r = 1 + np.sqrt(2 * (1 + 1 / np.sqrt(5)))

    r_inlets = R / enclosing_r

    check_inlets(r_inlets, list_inlets)

    # Distance origin-center/inlet
    d_inlet = R - r_inlets

    list_pos = list()

    # Create a temporary center for the inlets. It will be rotated
    x_start = d_inlet
    y_start = 0

    for a in [54, 126, 198, 270, 342]:
        a = np.deg2rad(a)
        new_x = -y_start * np.sin(a) + x_start * np.cos(a)
        new_y = y_start * np.cos(a) + x_start * np.sin(a)
        list_pos.append((new_x, new_y))

    return list_pos


def get_positions(R: float, list_inlets: List[TopInlet]) -> List[Tuple[float, float]]:

    """
    [summary]

    Arguments:
        R {float} -- [description]
        list_inlets {List[TopInlet]} -- [description]

    Returns:
        List[Tuple[float, float]] -- [description]
    """

    list_pos: List[Tuple[float, float]] = list()

    if len(list_inlets) == 1:
        list_pos = get_positions_1(R, list_inlets)

    elif len(list_inlets) == 2:
        list_pos = get_positions_2(R, list_inlets)

    elif len(list_inlets) == 3:
        list_pos = get_positions_3(R, list_inlets)

    elif len(list_inlets) == 4:
        list_pos = get_positions_4(R, list_inlets)

    elif len(list_inlets) == 5:
        list_pos = get_positions_5(R, list_inlets)

    return list_pos


if __name__ == "__main__":
    pass
