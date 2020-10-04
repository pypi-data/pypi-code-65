from PyQt5.QtCore import QObject,QRunnable,pyqtSignal,pyqtSlot
from src.TSNE_exp import tsnePassages,tsnePositions

class tsneSignals(QObject):

    finished = pyqtSignal(list)
    error = pyqtSignal()


class tsneProcess(QRunnable):

    def __init__(self,parameters,tsneType,nameExp):
        super(tsneProcess, self).__init__()
        self.data = parameters
        self.type = tsneType
        self.signals = tsneSignals()
        self.nameExp = nameExp


    @pyqtSlot()
    def run(self):

        try:
            if self.type == 'Passages':
                df = tsnePassages(self.data)
            else:
                df = tsnePositions(self.data)


        except Exception as e:
            print (e)
            self.signals.error.emit()

        finally:
            self.signals.finished.emit([self.data,df,self.type,self.nameExp])  # Done


class tsneProcessUpdate(QRunnable):
#dfs,perp,lr,data,"Passages",nameExps
    def __init__(self,parameters,perp,lr,oldData,tsneType,nameExp):
        super(tsneProcessUpdate, self).__init__()
        self.data = parameters
        self.type = type
        self.signals = tsneSignals()
        self.lr = lr
        self.perp = perp
        self.oldData = oldData
        self.type = tsneType
        self.nameExp = nameExp


    @pyqtSlot()
    def run(self):
        try:
            if self.type == 'Passages':
                df = tsnePassages(self.data,[self.perp],[self.lr],self.oldData)
            else:
                df = tsnePositions(self.data, [self.perp], [self.lr], self.oldData)


        except Exception as e:
            print(e)
            self.signals.error.emit()

        finally:
            self.signals.finished.emit([df,self.perp,self.lr,self.type,self.nameExp])  # Done