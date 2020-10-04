import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


dfPlot = ''

class FigureCD(FigureCanvas):

    def __init__(self,dfResult,df,th, parent,width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.parent = parent
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.dfResult = dfResult
        self.df = df
        self.th = th
        self.fig = fig
        self.auxInfo = []
        self.array = []
        self.compute_initial_figure()
        self._flag = False


    def updateCD(self,dfR,df,th):
        self.dfResult=dfR
        self.th = th
        self.df = df
        self.auxInfo = []
        self.array = []
        self.axes.cla()
        self.compute_initial_figure()


    def compute_initial_figure(self):
        passages = self.df['Passage'].unique()
        for pos in self.dfResult['Position']:
            maxF_Cod = self.dfResult.loc[self.dfResult['Position'] == pos].MaxFreqCodon.astype(str)
            freqEvol = self.df.loc[self.df['Position'] == pos]
            freqEvol = freqEvol[maxF_Cod.astype(str)]
            freqEvol = np.array(freqEvol)
            if (np.amin(freqEvol) < self.th):
                str_label = str(pos) + ' - ' + str(maxF_Cod.values.item())
                self.auxInfo.append(str_label)
                aux =self.axes.plot(passages, freqEvol)
                self.array.append(aux)
        self.axes.set_xlabel('Passages')
        self.axes.set_ylabel('Frequencies')

        self.annot = self.axes.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))

        self.annot.set_visible(False)
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)
        self.axes.legend()
        self.draw()



    def update_annot(self,x,y,i):

        #pos = self.array[i][0].get_offsets()[ind["ind"][0]]
        self.annot.xy = (x,y)
        self.annot.set_text(self.auxInfo[i])
        self.annot.get_bbox_patch().set_alpha(0.4)



    def hover(self,event):
        vis = self.annot.get_visible()
        if event.inaxes == self.axes:
            cont = False
            i = 0
            while not cont and i < len(self.array):
                line = self.array[i][0]

                cont, ind = line.contains(event)
                i = i +1
            if cont:
                self.update_annot(event.xdata,event.ydata,(i-1))

                self.annot.set_visible(True)
                self.fig.canvas.draw_idle()

            else:
                if vis:
                    self.annot.set_visible(False)
                    self.fig.canvas.draw_idle()
