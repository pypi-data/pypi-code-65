# Copyright 2020 by Erick Alexis Alvarez Sanchez, The national meteorological and hydrological service of Peru (SENAMHI).
# All rights reserved.
# This file is part of the VERTIpy package,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import xarray as xray
import numpy as np

class hybrid_height(object):
    def __init__(self,datos):
        self.datos=datos
    def pressure_from_hybrid_heigh(self):
        temp=self.datos['ta']
        orogen=self.datos['orog']
        hesp=self.datos['hus']
        psa=self.datos['ps']
        r=hesp/(1-hesp)
        tv=temp*(1+61*r)
        niveles=temp['lev']+self.datos['b']*orogen
        presion=temp.copy()
        for i in range(niveles['lev'].shape[0]):
            if i==0:
                presion[dict(lev=0)]=(psa*np.exp((-9.8/(287.055*tv[dict(lev=0)]))*(niveles[dict(lev=0)]-orogen)))
            else:
                presion[dict(lev=i)]=(presion[dict(lev=i-1)]*np.exp((-9.8/(287.055*tv[dict(lev=i)]))*(niveles[dict(lev=i)]-niveles[dict(lev=i-1)])))
        return presion

class hybrid_sigma(object):
    def __init__(self,datos):
        self.datos=datos
    def pressure_from_hybrid_sigma(self):
        self.datos['a']=self.datos['a']*self.datos['p0']
        presion=self.datos['a']+self.datos['ps']*self.datos['b']
        return presion
