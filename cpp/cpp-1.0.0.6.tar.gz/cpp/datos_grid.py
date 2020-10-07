import xarray as xray
import pandas as pd
import numpy as np
from .cpp import cpp
from .cpp_e import cpp_e
import os.path

def datasets_netcdf(do,dm,da,var,f_cal=None,f_apl=None):
    #LEER DATASETS EN FORMATO NETCDF
    cnj_datos=dict()
    for i,j in zip(['do','dm','da'],[do,dm,da]):
        if f_cal==None or f_apl==None:
            #SIN ESPECIFICAR FECHA
            cnj_datos[i]=xray.open_dataset(j)[var]
        else:
            #CON FECHA ESPECIFICADA
            if i=='da':
                cnj_datos[i]=xray.open_dataset(j)[var].sel(time=slice(f_apl[0],f_apl[1]))
            else:
                cnj_datos[i]=xray.open_dataset(j)[var].sel(time=slice(f_cal[0],f_cal[1]))
        #Interpolacion Lineal
        for la,lo in zip(['latitud','latitude','Latitude'],['longitud','longitude','Longitude']):
            if ((la in cnj_datos[i].coords.dims) and (lo in cnj_datos[i].coords.dims)):
                print('cambiando nombre de coordenadas a latlon')
                cnj_datos[i]=cnj_datos[i].rename({la:'lat',lo:'lon'})
            else:
                print('nombres latlon correcto')
        if i!='do':
            if not (np.array_equal(cnj_datos['do']['lat'].values,cnj_datos[i]['lat'].values) and
             np.array_equal(cnj_datos['do']['lon'].values,cnj_datos[i]['lon'].values)):
                print('interpolando latlon')
                cnj_datos[i]=cnj_datos[i].interp(lat=cnj_datos['do']['lat'],lon=cnj_datos['do']['lon'])
            else:
                pass
        #Orden de dimensiones
        cnj_datos[i]=cnj_datos[i].transpose("time", "lat", "lon")
    return cpp(cnj_datos)

def open_station(estaciones,do,dm,da,var,f_cal=None,f_apl=None):
    #LEER DATASETS EN FORMATO NETCDF
    cnj_datos=dict()
    coords=pd.read_csv(estaciones,delimiter=';',index_col=0)
    datos=pd.read_csv(do,delimiter=';',index_col=0)
    datos.index=pd.to_datetime(datos.index,format='%d/%m/%Y')
    datos=datos.loc[f_cal[0]:f_cal[1]]
    if f_cal==None or f_apl==None:
        cnj_datos['dm']=xray.open_dataset(dm)[var]
        cnj_datos['da']=xray.open_dataset(da)[var]
    else:
        cnj_datos['dm']=xray.open_dataset(dm)[var].sel(time=slice(f_cal[0],f_cal[1]))
        cnj_datos['da']=xray.open_dataset(da)[var].sel(time=slice(f_apl[0],f_apl[1]))
    for model_data in ['dm','da']:
        for la,lo in zip(['latitud','latitude','Latitude'],['longitud','longitude','Longitude']):
            if ((la in model_data.coords.dims) and (lo in model_data.coords.dims)):
                print('cambiando nombre de coordenadas a latlon')
                cnj_datos[model_data]=cnj_datos[model_data].rename({la:'lat',lo:'lon'})
            else:
                print('nombres latlon correcto')
    if cnj_datos['dm']['lon'].max()>180:
        cnj_datos['dm']['lon']=cnj_datos['dm']['lon']-360.0
    if cnj_datos['da']['lon'].max()>180:
        cnj_datos['da']['lon']=cnj_datos['da']['lon']-360.0
    cnj_datos['do']=datos
    cnj_datos['coords']=coords
    return cpp_e(cnj_datos)
