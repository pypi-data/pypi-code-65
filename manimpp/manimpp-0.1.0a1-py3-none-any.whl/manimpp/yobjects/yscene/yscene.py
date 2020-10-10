import inspect
import random
import warnings
import platform

from tqdm import tqdm as ProgressDisplay
import numpy as np

from manimpp.animation.animation import Animation
from manimpp.animation.transform import MoveToTarget, ApplyMethod
from manimpp.camera.camera import Camera
from manimpp.constants import *
from manimpp.container.container import Container
from manimpp.mobject.mobject import Mobject
from manimpp.scene.scene_file_writer import SceneFileWriter
from manimpp.utils.iterables import list_update
from manimpp.scene.scene import *

class YScene(Scene):
    CONFIG = {
        "camera_class": Camera,
        "camera_config": {},
        "file_writer_config": {},
        "skip_animations": False,
        "always_update_mobjects": False,
        "random_seed": 0,
        "start_at_animation_number": None,
        "end_at_animation_number": None,
        "leave_progress_bars": False,
    }

    def setBackgroundColor(self,cm):
        self.camera_config = {
            "background_color": background_color,
        }

    def setBackgroundColor(self,cm):
        self.camera_config = {
            "background_color": cm,
        }
        self.camera = self.camera_class(**self.camera_config)