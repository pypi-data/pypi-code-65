from PyQt5.QtCore import QObject,QRunnable,pyqtSignal,pyqtSlot
import pandas as pd
from src.GetEntropySurface import getEntropySurface
from src.PlotEntropyPosition import plotEntropyPosition
from src.calculateGumbel import gumbelPlot
from src.PlotPopularDecay import plotPopularDecay

import os
pathPip=str(os.path.dirname(pd.__file__)).split('pandas')[0]

path_pkl =pathPip+ 'src/data_experiments/'

class plotSignals(QObject):

    finished = pyqtSignal(list)
    error = pyqtSignal(object)

class plotSurface(QRunnable):

    def __init__(self,strain,repetition,fvp,lvp):
        super(plotSurface, self).__init__()
        self.strain = strain
        self.repetition = repetition
        self.fvp = fvp
        self.lvp = lvp
        self.signals = plotSignals()
    @pyqtSlot()
    def run(self):
        try:
            experimentName = self.strain + '_' + self.repetition + '(' + self.fvp + '-' + self.lvp + ')_entropy.parquet'
            df = pd.read_parquet(path_pkl + experimentName)
            getEntropySurface(df, self.strain, self.repetition)
        except Exception as e:
            self.signals.error.emit(e)
        finally:
            self.signals.finished.emit([self.strain,self.repetition,self.fvp,self.lvp])


class plotPositionEntropy(QRunnable):

    def __init__(self,strain,repetition,position,fvp,lvp):
        super(plotPositionEntropy, self).__init__()
        self.strain = strain
        self.repetition = repetition
        self.fvp = fvp
        self.lvp = lvp
        self.position = position
        self.signals = plotSignals()

    @pyqtSlot()
    def run(self):
        try:
            intposition = int(self.position)
            experimentName = self.strain + '_' + self.repetition + '(' + self.fvp + '-' + self.lvp + ')_entropy.parquet'
            df = pd.read_parquet(path_pkl + experimentName)
            plotEntropyPosition(intposition, df, self.strain, self.repetition, 'red')
        except:
            self.signals.error.emit("Please Select an Integer Position")
        finally:
            self.signals.finished.emit([self.strain,self.repetition,self.position,self.fvp,self.lvp])

class plotGumbel(QRunnable):
    def __init__(self,strain,repetition,fvp,lvp):
        super(plotGumbel, self).__init__()
        self.strain = strain
        self.repetition = repetition
        self.fvp = fvp
        self.lvp = lvp
        self.signals = plotSignals()

    @pyqtSlot()
    def run(self):
        try:
            experimentName = self.strain + '_' + self.repetition + '(' + self.fvp + '-' + self.lvp + ')_entropy.parquet'
            df = pd.read_parquet(path_pkl + experimentName)
            gumbelPlot(df,self.strain,self.repetition)
        except:
            self.signals.error.emit("ERROR")
        finally:
            self.signals.finished.emit([self.strain,self.repetition,self.fvp,self.lvp])


class codonDecay(QRunnable):
    def __init__(self,strain,repetition,th,fvp,lvp):
        super(codonDecay, self).__init__()
        self.strain = strain
        self.repetition = repetition
        self.th = th
        self.fvp = fvp
        self.lvp = lvp
        self.signals = plotSignals()

    @pyqtSlot()
    def run(self):
        try:
            experimentName = self.strain + '_' + self.repetition + '(' + self.fvp + '-' + self.lvp + ').parquet'
            df = pd.read_parquet(path_pkl + experimentName)
            dfReturn=plotPopularDecay(df,)
        except:
            self.signals.error.emit("ERROR")
        finally:
            self.signals.finished.emit([dfReturn,df,self.th,self.strain,self.repetition,self.fvp,self.lvp])