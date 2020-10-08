# Copyright 2020 by Erick Alexis Alvarez Sanchez, The national meteorological and hydrological service of Peru (SENAMHI).
# All rights reserved.
# This file is part of the VERTIpy package,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import seaborn as sns
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt

class convertido(object):
    def __init__(self,new_coord_dataset,coord_dataset):
        self.convertido=new_coord_dataset
        self.anterior=coord_dataset
    def plot(self,invert_y=False):
        d=round(len(self.convertido.lat)/2)
        fig,axes=plt.subplots(1,2,figsize=(13,4))
        vmin=int(self.convertido.isel(lat=d).isel(time=0).min().values)
        vmax=int(self.convertido.isel(lat=d).isel(time=0).max().values)
        self.anterior.isel(lat=d).plot.contourf(ax=axes[0],levels=20,cmap='jet',vmin=vmin,vmax=vmax)
        self.convertido.isel(lat=d).isel(time=0).plot.contourf(ax=axes[1],levels=20,cmap='jet',vmin=vmin,vmax=vmax)
        axes[1].invert_yaxis()
        if invert_y==True:
            axes[0].invert_yaxis()
        plt.suptitle('ANTERIOR COORDENADA (IZQUIERDA) - NUEVA COORDENADA (DERECHA)')
