import xarray as xray
import pandas as pd
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
        if i!='do':
            cnj_datos[i]=cnj_datos[i].interp(lat=cnj_datos['do']['lat'],lon=cnj_datos['do']['lon'])
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
        dm=xray.open_dataset(dm)[var]
        da=xray.open_dataset(da)[var]
    else:
        dm=xray.open_dataset(dm)[var].sel(time=slice(f_cal[0],f_cal[1]))
        da=xray.open_dataset(da)[var].sel(time=slice(f_apl[0],f_apl[1]))
    if dm['lon'].max()>180:
        dm['lon']=dm['lon']-360.0
    if da['lon'].max()>180:
        da['lon']=da['lon']-360.0
    cnj_datos['do']=datos
    cnj_datos['dm']=dm
    cnj_datos['da']=da
    cnj_datos['coords']=coords
    return cpp_e(cnj_datos)
