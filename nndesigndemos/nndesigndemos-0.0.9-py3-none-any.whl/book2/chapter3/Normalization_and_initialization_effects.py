from PyQt5 import QtWidgets, QtCore
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)
from mpl_toolkits.mplot3d import Axes3D

from nndesigndemos.nndesign_layout import NNDLayout
from nndesigndemos.get_package_path import PACKAGE_PATH


class NormAndInitEffects(NNDLayout):
    def __init__(self, w_ratio, h_ratio, dpi):
        super(NormAndInitEffects, self).__init__(w_ratio, h_ratio, dpi, main_menu=2)

        self.fill_chapter("Gradient Descent", 3, "\nClick anywhere on the\ngraph to start an initial guess."
                                                 "\nThen the steepest descent\ntrajectory will be shown.\n\n"
                                                 "Modify the learning rate\nby moving the slide bar.\n\n"
                                                 "Experiment with different\ninitial guesses and\nlearning rates.",
                          PACKAGE_PATH + "Chapters/3_D/Logo_Ch_3.svg", None,
                          icon_move_left=120, description_coords=(535, 105, 450, 250))

