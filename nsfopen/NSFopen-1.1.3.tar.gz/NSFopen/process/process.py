# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 15:13:47 2020

@author: Edward
"""

from NSFopen.read import read
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from matplotlib import cm
import pandas as pd
import scipy.stats as ss

class process():
    def __init__(self, filename):
        afm = read(filename, verbose=False)
        self.data = afm.data
        # self.processed = afm.data.copy()
        self.param = afm.param

    def flatten(self, order=1, direction='Forward', channel='Z-Axis', mask=[]):
        data_out = self.data['Image'][direction][channel]
        data_in = data_out.copy()
        x = np.arange(np.shape(data_in)[1])

        if np.any(mask):
            data_in[mask] = np.nan
        for idx, (out, line) in enumerate(zip(data_out, data_in)):
            ix = np.isfinite(line)
            p = np.polyfit(x[ix], line[ix], order)
            y = np.polyval(p, x)
            data_out[idx] = out - y
        self.data['Image'][direction][channel] = data_out

    def image(self,
              direction='Forward',
              channel='Z-Axis',
              scale=1e9,
              cmap=cm.afmhot,
              cbar=[],
              fontsize=10,
              scalebar=False):

        d = self.data['Image'][direction][channel]*scale
        x = self.param.X.range[0] * 1e6
        y = self.param.Y.range[0] * 1e6
        print(y)

        plt.imshow(d, extent=(0, x, 0, y), cmap=cmap, origin='lowerleft')

        if scalebar:
            if isinstance(scalebar,dict):
                dx = scalebar['length']
                c = scalebar['color']
            else:
                dx = np.round(x / 5)
                c = 'k'

            pad = y * 0.05
            plt.plot([x - dx - pad, x - pad], [pad, pad], linewidth=5, color=c)
            plt.text(x - pad - dx / 2, pad + x * 0.03, f'%i $\mu$m' % dx,
                     horizontalalignment='center',
                     fontsize=fontsize,
                     color=c)
            plt.xticks([])
            plt.yticks([])
        else:
            plt.xlabel('$[\mu{}$m]', fontsize=fontsize)
            plt.ylabel('$[\mu{}$m]', fontsize=fontsize)
            plt.xticks(fontsize=fontsize)
            plt.yticks(fontsize=fontsize)
        plt.title(f'{channel} - {direction}',fontsize=fontsize)
        if cbar:
            cb = plt.colorbar(pad=0.02)
            cb.set_label(label=cbar,size=fontsize)
            cb.ax.tick_params(labelsize=fontsize)

    # def surf(self,
    #          direction='Forward',
    #          channel='Z-Axis',
    #          scale=1e9,
    #          cmap = cm.afmhot,
    #          cbar = [],
    #          fontsize = 10):

    #     Z = self.data['Image'][direction][channel]*scale
    #     xx = self.param.X.range[0] * 1e6
    #     yy = self.param.Y.range[0] * 1e6
    #     X = np.linspace(0,xx,np.shape(Z)[0])
    #     Y = np.linspace(0,yy,np.shape(Z)[1])
    #     X, Y = np.meshgrid(X,Y)

    #     fig = plt.figure()
    #     ax = fig.gca(projection='3d')
    #     ax.set_proj_type('ortho')
    #     surf = ax.plot_surface(X, Y, Z,
    #                            cmap=cmap,
    #                            linewidth=0,
    #                            antialiased=False)

    #     ax.set_xlabel('$[\mu{}$m]', fontsize=fontsize)
    #     ax.set_ylabel('$[\mu{}$m]', fontsize=fontsize)
    #     ax.view_init(elev=45., azim=32)
    #     ax.set_frame_on(False)
    #     ax.grid(False)
    #     ax.xaxis.pane.fill=False
    #     ax.yaxis.pane.fill=False
    #     ax.zaxis.pane.fill=False
    #     if cbar:
    #         cb = plt.colorbar(surf,pad=0.02, shrink=0.5, aspect=10)
    #         cb.set_label(label=cbar,size=fontsize)
    #         cb.ax.tick_params(labelsize=fontsize)
    #         ax.set_zticks([])

    #     else:
    #         ax.set_zlabel('',fontsize=fontsize)


    def stats(self):
        def mad(x):
            return np.mean(np.abs(x-x.mean()))

        stat=[]
        names=[]
        s0, s1, s2, s3 = [], [], [], []
        for d, df in self.data['Image'].groupby(level=0):


            names.append(d)
            s0.append(df[d].apply(lambda x: mad(x)))
            s1.append(df[d].apply(np.std))
            s2.append(df[d].apply(lambda x: ss.skew(x,axis=None)))
            s3.append(df[d].apply(lambda x: ss.kurtosis(x,axis=None)))

        snames=['Sa','Sq','Skew','Kurtosis']
        s = [s0, s1, s2, s3]
        return pd.DataFrame(data=s,columns=names,index=snames)



if __name__ == "__main__":
    file = "test.nid"
    afm=process(file)


    afm.flatten(channel='Z-Axis Sensor')
    afm.image(cbar='[nm]',channel='Z-Axis Sensor',scalebar=True,scale=1e9)
    # plt.clim(-100,50)
    plt.show()
    rms = afm.stats().Forward.Sa['Z-Axis Sensor']
    z = afm.data.Image.Forward['Z-Axis Sensor']
    mask = z>2*rms
    afm.flatten(channel='Z-Axis Sensor',mask=mask)
    afm.image(cbar='[nm]',channel='Z-Axis Sensor',scalebar=True,scale=1e9)
    # plt.clim(-100,50)
    plt.show()

    print(rms)

    # {'a': row.mod() for row in afm.data.Image.Forward}
