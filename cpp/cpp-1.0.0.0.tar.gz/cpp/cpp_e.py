import xarray as xray
import numpy as np
import pandas as pd
from .ploteos import correct_mon
from .ploteos_e import correct_e

class cpp_e(object):
    def __init__(self,datos):
        self.data=datos
    def day_scaling(self,acu=False,f_cal=None,f_apl=None):
        #APLICAR SCALING DIARIO---------------------------
        print('realizando Scaling diario')
        cnj_do=pd.DataFrame()
        cnj_dm=pd.DataFrame()
        cnj_da=pd.DataFrame()
        cnj_cor=pd.DataFrame()
        for name in self.data['coords']['nombre']:
            print(name)
            coords=self.data['coords']
            data=self.data['do'][name]
            filtro_mes=data.resample('MS').agg(pd.Series.sum,skipna=False)
            data=data.where(~filtro_mes.reindex(data.index,method='ffill').isna())
            lat=coords.loc[coords['nombre']==name]['lat'].values[0]
            lon=coords.loc[coords['nombre']==name]['lon'].values[0]
            do=data.to_xarray()
            do=do.rename({'index':'time'})
            dm=self.data['dm'].interp(lat=lat,lon=lon)
            dm=dm.drop(['lat','lon'])
            da=self.data['da'].interp(lat=lat,lon=lon)
            da=da.drop(['lat','lon'])
            if f_cal==None or f_apl==None:
                pass
            else:
                do=do.loc[f_cal[0]:f_cal[1]]
                dm=dm.loc[f_cal[0]:f_cal[1]]
                da=da.loc[f_apl[0]:f_apl[1]]
            do['time']=dm['time']
            dm=dm.where(do>-888)
            if acu==True:
                divisor=dm.resample(time='MS').sum('time',skipna=False).groupby('time.month').mean('time')
                divisor=divisor.where(~(divisor<0.01),0.01)
                fc=(do.resample(time='MS').sum('time',skipna=False).groupby('time.month').mean('time')/
                        divisor)
                cor=(da.groupby('time.month')*fc)
            else:
                fc=(do.resample(time='MS').mean('time',skipna=False).groupby('time.month').mean('time')-
                        dm.resample(time='MS').mean('time',skipna=False).groupby('time.month').mean('time'))
                cor=(da.groupby('time.month')+fc)
            cor=cor.drop(['month'])
            cnj_do.loc[:,name]=do.to_dataframe(name=name).iloc[:,0]
            cnj_dm.loc[:,name]=dm.to_dataframe(name=name).iloc[:,0]
            cnj_da.loc[:,name]=da.to_dataframe(name=name).iloc[:,0]
            cnj_cor.loc[:,name]=cor.to_dataframe(name=name).iloc[:,0]
        print('Terminado Scaling diario')
        return correct_e(cnj_cor,cnj_da,cnj_dm,cnj_do,acu=acu)
    def day_eqm(self,acu=False,f_cal=None,f_apl=None):
        self.acumulado=acu
        #APLICAR EQM DIARIO.------------------------------
        print('realizando EQM diario')
        cnj_do=pd.DataFrame()
        cnj_dm=pd.DataFrame()
        cnj_da=pd.DataFrame()
        cnj_cor=pd.DataFrame()
        for name in self.data['coords']['nombre']:
            print(name)
            coords=self.data['coords']
            data=self.data['do'][name]
            filtro_mes=data.resample('MS').agg(pd.Series.sum,skipna=False)
            data=data.where(~filtro_mes.reindex(data.index,method='ffill').isna())
            lat=coords.loc[coords['nombre']==name]['lat'].values[0]
            lon=coords.loc[coords['nombre']==name]['lon'].values[0]
            do=data.to_xarray()
            do=do.rename({'index':'time'})
            dm=self.data['dm'].interp(lat=lat,lon=lon)
            dm=dm.drop(['lat','lon'])
            da=self.data['da'].interp(lat=lat,lon=lon)
            da=da.drop(['lat','lon'])
            if f_cal==None or f_apl==None:
                pass
            else:
                do=do.loc[f_cal[0]:f_cal[1]]
                dm=dm.loc[f_cal[0]:f_cal[1]]
                da=da.loc[f_apl[0]:f_apl[1]]
            do['time']=dm['time']
            dm=dm.where(do>-888)
            quantiles=np.arange(0.01,1,0.01)
            meses=[1,2,3,4,5,6,7,8,9,10,11,12]
            for mon in meses:
                do2=do.loc[do['time.month']==mon]
                dm2=dm.loc[dm['time.month']==mon]
                da2=da.loc[da['time.month']==mon]
                if acu==True:
                    do_f=do2.where(do2>=0.001)
                    dm_f=dm2.where(dm2>=0.001)
                    da_f=da2.where(da2>=0.001)
                else:
                    do_f=do2
                    dm_f=dm2
                    da_f=da2
                datos_his=dm_f
                datos_pro=da_f
                datos_obs_q=do_f.quantile(quantiles,dim='time')
                datos_his_q=dm_f.quantile(quantiles,dim='time')
                datos_pro_q=da_f.quantile(quantiles,dim='time')
                for quan in quantiles:
                    if quan==0.01:
                        datos_his_cor=datos_his.where(datos_his>datos_his_q.sel(quantile=0.02,method='nearest'),
                                                      datos_obs_q.sel(quantile=0.01,method='nearest'))
                    elif quan==0.99:
                        datos_his_cor=datos_his_cor.where(~(datos_his>=datos_his_q.sel(quantile=0.99,method='nearest')),
                                                          datos_obs_q.sel(quantile=0.99,method='nearest'))
                    else:
                        datos_his_cor=datos_his_cor.where(~((datos_his>=datos_his_q.sel(quantile=quan,method='nearest'))&
                                                          (datos_his<datos_his_q.sel(quantile=quan+0.01,method='nearest'))),
                                                          datos_obs_q.sel(quantile=quan,method='nearest'))

                deltas=datos_his_cor.quantile(quantiles,dim='time')-datos_his.quantile(quantiles,dim='time')
                #AÑADIENDO DELTAS DE QUANTILES A LA INFORMACION PROYECTADA.
                for quan in quantiles:
                    if quan==0.01:
                        datos_pro_cor=datos_pro.where(datos_pro>datos_pro_q.sel(quantile=0.02,method='nearest'),
                                                      datos_pro+deltas.sel(quantile=0.01,method='nearest'))
                    elif quan==0.99:
                        datos_pro_cor=datos_pro_cor.where(~(datos_pro>=datos_pro_q.sel(quantile=0.99,method='nearest')),
                                                          datos_pro+deltas.sel(quantile=0.99,method='nearest'))
                    else:
                        datos_pro_cor=datos_pro_cor.where(~((datos_pro>=datos_pro_q.sel(quantile=quan,method='nearest'))&
                                                          (datos_pro<datos_pro_q.sel(quantile=quan+0.01,method='nearest'))),
                                                          datos_pro+deltas.sel(quantile=quan,method='nearest'))
                if mon==1:
                    datos_his_cor2=datos_his_cor
                    datos_pro_cor2=datos_pro_cor
                else:
                    datos_his_cor2=xray.concat([datos_his_cor2,datos_his_cor],dim='time')
                    datos_pro_cor2=xray.concat([datos_pro_cor2,datos_pro_cor],dim='time')
            datos_his_cor2=datos_pro_cor2.sortby('time',ascending=True)
            datos_pro_cor2=datos_pro_cor2.sortby('time',ascending=True)
            if acu==True:
                #cor=da.where(~(da<0.1),0)
                #cor=cor.where(~(cor>=0.1),datos_pro_cor2)
                cor=datos_pro_cor2
                cor=cor.where(cor.notnull(),da)
                cor=cor.where(~(cor<0),0)
            else:
                cor=datos_pro_cor2
            cnj_do.loc[:,name]=do.to_dataframe(name=name).iloc[:,0]
            cnj_dm.loc[:,name]=dm.to_dataframe(name=name).iloc[:,0]
            cnj_da.loc[:,name]=da.to_dataframe(name=name).iloc[:,0]
            cnj_cor.loc[:,name]=cor.to_dataframe(name=name).iloc[:,0]
        #NOTA: LAS ADVERTENCIAS SALEN DEBIDO A QUE NO HAY DATOS EN OCEANO (POR PARTE DEL OBSERVADO)
        print('realizando EQM diario')
        return correct_e(cnj_cor,cnj_da,cnj_dm,cnj_do,acu=acu)
