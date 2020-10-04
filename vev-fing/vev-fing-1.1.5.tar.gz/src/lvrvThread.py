from PyQt5.QtCore import QObject,QRunnable,pyqtSignal,pyqtSlot
from src.Filtrados import descomposicion_Poly_LV_RV,movingAverage_1D,movingAverage,descomposicion_PM_LV_RV

class lvrvSignals(QObject):

    finished = pyqtSignal(list)
    error = pyqtSignal()


class lvrv_poly(QRunnable):
    def __init__(self,parameters,grade,nameExps):
        super(lvrv_poly, self).__init__()
        self.experiments = parameters
        self.grade = grade
        self.nameExps = nameExps
        self.signals = lvrvSignals()



    @pyqtSlot()
    def run(self):
        try:
            l_LV_RV = []

            for df in self.experiments:
                descomposicion = descomposicion_Poly_LV_RV(df,self.grade)
                l_LV_RV.append(descomposicion)

        except Exception as e:

            print(e)

            self.signals.Error.emit()


        finally:
            self.signals.finished.emit([l_LV_RV,'Polynomial',self.nameExps,self.grade])  # Done


class lvrv_average(QRunnable):
    def __init__(self,parameters,window,nameExps):
        super(lvrv_average, self).__init__()
        self.experiments = parameters
        self.window = window
        self.nameExps = nameExps
        self.signals = lvrvSignals()


    @pyqtSlot()
    def run(self):
        try:
            l_LV_RV = []
            for df in self.experiments:
                descomposicion = descomposicion_PM_LV_RV(df,self.window)
                l_LV_RV.append(descomposicion)
        except Exception as e:
            print(e)
            self.signals.error.emit()
        finally:
            self.signals.finished.emit([l_LV_RV,'Moving Average',self.nameExps,self.window])  # Done