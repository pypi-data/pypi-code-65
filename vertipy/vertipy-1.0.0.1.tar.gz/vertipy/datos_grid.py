# Copyright 2020 by Erick Alexis Alvarez Sanchez, The national meteorological and hydrological service of Peru (SENAMHI).
# All rights reserved.
# This file is part of the VERTIpy package,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import xarray as xray
import numpy as np
from .convertible import hybrid_height
from .convertible import hybrid_sigma
from .ploteos import convertido
import os.path

def open_hybrid_height_params(ta,hus,ps,orog=None,b=None,decode_times=True):
    #abrir para metros de hibridas de altura
    datos=dict()
    if orog==None and b==None:
        ta=xray.open_dataset(ta,decode_times=decode_times)
        for name in ['ta','orog','b']:
            datos[name]=ta[name]
        datos['hus']=xray.open_dataset(hus,decode_times=decode_times)['hus']
        datos['ps']=xray.open_dataset(ps,decode_times=decode_times)['ps']
    else:
        datos['ta']=xray.open_dataset(ta,decode_times=decode_times)['ta']
        datos['hus']=xray.open_dataset(hus,decode_times=decode_times)['hus']
        datos['ps']=xray.open_dataset(ps,decode_times=decode_times)['ps']
        datos['orog']=xray.open_dataset(orog,decode_times=decode_times)['orog']
        #datos['lev']=xray.open_dataset(a,decode_times=decode_times)['lev']
        datos['b']=xray.open_dataset(b,decode_times=decode_times)['b']
        #try:
        #    datos['p0']=xray.open_dataset(p0,decode_times=decode_times)['p0']
        #except:
        #    datos['p0']=p0
    return hybrid_height(datos)

def open_hybrid_sigma_params(a=None,b=None,ps=None,p0=None,data=None,decode_times=True):
    #abrir parametros de hibridas sigma
    datos=dict()
    if a==None and b==None and ps==None and p0==None:
        data=xray.open_dataset(data,decode_times=decode_times)
        for name in ['a','b','ps','p0']:
            datos[name]=data[name]
    else:
        datos['a']=xray.open_dataset(a,decode_times=decode_times)['a']
        datos['b']=xray.open_dataset(b,decode_times=decode_times)['b']
        datos['ps']=xray.open_dataset(ps,decode_times=decode_times)['ps']
        try:
            datos['p0']=xray.open_dataset(p0,decode_times=decode_times)['p0']
        except:
            datos['p0']=p0
    return hybrid_sigma(datos)

def interpolate_to_pressure(data,presion,niveles,extrapolate=False,decode_times=True):
    #interpolar datos a presion
    try:
        data=xray.open_dataset(data,decode_times=decode_times)
        data=data[list(data.data_vars.keys())[0]]
        #data=data[var]
    except:
        print("No se encontraron archivos con datos, procediendo a buscar variables")
        data=data
    try:
        presion=xray.open_dataset(presion,decode_times=decode_times)
        presion=presion[list(presion.data_vars.keys())[0]]
    except:
        print("No se encontraron archivos de presion,procediendo a buscar variables")
        presion=presion
    n=0
    for valor in niveles:
        pres_eval_u=presion.where(presion<=valor)
        pres_eval_l=presion.where(presion>valor)
        temp_u=data.where(pres_eval_u==pres_eval_u.max('lev')).min('lev')
        temp_l=data.where(pres_eval_l==pres_eval_l.min('lev')).min('lev')
        pres_u=pres_eval_u.max('lev')
        pres_l=pres_eval_l.min('lev')
        interpolados=(((valor-pres_u)/(pres_l-pres_u))*(temp_l-temp_u))+temp_u
        if n==0:
            datos_interp=interpolados.copy()
            n+=1
        else:
            datos_interp=xray.concat([datos_interp,interpolados],dim='nivel')
    shape_cont=len(datos_interp.shape)
    datos_interp['nivel']=niveles
    if extrapolate==True:
        #extrapolar variables
        try:
            from gridfill import fill
        except ImportError:
            raise ImportError('Se necesida del modulo gridfill, Repositorio-> https://github.com/ajdawson/gridfill')
        datos_mascara=np.ma.masked_invalid(datos_interp.values)
        kw = dict(eps=1e-4, relax=0.6, itermax=1e4, initzonal=False,
                      cyclic=False, verbose=True)
        filled,converged = fill(datos_mascara,shape_cont-1,shape_cont-2,**kw)
        #datos_interp2=datos_interp.copy()
        datos_interp.values=filled
        return convertido(datos_interp,data.isel(time=0))
    else:
        print(datos_interp)
        return convertido(datos_interp,data.isel(time=0))
