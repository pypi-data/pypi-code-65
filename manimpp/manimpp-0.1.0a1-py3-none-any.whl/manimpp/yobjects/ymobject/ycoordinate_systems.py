import numpy as np
import numbers

from manimpp.constants import *
from manimpp.mobject.functions import ParametricFunction
from manimpp.mobject.geometry import Arrow
from manimpp.mobject.geometry import Line
from manimpp.mobject.number_line import NumberLine
from manimpp.mobject.svg.tex_mobject import TexMobject
from manimpp.mobject.types.vectorized_mobject import VGroup
from manimpp.utils.config_ops import digest_config
from manimpp.utils.config_ops import merge_dicts_recursively
from manimpp.utils.simple_functions import binary_search
from manimpp.utils.space_ops import angle_of_vector
from manimpp.mobject.coordinate_systems import *

class YAxes(Axes):
    CONFIG = {
        "axis_config": {
            "color": LIGHT_GREY,
            "include_tip": True,
            "exclude_zero_from_default_numbers": True,
        },
        "x_axis_config": {},
        "y_axis_config": {
            "label_direction": LEFT,
        },
        "center_point": ORIGIN,
        "dimension": 2,
        "x_min": -FRAME_X_RADIUS,
        "x_max": FRAME_X_RADIUS,
        "y_min": -FRAME_Y_RADIUS,
        "y_max": FRAME_Y_RADIUS,
    }

    def __init__(self,xmin=-FRAME_X_RADIUS,
                 xmax=FRAME_X_RADIUS,
                 ymin=-FRAME_Y_RADIUS,
                 ymax=FRAME_Y_RADIUS,
                 x_tick_frequency = 1,
                 x_labeled_nums = [0],
                 x_label_decimal = 1,
                 x_axis_width = 9,
                 y_tick_frequency=1,
                 y_labeled_nums=[0],
                 y_label_decimal=1,
                 y_axis_width=9,
                 axes_color=LIGHT_GREY):
        self.x_min = xmin
        self.x_max = xmax
        self.y_min = ymin
        self.y_max = ymax
        self.axis_config = {
            "color": axes_color,
            "include_tip": True,
            "exclude_zero_from_default_numbers": True,
        }
        x_num_range = float(self.x_max - self.x_min)
        space_unit_to_x = x_axis_width / x_num_range
        self.x_axis_config = {
            "numbers_with_elongated_ticks": x_labeled_nums,
            "tick_frequency": x_tick_frequency,
            "decimal_number_config": {
                "num_decimal_places": x_label_decimal,
            },
            "unit_size" : space_unit_to_x,
        }
        y_num_range = float(self.y_max - self.y_min)
        space_unit_to_y = y_axis_width / y_num_range
        self.y_axis_config = {
            "numbers_with_elongated_ticks": y_labeled_nums,
            "tick_frequency": y_tick_frequency,
            "decimal_number_config": {
                "num_decimal_places": y_label_decimal,
            },
            "unit_size": space_unit_to_y,
        }
        Axes.__init__(self)