from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QFileDialog, QLabel, QSlider
import sys
from src.ReadData import readData,keepValidPositions
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPixmap, QPalette, QBrush, QImage, QIcon, QMovie
from src.pcaClass import FigurePCA
from src.dialogPositions import valuesPositions
import pandas as pd
from src.dialogInterpolation import dInterpolation
from src.threadsOpenClass import LoadFile, LoadFolder
from src.threadsPlotClass import plotSurface,plotPositionEntropy,plotGumbel, codonDecay
from src.tsneClass import FigureTSNE
from src.tsneThreadProcess import tsneProcess,tsneProcessUpdate
from src.lvrvClass import FigureLVRV
from src.lvrvThread import lvrv_poly,lvrv_average
from src.codonDecayClass import FigureCD
from src.threadPCA import pcaProcess
from datetime import datetime
import logging
import pymongo
import socket
import os
import json
from jsonschema import validate

pathPip=str(os.path.dirname(pymongo.__file__)).split('pymongo')[0]
path_buttons=pathPip+'src/buttons_and_background/'
path_pkl = pathPip+'src/data_experiments/' #también a cambiar
path_grafics=pathPip+'src/plot_images'
path_schemas = pathPip+'src/'
loaded_dfs = []

def dbconnect(mode):
    if mode:
        client = pymongo.MongoClient("mongodb+srv://vevdb:MDp1atkxAv9R2KxZ@cluster0.lu8xi.gcp.mongodb.net/")
        db = client['VEV']
        return db
    else:
        return None





def logger(new,experiment,log):
    logging.info(log)

def getExperiments(ne,nameExps):
    #299_1(774-7332)
    otherexperiments = ''
    for exp in nameExps:
        if ne != exp:
            experiment = exp.split('.')[0]
            otherexperiments =otherexperiments + experiment + ' '
    return otherexperiments


def initLoggin():
    date_time = datetime.now().strftime("%d-%m-%Y")
    logging.basicConfig(filename=pathPip+'src/logs/vev-'+date_time+'.log',format='%(asctime)s %(message)s', level=logging.INFO)
    logging.info('VEV Started')

class Interfaz(QtWidgets.QMainWindow):
    def __init__(self, mode=None):

        super(Interfaz, self).__init__()
        uic.loadUi(pathPip+'src/ui_files/mainwindow.ui', self)
        self._flag = False
        if mode==None:
            self.Online= True
        else:
            self.Online = False
        self.threadpool = QtCore.QThreadPool()
        self.label_lvrv.hide()
        self.input_lvrv.hide()
        self.slidersTSNE = QtWidgets.QVBoxLayout(self.frame_sliders)
        self.arraySliders = []
        initLoggin()
        self.db = dbconnect(self.Online)
        self.namePC = socket.gethostname()
        self.addUser()
        #call functions

        self.buttonCargar_experimento.clicked.connect(self.loadExperiment)
        self.buttonCargarPK.clicked.connect(self.loadExperimentPK)
        self.plotPositionButton.clicked.connect(self.plotPostionFunction)
        self.plotSurfaceButton.clicked.connect(self.plotSurfaceFunction)
        self.codonButton.clicked.connect(self.codonDecayFunction)
        self.PCAButton.clicked.connect(self.pcaFunction)
        self.tsneButton.clicked.connect(self.tsneFunctions)
        self.buttonInterpolation.clicked.connect(self.interpolateFunction)
        self.gumbelButton.clicked.connect(self.gumbelWidget)
        self.addPerpLRButton.clicked.connect(self.tsneAddPerpAndLR)
        self.mvAverage.toggled.connect(lambda: self.changeLabel(self.mvAverage))
        self.poly.toggled.connect(lambda: self.changeLabel(self.poly))
        self.lvrv_button.clicked.connect(self.lvrvFunction)

        #exports functions
        self.exportCSVTSNE.clicked.connect(self.exportTSNE)
        self.importCSVTSNE.clicked.connect(self.importTSNE)
        self.exportCSVLVRV.clicked.connect(self.exportLVRV)
        self.ImportCSVLVRV.clicked.connect(self.importLVRV)
        self.ExportCSVPCA.clicked.connect(self.exportPCA)
        self.ImportCSVPCA.clicked.connect(self.importPCA)

        # Move stacked widgets

        self.stackedWidget.setCurrentIndex(0)  # main
        self.buttonplotposition.clicked.connect(self.entropyPosition)
        self.buttonEntropySurface.clicked.connect(self.entropySurface)
        self.buttonCodonDecay.clicked.connect(self.codonDecayWidget)
        self.buttonPCAFunction.clicked.connect(self.pcaWidget)
        self.buttonTsne.clicked.connect(self.tsne)
        self.plotGumbelButton.clicked.connect(self.gumbelFunction)
        self.buttonLVRV.clicked.connect(self.LVRV)

        # style
        self.setMinimumSize(1000, 568)
        self.setWindowIcon(QIcon(path_buttons+'ImageICON.jpg'))
        self.buttonCargar_experimento.setStyleSheet("QPushButton{border-image:url("+path_buttons+"Load Folder.png);}")
        self.buttonCargar_experimento.setToolTip("Click this button to open experiment folder")
        self.buttonCargarPK.setStyleSheet("QPushButton{border-image:url(" + path_buttons + "Load File.png);}")
        self.buttonCargarPK.setToolTip("Click this button to open experiment file")
        self.buttonLVRV.setStyleSheet("QPushButton{border-image:url(" + path_buttons + "LVRV.png);}")
        self.buttonLVRV.setToolTip("Plot Leading Variations and Random Variations")
        self.buttonplotposition.setStyleSheet("QPushButton{border-image:url(" + path_buttons + "Plot Entropy x Position.png);}")
        self.buttonplotposition.setToolTip("Plot Entropy times position")
        self.buttonEntropySurface.setStyleSheet("QPushButton{border-image:url(" + path_buttons + "Plot Entropy Surface.png);}")
        self.buttonEntropySurface.setToolTip("Plot Entropy Surface of an experiment")
        self.buttonCodonDecay.setStyleSheet("QPushButton{border-image:url(" + path_buttons + "Codon Decay.png);}")
        self.buttonCodonDecay.setToolTip("Plot Codon Decay of an experiment")
        self.buttonPCAFunction.setStyleSheet("QPushButton{border-image:url(" + path_buttons + "PCA.png);}")
        self.buttonPCAFunction.setToolTip("Plot PCA")
        self.gumbelButton.setStyleSheet("QPushButton{border-image:url(" + path_buttons + "Gumbel.png);}")
        self.gumbelButton.setToolTip("Plot Gumbel distribution")
        self.buttonTsne.setStyleSheet("QPushButton{border-image:url(" + path_buttons + "t-SNE.png);}")
        self.buttonTsne.setToolTip("Enter to t-SNE plot options")
        self.buttonInterpolation.setStyleSheet("QPushButton{border-image:url(" + path_buttons + "Interpolation.png);}")
        self.buttonInterpolation.setToolTip("Interpolate experiment data")

        #TABLE VIEW MODELS##
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Experiment '])
        self.tableView_PlotPostion.setModel(self.model)
        self.tableView_PlotPostion.horizontalHeader().setSectionResizeMode(1)
        self.tableTSNE.setModel(self.model)
        self.tableTSNE.horizontalHeader().setSectionResizeMode(1)
        self.tablePCA.setModel(self.model)
        self.tablePCA.horizontalHeader().setSectionResizeMode(1)
        self.tableViewCodon.setModel(self.model)
        self.tableViewCodon.horizontalHeader().setSectionResizeMode(1)
        self.tableViewEntropySurface.setModel(self.model)
        self.tableViewEntropySurface.horizontalHeader().setSectionResizeMode(1)
        self.tableViewGumbel.setModel(self.model)
        self.tableViewGumbel.horizontalHeader().setSectionResizeMode(1)
        self.tableLVRV.setModel(self.model)
        self.tableLVRV.horizontalHeader().setSectionResizeMode(1)
        #Sliders
        self.perplexitySlider.setMaximum(3)
        self.perplexitySlider.setMinimum(0)
        self.lrSlider.setMaximum(3)
        self.lrSlider.setMinimum(0)

        self.perplexitySlider.valueChanged.connect(self.updateTSNE)
        self.lrSlider.valueChanged.connect(self.updateTSNE)
        #FIGURES
        self.pca=None
        self.tsne=None
        self.lvrv=None
        self.condonDecay=None
        #AUXILIAR
        self.perAux=[3,6,12,15]
        self.lrAux=[10,100,300,500]
        self.movie = QMovie(path_buttons+'Loading.gif')

    def scale_image(self,size):
        imageBack = QImage(path_buttons+'background.png')
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(imageBack))
        self.setPalette(palette)

    def resizeEvent(self, e):
        if not self._flag:
            self._flag = True
            self.scale_image(e.size())
            QtCore.QTimer.singleShot(30, lambda: setattr(self, "_flag", False))
        super().resizeEvent(e)

#CHANGE LABEL
    def changeLabel(self, b): #b is the radio button
        self.label_lvrv.show()
        self.input_lvrv.show()
        if b.text() == "Moving Average":
            if b.isChecked() == True:
                self.label_lvrv.setText("Select Average Window:")
            else:
                self.label_lvrv.setText("Select Polynomial Grade:")

        else:
            if b.isChecked() == True:
                self.label_lvrv.setText("Select Polynomial Grade:")
            else:
                self.label_lvrv.setText("Select Average Window:")
#Load FILES AND FOLDERS

    def loadExperiment(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.DontUseCustomDirectoryIcons
        fileName = QFileDialog.getExistingDirectory(self, directory=os.getcwd(),caption='Select a directory', options=options)
        if fileName != "":
            vp = valuesPositions()
            vp.exec()
            fvp = vp.getFVP()
            lvp = vp.getLVP()
            setIt= vp.getIfSet()
            if setIt:
                thread = LoadFolder(fileName,fvp,lvp)
                thread.signals.error.connect(self.openError)
                thread.signals.finished.connect(self.openOK)
                self.threadpool.start(thread)
            else:
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage('Error: Parameters was not correctly selected')
                error_dialog.exec()

    def loadExperimentPK(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.DontUseCustomDirectoryIcons
        (fileName, aux) = QFileDialog.getOpenFileName(self,directory=path_pkl, caption='Select a .parquet File', filter='*.parquet',options=options)
        if fileName != "":
            thread = LoadFile(fileName)
            thread.signals.error.connect(self.openError)
            thread.signals.finished.connect(self.openOK)
            self.threadpool.start(thread)

# Complete or Errors with open

    def openOK(self,parameters):
        print (parameters)
        strain = parameters[0]
        repetition = parameters[1]
        fvp = parameters[2]
        lvp = parameters[3]
        control = parameters[4]
        if (strain, repetition, fvp, lvp) in loaded_dfs:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('This experiment is already loaded')
            error_dialog.exec()
        else:
            loaded_dfs.append((strain, repetition, fvp, lvp))
            experimentName = "Strain: " + strain + " " + "Repetition: " + repetition
            row = (QStandardItem(experimentName))
            self.model.appendRow(row)
            self.refreshFunction()
            if control:
                nameLog=strain + '_' + repetition + '(' + str(fvp) + '-' + str(lvp) + ').txt'
                log = 'Experiment was loaded and entropy was calculated with First Value Position(FVP) = '+str(fvp)+' and Last Value Position(LVP) = '+str(lvp)
                logger(True,nameLog,log)
                de = QtWidgets.QMessageBox()
                de.setText('Folder: ' + experimentName + ' loaded')
                de.exec()
            else:

                logging.info(' Experiment already calculated was load: '+strain+'_'+repetition+'('+str(fvp)+'-'+str(lvp)+')')


    def openError(self,error):
        error_dialog = QtWidgets.QErrorMessage()
        error_dialog.showMessage(str(error))
        error_dialog.exec()
        logging.info('An error has occurred when an experiment was loaded')


    def refreshFunction(self):
        self.tablePCA.update()
        self.tableViewEntropySurface.update()
        self.tableView_PlotPostion.update()
        self.tableViewCodon.update()
        self.tableTSNE.update()
        self.tableViewGumbel.update()
        self.tableLVRV.update()

    def interpolateFunction(self): #ver posibilidad de hilo
        di = dInterpolation(loaded_dfs)
        di.exec()
        executed, typeInterpolation,strain,repetition,fvp,lvp,passage = di.getInfo()
        if executed:
            nameLog = strain + '_' + repetition + '(' + str(fvp) + '-' + str(lvp) + ').txt'
            log = typeInterpolation + ' interpolation was made for passage number ' +passage
            logger(False, nameLog, log)

    # PLOTS AND LOADS FUNCTIONS


    def tsneAddPerpAndLR(self):
        try:

            perp = int(self.newPerplexity.toPlainText())
            lr   = int(self.newLR.toPlainText())
            if self.tsne == None:
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage('Error: Please plot t-SNE method first')
                error_dialog.exec()
            else:
                dfs,data,nameExps = self.tsne.getData()
                print ("info return from getdata: "+str(nameExps))
                auxType= self.tsne.getType()
                if auxType == 'Passages':
                    thread = tsneProcessUpdate(dfs,perp,lr,data,"Passages",nameExps)
                else:
                    thread = tsneProcessUpdate(dfs,perp,lr,data,"Positions",nameExps)
                thread.signals.error.connect(self.errorTSNEProcess)
                thread.signals.finished.connect(self.okProcessTSNEUpdate)

                self.loading.setMovie(self.movie)
                self.movie.start()
                self.threadpool.start(thread)

        except Exception as e:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Error: Please enter integer values')
            error_dialog.exec()
    def okProcessTSNEUpdate(self,parameters):
        self.movie.stop()
        self.loading.clear()
        data = parameters[0]
        perp = parameters[1]
        lr = parameters[2]
        typeTSNE = parameters[3]
        nameExps = parameters[4]

        self.tsne.updateData(data,perp,lr,nameExps)
        for ne in nameExps:
            otherexperiments = getExperiments(ne,nameExps)
            auxStrain = ne.split("_")
            strain = auxStrain[0]
            auxRep = auxStrain[1].split("(")
            repetition = auxRep[0]
            auxfvp = auxRep[1].split("-")
            fvp = auxfvp[0]
            lvp = auxfvp[1].split(")")[0]
            log = typeTSNE +' t-SNE executed with perplexity = '+str(perp) +' and learning rate = '+ str(lr) + ' with this experiments: '+otherexperiments
            #logger(False, ne, log)
            logging.info(log)
            self.addEntrydb(strain, repetition, fvp, lvp, 't-SNE '+typeTSNE+' with perp='+str(perp)+' and lr='+str(lr), otherexperiments, '')

    def clearLayout(self, layout):
        self.arraySliders=[]
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())
                layout.removeItem(item)

    def addSlidersTSNE(self,strains):
        self.clearLayout(self.slidersTSNE)

        for strain in strains:
            label = QLabel()
            label.setText(str(strain))
            self.slidersTSNE.addWidget(label)
            slid = QSlider(QtCore.Qt.Horizontal)
            slid.setMaximum(1)
            slid.setMinimum(0)
            self.slidersTSNE.addWidget(slid)
            slid.setValue(0)
            slid.valueChanged.connect(self.updateStrainsTSNE)
            self.arraySliders.append([slid,strain])

    def tsneFunctions(self):
        dfsAux = []
        dfs = []
        strains = []
        nameExperiments= []
        indices = self.tableTSNE.selectionModel().selectedRows()
        if len(indices) < 1:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Error: Please select at least one Experiment')
            error_dialog.exec()


        elif (self.rb_passages.isChecked()==False and self.rb_positions.isChecked()==False):
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Error: Please select method type')
            error_dialog.exec()

        else:
            try:
                fvpMayor = 0
                lvpMenor = 0
                for index in sorted(indices):
                    experimentIndex = (index.row())
                    df = loaded_dfs[experimentIndex]
                    strain = str(df[0])
                    if strain not in strains:
                        strains.append(strain)
                    repetition = str(df[1])
                    fvp = df[2]
                    lvp = df[3]
                    if fvpMayor == 0 and lvpMenor == 0:
                        fvpMayor = fvp
                        lvpMenor = lvp
                    else:
                        if fvp > fvpMayor:
                            fvpMayor = fvp
                        if lvp < lvpMenor:
                            lvpMenor = lvp
                    experimentNametxt = strain + '_' + repetition + '(' + str(fvp) + '-' + str(lvp) + ').txt'
                    experimentName = strain + '_' + repetition + '(' + str(fvp) + '-' + str(lvp) + ')_entropy.parquet'
                    dfAux = pd.read_parquet(path_pkl + experimentName)
                    dfsAux.append(dfAux)
                    nameExperiments.append(experimentNametxt)
                for dataFrame in dfsAux:
                    df = keepValidPositions(dataFrame, fvpMayor, lvpMenor)
                    dfs.append(df)

                self.addSlidersTSNE(strains)
                if self.rb_passages.isChecked()==True:
                    auxType = 'Passages'
                else:
                    auxType = 'Positions'
                thread = tsneProcess(dfs,auxType,nameExperiments)
                thread.signals.error.connect(self.errorTSNEProcess)
                thread.signals.finished.connect(self.okProcessTSNE)
                self.loading.setMovie(self.movie)
                self.movie.start()
                self.threadpool.start(thread)
            except Exception as e:
                print (e)
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage('Error')
                error_dialog.exec()

    def errorTSNEProcess(self):
        self.newPerplexity.clear()
        self.newLR.clear()
        self.movie.stop()
        self.loading.clear()
        error_dialog = QtWidgets.QErrorMessage()
        error_dialog.showMessage('Error: An error has occurred when calculated t-SNE')
        error_dialog.exec()
        logging.info('An error has occurred when calculated t-SNE')

    def okProcessTSNE(self,parameters):
        self.newPerplexity.clear()
        self.newLR.clear()
        self.movie.stop()
        self.loading.clear()
        dfs = parameters[0]
        data = parameters[1]
        tsneType = parameters[2]
        nameExp = parameters[3]
        if self.tsne == None:
            boxAux = QtWidgets.QVBoxLayout(self.tsneFrame)
            self.tsne = FigureTSNE(dfs,data,tsneType,nameExp, self.tsneFrame, width=6, height=5, dpi=100)
            boxAux.addWidget(self.tsne)
        else:
            self.perplexitySlider.valueChanged.disconnect()
            self.lrSlider.valueChanged.disconnect()
            self.tsne.newtSNE(dfs,data,tsneType,nameExp)
            self.perplexitySlider.setValue(0)
            self.lrSlider.setValue(0)
            self.perplexity.setText(str(3))
            self.lr.setText(str(10))
            self.perplexitySlider.valueChanged.connect(self.updateTSNE)
            self.lrSlider.valueChanged.connect(self.updateTSNE)
        if tsneType == 'Passages':
            self.perplexitySlider.setMaximum(3)
            self.lrSlider.setMaximum(3)
            self.perAux = [3, 6, 12, 15]
            self.lrAux = [10, 100, 300, 500]
        else:
            self.perplexitySlider.setMaximum(1)
            self.lrSlider.setMaximum(1)
            self.perAux = [3, 12]
            self.lrAux = [10, 300]
        for ne in nameExp:
            auxStrain = ne.split("_")
            strain = auxStrain[0]
            auxRep = auxStrain[1].split("(")
            repetition = auxRep[0]
            auxfvp = auxRep[1].split("-")
            fvp = auxfvp[0]
            lvp = auxfvp[1].split(")")[0]
            otherexperiments = getExperiments(ne,nameExp)
            log = tsneType+' t-SNE executed with this experiments: '+otherexperiments
            #logger(False, ne, log)
            logging.info(log)
            self.addEntrydb(strain, repetition, fvp, lvp, 't-SNE '+tsneType, otherexperiments, '')

    def updateTSNE(self):
        perplexity = self.perAux[self.perplexitySlider.value()]
        lr = self.lrAux[self.lrSlider.value()]
        self.perplexity.setText(str(perplexity))
        self.lr.setText(str(lr))
        if self.tsne==None:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Error: Please before change this, plot t-SNE method')
            error_dialog.exec()
            self.perplexitySlider.valueChanged.disconnect()
            self.lrSlider.valueChanged.disconnect()
            self.perplexitySlider.setValue(0)
            self.lrSlider.setValue(0)
            self.perplexity.setText(str(3))
            self.lr.setText(str(10))
            self.perplexitySlider.valueChanged.connect(self.updateTSNE)
            self.lrSlider.valueChanged.connect(self.updateTSNE)
        else:
            self.tsne.updateParameters(perplexity,lr)

    def getChanges(self):
        changes = []
        for [slider, strain] in self.arraySliders:
            if slider.value() == 1:
                changes.append(strain)
        return changes

    def updateStrainsTSNE(self):
        if self.tsne==None:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Error: Please before change this, plot t-SNE method')
            error_dialog.exec()
        else:
            changes =self.getChanges()
            self.tsne.onOffStrains(changes)

    def pcaFunction(self):  #PASAR PCA A HILOS
        dfsAux = []
        dfs = []
        nameExps = []
        indices = self.tablePCA.selectionModel().selectedRows()

        if len(indices) < 2:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Error: Please select at least two Experiments')
            error_dialog.exec()

        else:
            try:
                fvpMayor = 0
                lvpMenor = 0
                for index in sorted(indices):
                    experimentIndex = (index.row())
                    df = loaded_dfs[experimentIndex]
                    strain = str(df[0])
                    repetition = str(df[1])
                    fvp =df[2]
                    lvp =df[3]
                    if fvpMayor == 0 and lvpMenor ==0:
                        fvpMayor = fvp
                        lvpMenor = lvp
                    else:
                        if fvp > fvpMayor:
                            fvpMayor = fvp
                        if lvp < lvpMenor:
                            lvpMenor = lvp
                    experimentNametxt = strain + '_' + repetition + '(' + str(fvp) + '-' + str(lvp) + ').txt'
                    experimentName = strain + '_' + repetition +'('+str(fvp)+'-'+str(lvp)+ ')_entropy.parquet'
                    dfAux = pd.read_parquet(path_pkl + experimentName)
                    dfsAux.append(dfAux)
                    nameExps.append(experimentNametxt)
                for dataFrame in dfsAux:
                    df =keepValidPositions(dataFrame,fvpMayor,lvpMenor)
                    dfs.append(df)

                thread = pcaProcess(dfs,nameExps)
                thread.signals.error.connect(self.errorPCA)
                thread.signals.finished.connect(self.pcaOK)
                self.loadingPCA.setMovie(self.movie)
                self.movie.start()
                self.threadpool.start(thread)
            except Exception as e:
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage(str(e))
                error_dialog.exec()


    def pcaOK(self,parameters):
        self.movie.stop()
        self.loadingPCA.clear()
        # def __init__(self, dfPuntosPCA, infoDF, pcaVector, nameExps,dfs, parent, width=5, height=4, dpi=100):
        #[dfPuntosPCA,pcaVector,infoDF, self.nameExp,self.data]
        dfPuntosPCA = parameters[0]
        pcaVector = parameters[1]
        infoDF = parameters[2]
        nameExps = parameters[3]
        dfs = parameters[4]
        if self.pca == None:
            boxAux = QtWidgets.QVBoxLayout(self.widget_image)
            self.pca = FigurePCA(dfPuntosPCA,pcaVector,infoDF,nameExps,dfs, self.widget_image, width=6, height=5, dpi=100)
            boxAux.addWidget(self.pca)
        else:
            self.pca.updatePCA(dfPuntosPCA,pcaVector,infoDF,nameExps,dfs)
        for ne in nameExps:
            auxStrain = ne.split("_")
            strain = auxStrain[0]
            auxRep = auxStrain[1].split("(")
            repetition = auxRep[0]
            auxfvp = auxRep[1].split("-")
            fvp = auxfvp[0]
            lvp = auxfvp[1].split(")")[0]
            otherexperiments = getExperiments(ne, nameExps)
            log = 'PCA executed with this experiments ' + otherexperiments
            #logger(False, ne, log)
            logging.info(log)
            self.addEntrydb(strain, repetition, fvp, lvp, 'PCA', otherexperiments, '')

    def errorPCA(self):
        self.movie.stop()
        self.loadingPCA.clear()
        error_dialog = QtWidgets.QErrorMessage()
        error_dialog.showMessage('Error: An error has occurred when calculated PCA')
        error_dialog.exec()
        logging.info('An error has occurred when calculated PCA')

    def codonDecayFunction(self):
        indices = self.tableViewCodon.selectionModel().selectedRows()
        if len(indices) < 1:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Error: Please select at least one Experiment')
            error_dialog.exec()
        elif len(indices) > 1:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Error: Please select only one Experiment')
            error_dialog.exec()
        else:
            try:
                th = self.threshold.toPlainText()
                fth = float(th)
                if fth < 0 or fth >= 1:
                    error_dialog = QtWidgets.QErrorMessage()
                    error_dialog.showMessage('Error: Please select threshold between 0 and 1')
                    error_dialog.exec()
                else:
                    for index in sorted(indices):
                        experimentIndex = (index.row())
                    df = loaded_dfs[experimentIndex]
                    strain = str(df[0])
                    repetition = str(df[1])
                    fvp = str(df[2])
                    lvp = str(df[3])
                    thread = codonDecay(strain, repetition, fth, fvp, lvp)
                    thread.signals.error.connect(self.errorPlotCD)
                    thread.signals.finished.connect(self.codonDecayOK)
                    self.loadingCD.setMovie(self.movie)
                    self.movie.start()
                    self.threadpool.start(thread)
            except Exception as e:
                if e.__class__ == FileNotFoundError:
                    error_dialog = QtWidgets.QErrorMessage()
                    error_dialog.showMessage('Error: Please enter the experiment pkl with frequencies')
                    error_dialog.exec()
                else:
                    error_dialog = QtWidgets.QErrorMessage()
                    error_dialog.showMessage('Error: Please enter an float threshold')
                    error_dialog.exec()


    def errorPlotCD(self):
        self.movie.stop()
        self.loadingCD.clear()
        error_dialog = QtWidgets.QErrorMessage()
        error_dialog.showMessage('Error: An error has occurred when calculated Codon Decay')
        error_dialog.exec()
        logging.info('An error has occurred when calculated Codon Decay')

    def codonDecayOK(self,parameters):
        self.movie.stop()
        self.loadingCD.clear()
        dfResult = parameters[0]
        df = parameters[1]
        th = parameters[2]
        strain = parameters[3]
        repetition = parameters[4]
        fvp = parameters[5]
        lvp = parameters[6]
        if self.condonDecay == None:
            boxAux = QtWidgets.QVBoxLayout(self.codonDecayFrame)
            self.condonDecay = FigureCD(dfResult,df,th, self.codonDecayFrame, width=6, height=5, dpi=100)
            boxAux.addWidget(self.condonDecay)
        else:
            self.condonDecay.updateCD(dfResult,df,th)
        nameLog = strain + '_' + repetition + '(' + str(fvp) + '-' + str(lvp) + ').txt'
        log = 'Codon Decay was plotted with threshold '+str(th)
        # logger(False, ne, log)
        logging.info(log)
        self.addEntrydb(strain, repetition, fvp, lvp, 'Codon Decay', th, '')


    def plotSurfaceFunction(self):
        indices = self.tableViewEntropySurface.selectionModel().selectedRows()
        if len(indices) < 1:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Error: Please select at least one Experiment')
            error_dialog.exec()
        elif len(indices) > 1:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Error: Please select only one Experiment')
            error_dialog.exec()
        else:
            for index in sorted(indices):
                experimentIndex = (index.row())
            df = loaded_dfs[experimentIndex]
            strain = str(df[0])
            repetition = str(df[1])
            fvp = str(df[2])
            lvp = str(df[3])
            thread = plotSurface(strain,repetition, fvp, lvp)
            thread.signals.error.connect(self.errorPlot)
            thread.signals.finished.connect(self.plotSurfaceOK)
            self.loadingPS.setMovie(self.movie)
            self.movie.start()
            self.threadpool.start(thread)


    def plotSurfaceOK(self,parameters):
            self.movie.stop()
            self.loadingPS.clear()
            strain = parameters[0]
            repetition = parameters[1]
            fvp = parameters[2]
            lvp = parameters[3]
            name = path_grafics + '/entropySurface_' + strain + '_' + repetition + '.png'
            pixmap = QPixmap(name)
            #pixmap = pixmap.scaled(700, 700, QtCore.Qt.KeepAspectRatio)
            self.imageSurface.setPixmap(pixmap)
            nameLog = strain + '_' + repetition + '(' + str(fvp) + '-' + str(lvp) + ').txt'
            log = 'Entropy surface is plotted and saved'
            # logger(False, ne, log)
            logging.info(log)
            self.addEntrydb(strain, repetition, fvp, lvp, 'Plot Surface Entropy', '', name)




    def plotPostionFunction(self):
        indices = self.tableView_PlotPostion.selectionModel().selectedRows()
        if len(indices) < 1:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Error: Please select at least one Experiment')
            error_dialog.exec()
        elif len(indices) > 1:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Error: Please select only one Experiment')
            error_dialog.exec()
        else:
            position = self.textEditPosition.toPlainText()
            for index in sorted(indices):
                experimentIndex = (index.row())
            df = loaded_dfs[experimentIndex]
            strain = str(df[0])
            repetition = str(df[1])
            fvp=str(df[2])
            lvp=str(df[3])
            thread = plotPositionEntropy(strain,repetition,position, fvp, lvp)
            thread.signals.error.connect(self.errorPlot)
            thread.signals.finished.connect(self.plotEntropyPositionOK)
            self.loadingPPP.setMovie(self.movie)
            self.movie.start()
            self.threadpool.start(thread)

    def plotEntropyPositionOK(self, parameters):
        self.movie.stop()
        self.loadingPPP.clear()
        strain = parameters[0]
        repetition = parameters[1]
        position = parameters[2]
        fvp = parameters[3]
        lvp = parameters[4]
        name = path_grafics + '/Entropy_' + str(position) + '_' + strain + '_' + repetition + '.png'
        pixmap = QPixmap(name)
        self.plotPositionImage.setPixmap(pixmap)
        nameLog = strain + '_' + repetition + '(' + str(fvp) + '-' + str(lvp) + ').txt'
        log = 'Entropy is plotted and saved for position '+str(position)
        logger(False, nameLog, log)
        self.addEntrydb(strain,repetition,fvp,lvp,'Entropy times Position',position,name)

    def gumbelFunction(self):
        indices = self.tableViewGumbel.selectionModel().selectedRows()
        if len(indices) < 1:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Error: Please select at least one Experiment')
            error_dialog.exec()
        elif len(indices) > 1:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Error: Please select only one Experiment')
            error_dialog.exec()
        else:
            for index in sorted(indices):
                experimentIndex = (index.row())
            df = loaded_dfs[experimentIndex]
            strain = str(df[0])
            repetition = str(df[1])
            fvp = str(df[2])
            lvp = str(df[3])
            thread = plotGumbel(strain, repetition,fvp,lvp)
            thread.signals.error.connect(self.errorPlot)
            thread.signals.finished.connect(self.plotGumbelOK)
            self.loadingGP.setMovie(self.movie)
            self.movie.start()
            self.threadpool.start(thread)



    def plotGumbelOK(self, parameters):
        self.movie.stop()
        self.loadingGP.clear()
        strain = parameters[0]
        repetition = parameters[1]
        fvp=parameters[2]
        lvp = parameters[3]
        name = path_grafics + '/Gumbel'+ '_' + strain + '_' + repetition + '.png'
        pixmap = QPixmap(name)
        self.imageGumbel.setPixmap(pixmap)
        nameLog = strain + '_' + repetition + '(' + str(fvp) + '-' + str(lvp) + ').txt'
        log = 'Gumbel is plotted and saved'
        # logger(False, ne, log)
        logging.info(log)
        self.addEntrydb(strain, repetition, fvp, lvp, 'Gumbel', '', name)

    def errorPlot(self, e):
        self.movie.stop()
        self.loadingGP.clear()
        self.loadingPPP.clear()
        self.loadingPS.clear()
        error_dialog = QtWidgets.QErrorMessage()
        error_dialog.showMessage(str(e))
        error_dialog.exec()
        logging.info('An error has occurred when experiment was plotted')


    def lvrvFunction(self):
        dfsAux = []
        dfs = []
        nameExp = []
        indices = self.tableLVRV.selectionModel().selectedRows()
        if len(indices) < 1:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Error: Please select at least one Experiment')
            error_dialog.exec()


        elif (self.mvAverage.isChecked()==False and self.poly.isChecked()==False ):
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Error: Please select method type')
            error_dialog.exec()

        else:
            try:
                input = self.input_lvrv.toPlainText()
                intInput = int(input)
                fvpMayor = 0
                lvpMenor = 0
                for index in sorted(indices):
                    experimentIndex = (index.row())
                    df = loaded_dfs[experimentIndex]
                    strain = str(df[0])
                    repetition = str(df[1])
                    fvp = df[2]
                    lvp = df[3]
                    if fvpMayor == 0 and lvpMenor == 0:
                        fvpMayor = fvp
                        lvpMenor = lvp
                    else:
                        if fvp > fvpMayor:
                            fvpMayor = fvp
                        if lvp < lvpMenor:
                            lvpMenor = lvp
                    experimentNametxt = strain + '_' + repetition + '(' + str(fvp) + '-' + str(lvp) + ').txt'
                    experimentName = strain + '_' + repetition + '(' + str(fvp) + '-' + str(lvp) + ')_entropy.parquet'
                    dfAux = pd.read_parquet(path_pkl + experimentName)
                    dfsAux.append(dfAux)
                    nameExp.append(experimentNametxt)
                for dataFrame in dfsAux:
                    df = keepValidPositions(dataFrame, fvpMayor, lvpMenor)
                    dfs.append(df)
                if self.mvAverage.isChecked()==True:
                    thread = lvrv_average(dfs,intInput,nameExp)
                    thread.signals.finished.connect(self.lvrvOK)
                    thread.signals.error.connect(self.lvrvError)

                    self.loadingLVRV.setMovie(self.movie)
                    self.movie.start()
                    self.threadpool.start(thread)
                else:
                    thread = lvrv_poly(dfs,intInput,nameExp)
                    thread.signals.finished.connect(self.lvrvOK)
                    thread.signals.error.connect(self.lvrvError)
                    self.threadpool.start(thread)
            except Exception as e:
                print (e)
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage('Error: Please enter an integer')
                error_dialog.exec()

    def lvrvError(self):
        self.movie.stop()
        self.loadingLVRV.clear()
        error_dialog = QtWidgets.QErrorMessage()
        error_dialog.showMessage('Error: An error has occurred when calculated LV-RV')
        error_dialog.exec()
        logging.info('An error has occurred when calculated LV-RV')

    def lvrvOK(self,parameters):
        self.movie.stop()
        self.loadingLVRV.clear()
        dfs = parameters[0]
        typeLVRV = parameters[1]
        nameExps = parameters[2]
        param = parameters[3]
        if self.lvrv == None:
            boxAux = QtWidgets.QVBoxLayout(self.lvrv_frame)
            self.lvrv = FigureLVRV(dfs, self.lvrv_frame,nameExps,typeLVRV,param, width=6, height=5, dpi=100)
            boxAux.addWidget(self.lvrv)
        else:
            self.lvrv.updatelvrv(dfs,nameExps,typeLVRV,param)
        for ne in nameExps:

            auxStrain = ne.split("_")
            strain = auxStrain[0]
            auxRep = auxStrain[1].split("(")
            repetition = auxRep[0]
            auxfvp = auxRep[1].split("-")
            fvp = auxfvp[0]
            lvp = auxfvp[1].split(")")[0]

            otherexperiments = getExperiments(ne,nameExps)

            log = typeLVRV +' LV-RV was plotted with parameter '+str(param)+' with this experiments: '+otherexperiments
            #logger(False, ne, log)
            logging.info(log)
            self.addEntrydb(strain,repetition,fvp,lvp,typeLVRV+' LV-RV',otherexperiments+' with parameter = '+str(param),'')
    # functions for move stackedWidget
    def entropyPosition(self):
        self.stackedWidget.setCurrentIndex(1)  # plotEntropyPosition
    def entropySurface(self):
        self.stackedWidget.setCurrentIndex(2)
    def codonDecayWidget(self):
        self.stackedWidget.setCurrentIndex(4)
    def tsne(self):
        self.stackedWidget.setCurrentIndex(5)
    def pcaWidget(self):
        self.stackedWidget.setCurrentIndex(3)
    def gumbelWidget(self):
        self.stackedWidget.setCurrentIndex(6)

    def LVRV(self):
        self.stackedWidget.setCurrentIndex(7)

    #functions to export

    def exportTSNE(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.DontUseCustomDirectoryIcons
        fileName, _ = QFileDialog.getSaveFileName(self, caption='Save experiment', filter='*.csv',
                                                      options=options)
        if fileName !='':
            if '.csv' not in fileName:
                fileName = fileName.replace('.','') + '.csv'
            if self.tsne == None:
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage('Error: Please Plot t-SNE before export')
                error_dialog.exec()
            else:

                nameExp,normal,lr,perp,tsneType = self.tsne.exportCSV(fileName)
                for ne in nameExp:
                    auxStrain = ne.split("_")
                    strain = auxStrain[0]
                    auxRep = auxStrain[1].split("(")
                    repetition = auxRep[0]
                    auxfvp = auxRep[1].split("-")
                    fvp = auxfvp[0]
                    lvp = auxfvp[1].split(")")[0]
                    otherexperiments = getExperiments(ne, nameExp)
                    if normal:
                        log = tsneType + ' t-SNE executed with this experiments: ' + otherexperiments

                        logging.info(log)
                        self.addEntrydb(strain, repetition, fvp, lvp, 't-SNE '+tsneType, otherexperiments, fileName)
                    else:
                        log = tsneType + ' t-SNE executed with perplexity = ' + str(perp) + ' and learning rate = ' + str(lr) + ' with this experiments: ' + otherexperiments
                        logging.info(log)
                        self.addEntrydb(strain, repetition, fvp, lvp,'t-SNE ' + tsneType + ' with perp=' + str(perp) + ' and lr=' + str(lr), otherexperiments, fileName)


    def importTSNE(self):
        try:
            nameExps = []
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            options |= QFileDialog.DontUseCustomDirectoryIcons
            (fileName, aux) = QFileDialog.getOpenFileName(self, caption='Select a .csv File', filter='*.csv',options=options)
            #/home/rodrigo/Proyecto/vev/src/exports/tSNE-exps-WT_1(774-7332)-299_1(774-7332).csv
            if fileName != "":
                df = pd.read_csv(fileName)
                strains = df.Strain.unique()
                self.addSlidersTSNE(strains)
                columns = df.columns.unique()
                if 'Position' in columns:
                    tsneType = 'Positions'
                else:
                    tsneType = 'Passages'
                perps = df.Perp.unique()
                lrs = df.LR.unique()

                if len(perps) == 1 and len(lrs)==1:
                    perp = perps[0]
                    lr = lrs[0]
                else:
                    lr= None
                    perp = None


                if self.tsne == None:
                    boxAux = QtWidgets.QVBoxLayout(self.tsneFrame)
                    self.tsne = FigureTSNE(None, df, tsneType, nameExps, self.tsneFrame,lr,perp, width=6, height=5, dpi=100)
                    boxAux.addWidget(self.tsne)
                else:
                    #def newtSNE(self,dataframes,data, tsneType,nameExp,lr=None,perp=None):
                    self.tsne.newtSNE(None, df, tsneType, nameExps,lr,perp)
                self.perplexitySlider.valueChanged.disconnect()
                self.lrSlider.valueChanged.disconnect()
                if tsneType == 'Passages':
                    self.perplexitySlider.setValue(0)
                    self.lrSlider.setValue(0)
                    self.perplexitySlider.setMaximum(3)
                    self.lrSlider.setMaximum(3)
                    self.perAux = [3, 6, 12, 15]
                    self.lrAux = [10, 100, 300, 500]
                else:

                    self.perplexitySlider.setMaximum(1)
                    self.lrSlider.setMaximum(1)
                    self.perAux = [3,12]
                    self.lrAux = [10,300]

                    self.perplexitySlider.setValue(0)
                    self.lrSlider.setValue(0)
                    #self.perplexity.setText(str(3))
                    #self.lr.setText(str(10))

                self.perplexitySlider.valueChanged.connect(self.updateTSNE)
                self.lrSlider.valueChanged.connect(self.updateTSNE)
        except Exception as e:
            print(e)
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Error: Please import a valid t-SNE experiment CSV')
            error_dialog.exec()


    def exportLVRV(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.DontUseCustomDirectoryIcons
        fileName, _ = QFileDialog.getSaveFileName(self, caption='Save experiment', filter='*.csv',
                                                      options=options)
        if fileName !='':
            if '.csv' not in fileName:
                fileName = fileName.replace('.','') + '.csv'
            if self.lvrv == None:
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage('Error: Please Plot LV-RV before export')
                error_dialog.exec()
            else:
                nameExps,typeLVRV,param = self.lvrv.exportCSV(fileName)
                for ne in nameExps:
                    auxStrain = ne.split("_")
                    strain = auxStrain[0]
                    auxRep = auxStrain[1].split("(")
                    repetition = auxRep[0]
                    auxfvp = auxRep[1].split("-")
                    fvp = auxfvp[0]
                    lvp = auxfvp[1].split(")")[0]

                    otherexperiments = getExperiments(ne, nameExps)

                    log = typeLVRV + ' LV-RV was plotted with parameter ' + str(
                        param) + ' with this experiments: ' + otherexperiments
                    # logger(False, ne, log)
                    logging.info(log)
                    self.addEntrydb(strain, repetition, fvp, lvp, typeLVRV + ' LV-RV',otherexperiments + ' with parameter = ' + str(param), fileName)

    def importLVRV(self):
        try:

            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            options |= QFileDialog.DontUseCustomDirectoryIcons
            (fileName, aux) = QFileDialog.getOpenFileName(self, caption='Select a .csv File', filter='*.csv',
                                                          options=options)

            if fileName != "":
                df = pd.read_csv(fileName)
                lvrvType = df.type.unique()[0]

                if self.lvrv == None:
                    boxAux = QtWidgets.QVBoxLayout(self.lvrv_frame)
                    self.lvrv = FigureLVRV(df, self.lvrv_frame, lvrvType, None, width=6, height=5, dpi=100)
                    boxAux.addWidget(self.lvrv)
                else:
                    self.lvrv.updatelvrv(df)
        except Exception as e:
            print(e)
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Error: Please import a valid LV-RV experiment CSV')
            error_dialog.exec()

    def exportPCA(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.DontUseCustomDirectoryIcons
        fileName, _ = QFileDialog.getSaveFileName(self, directory=os.getcwd(), caption='Save experiment',
                                                  filter='*.csv',
                                                  options=options)
        if fileName != '':
            if '.csv' not in fileName:
                fileName = fileName.replace('.', '') + '.csv'
            if self.pca == None:
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage('Error: Please Plot PCA before export')
                error_dialog.exec()
            else:
                nameExps= self.pca.exportPCA(fileName)
                for ne in nameExps:
                    auxStrain = ne.split("_")
                    strain = auxStrain[0]
                    auxRep = auxStrain[1].split("(")
                    repetition = auxRep[0]
                    auxfvp = auxRep[1].split("-")
                    fvp = auxfvp[0]
                    lvp = auxfvp[1].split(")")[0]
                    otherexperiments = getExperiments(ne, nameExps)
                    log = 'PCA executed with this experiments ' + otherexperiments
                    # logger(False, ne, log)
                    logging.info(log)
                    self.addEntrydb(strain, repetition, fvp, lvp, 'PCA', otherexperiments, fileName)

    def importPCA(self):
        try:

            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            options |= QFileDialog.DontUseCustomDirectoryIcons
            (fileName, aux) = QFileDialog.getOpenFileName(self, directory=os.getcwd(), caption='Select a .csv File',
                                                          filter='*.csv',
                                                          options=options)

            if fileName != "":
                df = pd.read_csv(fileName)

                if self.pca == None:
                    boxAux = QtWidgets.QVBoxLayout(self.widget_image)
                    self.pca = FigurePCA(None, None, None, None, None, self.widget_image,df, width=6,
                                         height=5, dpi=100)
                    boxAux.addWidget(self.pca)
                else:
                    self.pca.updatePCA(None, None, None, None, None,df)
        except Exception as e:
            print(e)
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Error: Please import a valid PCA experiment CSV')
            error_dialog.exec()


    # data base functions
    # data base functions

    def addFunctions(self,funcName,params): #add entry in database for functions
        if self.Online: #online mode
            functionsCollection = self.db['functions']
            functionEntry = {"_id":funcName, "parameters":params}
            validation = self.validateEntry(functionEntry,'Function')
            if validation:
                entryD = functionsCollection.find_one({"_id": funcName})
                if entryD == None: #insert
                    functionsCollection.insert_one(functionEntry)
                else:
                    functionsCollection.update_one({'_id': funcName}, {"$set": functionEntry}, upsert=False)

    def addExperiment(self,strain,repetition,fvp,lvp): #add entry in database for experiments
        if self.Online: # online mode
            experimentsCollection = self.db['experiments']
            fvp = int(fvp)
            lvp = int(lvp)
            repetition = int(repetition)
            experimentEntry = {"_id":{"user": self.namePC, "strain": strain, "repetition": repetition,"fvp":fvp,
                              "lvp":lvp}}
            validation = self.validateEntry(experimentEntry, 'Experiment')
            if validation:
                entryD = experimentsCollection.find_one({"id": experimentEntry["_id"]})
                if entryD == None: #insert
                    experimentsCollection.insert_one(experimentEntry)

    def addEntrydb(self, strain, repetition, fvp, lvp, expName, params, result):
        if self.Online: #online mode
            fvp = int(fvp)
            lvp = int(lvp)
            repetition = int(repetition)
            vevExp = {"_id": {"user": self.namePC, "strain": strain, "repetition": repetition,"fvp":fvp,
                              "lvp":lvp,"expName":expName},"params":params,"result":result}
            validation = self.validateEntry(vevExp,'ResultsExperiments')
            if validation:
                vevExperiments = self.db['ResultsExperiments']


                entryD = vevExperiments.find_one({"_id": vevExp["_id"]})
                if entryD == None: #insert
                    vevExperiments.insert_one(vevExp)
                else: #update
                    vevExperiments.update_one({'_id': vevExp["_id"]}, {"$set": vevExp}, upsert=False)


    def addUser(self):
        if self.Online: #online mode
            userCollection = self.db['users']
            entryD = userCollection.find_one({"_id": self.namePC})
            user = {"_id": self.namePC}
            validation = self.validateEntry(user,'User')
            if validation:
                if entryD == None:  # insert
                    userCollection.insert_one(user)

    def validateEntry(self,entry,collection):
        #first need to select proper schema
        try:
            if collection == 'ResultsExperiments':
                with open(path_schemas+'Schema experiments results.json') as j:
                    schema = json.load(j)
            elif collection == 'Experiment':
                with open(path_schemas+'Schema experiments.json') as j:
                    schema = json.load(j)
            elif collection == 'Function':
                with open(path_schemas+'Schema function.json') as j:
                    schema = json.load(j)
            else:
                with open(path_schemas+'Schema user.json') as j:
                    schema = json.load(j)
            validate(instance=entry, schema=schema)
            return True
        except:
            return False
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Error: Invalid entry. Not fulfill schema')
            error_dialog.exec()

def main(args):
    app = QtWidgets.QApplication([])
    args = [x.upper() for x in args]  # upper args to avoid case sensitive
    if 'OFFLINE' in args:
        win = Interfaz('OFFLINE')
    else:
        win = Interfaz()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main(sys.argv)

