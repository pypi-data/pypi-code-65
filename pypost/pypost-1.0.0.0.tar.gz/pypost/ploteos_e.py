# Copyright 2020 by Erick Alexis Alvarez Sanchez, The national meteorological and hydrological service of Peru (SENAMHI).
# All rights reserved.
# This file is part of the pypost package,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import seaborn as sns
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt
class correct_e:
    def __init__(self,cor,da,dm,do,acu=False):
        self.observados=do
        self.historicos=dm
        self.proyectados=da
        self.corregidos=cor
