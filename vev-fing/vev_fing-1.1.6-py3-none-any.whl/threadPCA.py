from PyQt5.QtCore import QObject,QRunnable,pyqtSignal,pyqtSlot
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

class pcaSignals(QObject):

    finished = pyqtSignal(list)
    error = pyqtSignal()


class pcaProcess(QRunnable):

    def __init__(self,parameters,nameExp):
        super(pcaProcess, self).__init__()
        self.dfs = parameters
        self.nameExp = nameExp
        self.signals = pcaSignals()

    @pyqtSlot()
    def run(self):

        try:

            arrayDF=[]
            infoDF =[]
            strainDF = []
            repDF = []
            dfPuntosPCA=pd.DataFrame(columns=["PCA_1", "PCA_2", "Strain", "Repetition"])

            for df in self.dfs:

                arrayDF.append(df['Entropy'])
                infoDF.append(df['info'])

                info_df=str(df['info'].iloc[0])
                strain_df=info_df.split(',')[0]
                repet=info_df.split(',')[1]
                strainDF.append(strain_df)
                repDF.append(repet)



            X = np.squeeze(np.array([arrayDF]))
            infoDF = np.squeeze(np.array([infoDF]))
            pca = PCA(n_components=2)
            auxReturn = pca.fit_transform(X)
            pcaVector = pca.components_

            dfPuntosPCA['PCA_1']=auxReturn[:,0]
            dfPuntosPCA['PCA_2']=auxReturn[:,1]
            dfPuntosPCA['Strain']=strainDF
            dfPuntosPCA['Repetition']=repDF



        except Exception as e:
            print (e)
            self.signals.error.emit()

        finally:

            self.signals.finished.emit([dfPuntosPCA,pcaVector,infoDF, self.nameExp,self.dfs])  # Done
