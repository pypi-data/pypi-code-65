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
