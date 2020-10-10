from manimpp.constants import *

from manimpp.animation.animation import *
from manimpp.animation.composition import *
from manimpp.animation.creation import *
from manimpp.animation.fading import *
from manimpp.animation.growing import *
from manimpp.animation.indication import *
from manimpp.animation.movement import *
from manimpp.animation.numbers import *
from manimpp.animation.rotation import *
from manimpp.animation.specialized import *
from manimpp.animation.transform import *
from manimpp.animation.update import *

from manimpp.camera.camera import *
from manimpp.camera.mapping_camera import *
from manimpp.camera.moving_camera import *
from manimpp.camera.three_d_camera import *

from manimpp.mobject.coordinate_systems import *
from manimpp.mobject.changing import *
from manimpp.mobject.frame import *
from manimpp.mobject.functions import *
from manimpp.mobject.geometry import *
from manimpp.mobject.matrix import *
from manimpp.mobject.mobject import *
from manimpp.mobject.number_line import *
from manimpp.mobject.numbers import *
from manimpp.mobject.probability import *
from manimpp.mobject.shape_matchers import *
from manimpp.mobject.svg.brace import *
from manimpp.mobject.svg.drawings import *
from manimpp.mobject.svg.svg_mobject import *
from manimpp.mobject.svg.tex_mobject import *
from manimpp.mobject.svg.text_mobject import *
from manimpp.mobject.svg.code_mobject import *
from manimpp.mobject.three_d_utils import *
from manimpp.mobject.three_dimensions import *
from manimpp.mobject.types.image_mobject import *
from manimpp.mobject.types.point_cloud_mobject import *
from manimpp.mobject.types.vectorized_mobject import *
from manimpp.mobject.mobject_update_utils import *
from manimpp.mobject.value_tracker import *
from manimpp.mobject.vector_field import *

from manimpp.for_3b1b_videos.common_scenes import *
from manimpp.for_3b1b_videos.pi_creature import *
from manimpp.for_3b1b_videos.pi_creature_animations import *
from manimpp.for_3b1b_videos.pi_creature_scene import *

from manimpp.once_useful_constructs.arithmetic import *
from manimpp.once_useful_constructs.combinatorics import *
from manimpp.once_useful_constructs.complex_transformation_scene import *
from manimpp.once_useful_constructs.counting import *
from manimpp.once_useful_constructs.fractals import *
from manimpp.once_useful_constructs.graph_theory import *
from manimpp.once_useful_constructs.light import *

from manimpp.scene.graph_scene import *
from manimpp.scene.moving_camera_scene import *
from manimpp.scene.reconfigurable_scene import *
from manimpp.scene.scene import *
from manimpp.scene.sample_space_scene import *
from manimpp.scene.graph_scene import *
from manimpp.scene.scene_from_video import *
from manimpp.scene.three_d_scene import *
from manimpp.scene.vector_space_scene import *
from manimpp.scene.zoomed_scene import *

from manimpp.utils.bezier import *
from manimpp.utils.color import *
from manimpp.utils.config_ops import *
from manimpp.utils.debug import *
from manimpp.utils.images import *
from manimpp.utils.iterables import *
from manimpp.utils.file_ops import *
from manimpp.utils.paths import *
from manimpp.utils.rate_functions import *
from manimpp.utils.simple_functions import *
from manimpp.utils.sounds import *
from manimpp.utils.space_ops import *
from manimpp.utils.strings import *

from manimpp.yobjects.yrender import *
from manimpp.yobjects.ycolormap import *
from manimpp.yobjects.yscene.yscene import *
from manimpp.yobjects.ymobject.ycoordinate_systems import *

# Non manim libraries that are also nice to have without thinking

import inspect
import itertools as it
import numpy as np
import operator as op
import os
import random
import re
import string
import sys
import math

from PIL import Image
from colour import Color


#!/usr/bin/env python
import manimpp.config
import manimpp.constants
import manimpp.extract_scene
import manimpp_exec

def main():
    args = manimpp.config.parse_cli()
    config = manimpp.config.get_configuration(args)
    manimpp.constants.initialize_directories(config)
    manimpp.extract_scene.main(config)
