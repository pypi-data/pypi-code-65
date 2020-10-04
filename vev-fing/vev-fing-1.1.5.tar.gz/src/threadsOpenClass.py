from PyQt5.QtCore import QObject,QRunnable,pyqtSignal,pyqtSlot

from src.ReadData import readData,keepValidPositions
from src.GetEntropy import getEntropyExperiment, getEntropyExperimentAminos
import os
import pandas as pd

import os
pathPip=str(os.path.dirname(pd.__file__)).split('pandas')[0]


path_pkl = pathPip+'src/data_experiments/' #también a cambiar

class loadSignals(QObject):

    finished = pyqtSignal(list)
    error = pyqtSignal(object)


class LoadFolder(QRunnable):

    def __init__(self,filename,fvp,lvp):
        super(LoadFolder, self).__init__()
        self.filename = filename
        self.fvp = fvp
        self.lvp = lvp
        self.signals = loadSignals()


    @pyqtSlot()
    def run(self):

        try:

            fileName = self.filename + '/'
            parameters = [fileName, self.fvp, self.lvp]
            df,strain,repetition,self.lvp = readData(parameters)

            experimentName = strain + '_' + repetition + '(' + str(self.fvp) + '-' + str(self.lvp) + ').parquet'
            entropyName = strain + '_' + repetition + '(' + str(self.fvp) + '-' + str(self.lvp) + ')_entropy.parquet'
            df.to_parquet(path_pkl + experimentName)
            dfAux = getEntropyExperiment(strain, repetition, self.fvp, self.lvp, df)
            dfAux.to_parquet(path_pkl + entropyName)


        except Exception as e:
            self.signals.error.emit(e)

        finally:
            self.signals.finished.emit([strain, repetition, self.fvp, self.lvp, True])  # Done

class LoadFile(QRunnable):

    def __init__(self,filename):
        super(LoadFile, self).__init__()
        self.filename = filename
        self.signals = loadSignals()
        self.fvp = 0
        self.lvp = 0
    @pyqtSlot()
    def run(self):

        try:
            fileName = self.filename
            auxSplit = fileName.split('/')
            cantidad = len(auxSplit)
            print(cantidad)
            i = 0
            directorio = ''
            while i < (cantidad - 1):
                if i == 0:
                    directorio = auxSplit[i]
                else:
                    directorio = str(directorio) + '/' + str(auxSplit[i])
                i = i + 1
            directorio = str(directorio) + '/'
            archivo = auxSplit[cantidad - 1]

            aux = str(os.getcwd()) + '/' + path_pkl
            archivoAux = archivo.split('.')[0]
            strain_repetion = archivoAux.split('_')
            strain = strain_repetion[0]
            auxSplit = strain_repetion[1].split('(')
            repetition = auxSplit[0]
            aux_fvp_lvp = auxSplit[1].split('-')
            self.fvp = int(aux_fvp_lvp[0])
            self.lvp = int(aux_fvp_lvp[1].split(')')[0])
            if "entropy" not in archivo:
                aux_name_entroy = archivoAux + '_entropy.parquet'
                print(aux_name_entroy)
                if os.path.exists(directorio + aux_name_entroy):
                    if aux != directorio:
                        df = pd.read_parquet(directorio + archivo)
                        df.to_parquet(path_pkl + archivo)
                        df = pd.read_parquet(directorio + aux_name_entroy)
                        df.to_parquet(path_pkl + aux_name_entroy)
                else:
                    if aux != directorio:
                        df = pd.read_parquet(directorio + archivo)
                        df.to_parquet(path_pkl + archivo)
                        df = getEntropyExperiment(strain, repetition, self.fvp, self.lvp, df)
                        df.to_parquet(path_pkl + aux_name_entroy)
                    else:
                        df = pd.read_parquet(directorio + archivo)
                        df = getEntropyExperiment(os.getcwd(), strain, repetition, self.fvp, self.lvp, df)
                        df.to_parquet(path_pkl + aux_name_entroy)
            else:
                if aux != directorio:
                    auxExperiment = archivo.replace('_entropy.parquet', '.parquet')
                    if os.path.exists(directorio + auxExperiment):
                        df = pd.read_parquet(directorio + auxExperiment)
                        df.to_parquet(path_pkl + auxExperiment)
                    df = pd.read_parquet(directorio + archivo)
                    df.to_parquet(path_pkl + archivo)


        except Exception as e:
            print(e)
            self.signals.error.emit()

        finally:
            self.signals.finished.emit([strain, repetition, self.fvp, self.lvp, False])  # Done