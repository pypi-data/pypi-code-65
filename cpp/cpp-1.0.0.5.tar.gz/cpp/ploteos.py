import seaborn as sns
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt
class correct_mon:
    def __init__(self,cor,da,do,dm,acu=False):
        self.corregido=cor
        self.no_corregido=da
        self.observado=do
        self.historico=dm
        self.acu=acu
    def plot(self):
        if self.acu==True:
            cmap='viridis'
        else:
            cmap='jet'
        fig=plt.figure(figsize=(10,10))
        gs=fig.add_gridspec(4,4,hspace=0.3)
        corregido=self.corregido
        #AGREGAR -800 PARA Q LA MASCARA SEA IGUAL AL CORREGIDO
        no_corregido=self.no_corregido.where(corregido>-800)
        #CAMBIAR PROMEDIOS A SUMAS EN CASO DE PRECIPITACION
        if self.acu==True:
            dc=corregido.resample(time='Q-FEB').sum('time',skipna=False).groupby('time.season').mean('time')
            dm=no_corregido.resample(time='Q-FEB').sum('time',skipna=False).groupby('time.season').mean('time')
            vmin=0
            vmax=dc.max().values
        else:
            dc=corregido.groupby('time.season').mean('time')
            dm=no_corregido.groupby('time.season').mean('time')
            vmin=dc.min().values
            vmax=dc.max().values
        cols=range(4)
        rows=range(2)
        seasons=['DJF','MAM','JJA','SON']
        for row,dat,datname in zip(rows,[dc,dm],['corregido','no-corregido']):
            for col,season in zip(cols,seasons):
                ax=fig.add_subplot(gs[row,col])
                dato=dat.sel(season=season).plot(ax=ax,vmin=vmin,vmax=vmax,cmap=cmap,add_colorbar=False)
                if datname=='corregido':
                    ax.set_title(season)
                else:
                    ax.set_title('')
                if season=='DJF':
                    ax.set_ylabel(datname)
                else:
                    ax.set_ylabel('')
                ax.set_xlabel('')
        cbar_ax1 = fig.add_axes([0.93, 0.52, 0.02, 0.36])
        cbar1=fig.colorbar(dato,cax=cbar_ax1)
        #--------------------------------------------------------------------
        if self.acu==True:
            dc=corregido.groupby('time.year').sum('time',skipna=False).mean(dim=['lat','lon'])
            dm=no_corregido.groupby('time.year').sum('time',skipna=False).mean(dim=['lat','lon'])
        else:
            dc=corregido.groupby('time.year').mean('time').mean(dim=['lat','lon'])
            dm=no_corregido.groupby('time.year').mean('time').mean(dim=['lat','lon'])
        ax=fig.add_subplot(gs[2,:2])
        dc.plot(ax=ax)
        dm.plot(ax=ax)
        ax.set_title('Serie anual')
        ax.set_xlabel('')
        #------------------------------------------------------------------------
        if self.acu==True:
            dc=corregido.resample(time='MS').sum('time',skipna=False).groupby('time.month').mean('time').mean(dim=['lat','lon'])
            dm=no_corregido.resample(time='MS').sum('time',skipna=False).groupby('time.month').mean('time').mean(dim=['lat','lon'])
        else:
            dc=corregido.groupby('time.month').mean('time').mean(dim=['lat','lon'])
            dm=no_corregido.groupby('time.month').mean('time').mean(dim=['lat','lon'])
        ax=fig.add_subplot(gs[3,:2])
        dc.plot(ax=ax)
        dm.plot(ax=ax)
        ax.set_title('Ciclo anual')
        plt.legend(['corr','no-corr'])
        #-----------------------------------------------------------------------
        if self.acu==True:
            dc=corregido.groupby('time.year').sum('time',skipna=False).mean('year')
            dm=no_corregido.groupby('time.year').sum('time',skipna=False).mean('year')
            vmin=0
            vmax=dc.max().values
        else:
            dc=corregido.groupby('time.year').mean('time').mean('year')
            dm=no_corregido.groupby('time.year').mean('time').mean('year')
            vmin=dc.min().values
            vmax=dc.max().values
        for col,dat,datname in zip([2,3],[dc,dm],['corregido_anual','no-corregido_anual']):
            ax=fig.add_subplot(gs[2,col])
            dato=dat.plot(ax=ax,vmin=vmin,vmax=vmax,cmap=cmap,add_colorbar=False)
            ax.set_title(datname)
            ax.set_ylabel('')
            ax.set_xlabel('')
        cbar_ax2 = fig.add_axes([0.93, 0.32, 0.02, 0.16])
        cbar2=fig.colorbar(dato,cax=cbar_ax2)
        #-------------------------------------------------------------------
        ax=fig.add_subplot(gs[3,2])
        sns.distplot(np.ndarray.flatten(dc.values),kde=False,bins=15,ax=ax)
        sns.distplot(np.ndarray.flatten(dm.values),kde=False,bins=15,ax=ax)
        ax.set_title('Distribucion espacial anual')
        #---------------------------------TABLA----------------------------------
        if self.acu==True:
            y_cor=corregido.groupby('time.year').sum('time',skipna=False).mean(dim=['lat','lon']).values.reshape(-1, 1)
            y_mod=no_corregido.groupby('time.year').sum('time',skipna=False).mean(dim=['lat','lon']).values.reshape(-1, 1)
        else:
            y_cor=corregido.groupby('time.year').mean('time').mean(dim=['lat','lon']).values.reshape(-1, 1)
            y_mod=no_corregido.groupby('time.year').mean('time').mean(dim=['lat','lon']).values.reshape(-1, 1)
        x=np.arange(1,len(y_cor)+1).reshape(-1,1)
        reg_cor=LinearRegression().fit(x,y_cor)
        reg_mod=LinearRegression().fit(x,y_mod)
        #_-----------------------
        ax=fig.add_subplot(gs[3,3])
        col_labels = ['Cor','no_Cor']
        row_labels = ['Tenden.','Prom.','Max','Min','SD']
        table_vals = [[reg_cor.coef_[0][0],reg_mod.coef_[0][0]],
                      [dc.mean().values,dm.mean().values],
                      [dc.max().values,dm.max().values],
                      [dc.min().values,dm.min().values],
                      [dc.std().values,dm.std().values]]
        table_vals2 = [['%.2f' % j for j in i] for i in table_vals]


        the_table = ax.table(cellText=table_vals2,
                              colWidths=[0.05] * 3,
                              rowLabels=row_labels,
                              colLabels=col_labels,
                              loc='center right',cellLoc='center')
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(10)
        the_table.scale(7, 1.6)
        ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        ax.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
        ax.set_title('resumen anual')
        for pos in ['right','top','bottom','left']:
            ax.spines[pos].set_visible(False)
        plt.close(fig)
        return fig
