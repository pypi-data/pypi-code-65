import xarray as xray
import numpy as np
from .ploteos import correct_mon
class cpp(object):
    def __init__(self,datos):
        self.data=datos
    def month_scaling(self,acu=False,f_cal=None,f_apl=None):
        #APLICAR SCALING MENSUAL---------------------------------
        print('realizando Scaling mensual')
        if f_cal==None or f_apl==None:
            pass
        else:
            self.data['do']=self.data['do'].loc[f_cal[0]:f_cal[1]]
            self.data['dm']=self.data['dm'].loc[f_cal[0]:f_cal[1]]
            self.data['da']=self.data['da'].loc[f_apl[0]:f_apl[1]]
        if acu==True:
            divisor=self.data['dm'].groupby('time.month').mean('time')
            divisor=divisor.where(~(divisor<0.01),0.01)
            fc=(self.data['do'].groupby('time.month').mean('time')/
                    divisor)
            cor=(self.data['da'].groupby('time.month')*fc)
        else:
            fc=(self.data['do'].groupby('time.month').mean('time')-
                    self.data['dm'].groupby('time.month').mean('time'))
            cor=(self.data['da'].groupby('time.month')+fc)
        print('Terminado Scaling mensual')
        return correct_mon(cor,self.data['da'],self.data['do'],self.data['dm'],acu=acu)
    def day_scaling(self,acu=False,f_cal=None,f_apl=None):
        #APLICAR SCALING DIARIO---------------------------
        self.acumulado=acu
        print('realizando Scaling diario')
        if f_cal==None or f_apl==None:
            pass
        else:
            self.data['do']=self.data['do'].loc[f_cal[0]:f_cal[1]]
            self.data['dm']=self.data['dm'].loc[f_cal[0]:f_cal[1]]
            self.data['da']=self.data['da'].loc[f_apl[0]:f_apl[1]]
        if acu==True:
            divisor=self.data['dm'].resample(time='MS').sum('time',skipna=False).groupby('time.month').mean('time')
            divisor=divisor.where(~(divisor<0.01),0.01)
            fc=(self.data['do'].resample(time='MS').sum('time',skipna=False).groupby('time.month').mean('time')/
                    divisor)
            cor=(self.data['da'].groupby('time.month')*fc)
        else:
            fc=(self.data['do'].resample(time='MS').mean('time',skipna=False).groupby('time.month').mean('time')-
                    self.data['dm'].resample(time='MS').mean('time',skipna=False).groupby('time.month').mean('time'))
            cor=(self.data['da'].groupby('time.month')+fc)
        print('Terminado Scaling diario')
        return correct_mon(cor,self.data['da'],self.data['do'],self.data['dm'],acu=acu)
    def day_eqm(self,acu=False,f_cal=None,f_apl=None):
        self.acumulado=acu
        #APLICAR EQM DIARIO.------------------------------
        print('realizando EQM diario')
        if f_cal==None or f_apl==None:
            pass
        else:
            self.data['do']=self.data['do'].loc[f_cal[0]:f_cal[1]]
            self.data['dm']=self.data['dm'].loc[f_cal[0]:f_cal[1]]
            self.data['da']=self.data['da'].loc[f_apl[0]:f_apl[1]]
        quantiles=np.arange(0.01,1,0.01)
        meses=[1,2,3,4,5,6,7,8,9,10,11,12]
        if acu==True:
            print("esta parte demora")
            do_mayor=self.data['do'].where(self.data['do']>=0.001)
            dm_mayor=self.data['dm'].where(self.data['dm']>=0.001)
            da_mayor=self.data['da'].where(self.data['da']>=0.001)
            print("termino la parte que demora")
        for mon in meses:
            if acu==True:
                do_f=do_mayor.loc[do_mayor['time.month']==mon]
                dm_f=dm_mayor.loc[dm_mayor['time.month']==mon]
                da_f=da_mayor.loc[da_mayor['time.month']==mon]
                #do_f=do2.where(do2>=0.1)
                #dm_f=dm2.where(dm2>=0.1)
                #da_f=da2.where(da2>=0.1)
            else:
                do_f=self.data['do'].loc[self.data['do']['time.month']==mon]
                dm_f=self.data['dm'].loc[self.data['dm']['time.month']==mon]
                da_f=self.data['da'].loc[self.data['da']['time.month']==mon]
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
            #cor=self.data['da'].where(~(self.data['da']<0.001),0)
            cor=datos_pro_cor2
            cor=cor.where(cor.notnull(),self.data['da'])
            #cor=cor.where(~(cor>=0.001),datos_pro_cor2)
            cor=cor.where(~(cor<0),0)
            cor=cor.where(self.data['do'].isel(time=0)>-888)
            #cor=cor.where(~(cor<0.001),0)
        else:
            cor=datos_pro_cor2
            cor=cor.where(self.data['do'].isel(time=0)>-888)
        #NOTA: LAS ADVERTENCIAS SALEN DEBIDO A QUE NO HAY DATOS EN OCEANO (POR PARTE DEL OBSERVADO)
        print('realizando EQM diario')
        return correct_mon(cor,self.data['da'],self.data['do'],self.data['dm'],acu=acu)
