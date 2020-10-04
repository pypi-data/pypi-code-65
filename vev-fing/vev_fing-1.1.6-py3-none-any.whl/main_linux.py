from ReadData import readData
from GetEntropy import getEntropyExperiment, getEntropyExperimentAminos
from GetEntropySurface import getEntropySurface
from PlotEntropyPosition import plotEntropyPosition
from PCA import plotPCA
from EntropyInterpolation import interpolationPosition
import pandas as pd
import os
from PIL import Image
from PlotPopularDecay import plotPopularDecay
from PyQt5 import *
import sys

loaded_dfs = []
folder = ''
def commandExecute(argument):
    switcher ={
        '0': 'exit',
        '1': 'readDataExperiment',
        '2': 'loadDataExperiment',
        '3': 'getEntropy',
        '4': 'loadEntroy',
        '5': 'interpolateExperiment',
        '6': 'plotEntropySurface',
        '7': 'getPCA',
        '8': 'getCodonDecay',
        '9': 'plotEntropyPositionExperiment',
        '10': 'getLoadedExperiments'
    }
    ok = False
    while not ok:
        try:
            command = switcher[argument]
            ok = True
        except:
            argument =input('Escriba un comando valido: ')
    return eval(command + '()')

def main():
        print('#######################################################################')
        print('######################## VEV PROYECT ##################################')
        salir = False

        while not salir:
            print('1: Leer Nuevos Datos de Experimentos')
            print('2: Cargar Experimento ya procesado')
            print('3: Calcular Entropía')
            print('4: Cargar Entropía ya calculada')
            print('5: Interpolar Datos')
            print('6: Plotear Superficie de Entropía')
            print('7: Hacer PCA')
            print('8: Codon decay')
            print('9: Plotear Entropía por Posición')
            print('10: Ver Experimentos Cargados')
            print('0: Salir')
            command = input("Escriba el número de comando a ejecutar: ")
            salir=commandExecute(command)
            print("\n\n")

def exit():
    return True

def readDataExperiment():
    strain = input ("Escriba el nombre del experimento a leer: ")
    global folder
    if folder =='':
        folder = input ("Escriba la ubicación de los datos: ")
    repetition = input("Escriba el número de repetición: ")
    path = folder + '/' + strain + '_' + repetition+'/'
    print(path)
    parameters = [path,'Sample_p',strain,repetition,0,2482]
    try:
        df = readData(parameters)
        experimentName = strain + '_' + repetition + '.pkl'
        df.to_pickle(os.getcwd()+'/'+experimentName)
        loaded_dfs.append(experimentName)
        return False
    except:
        folder=''
        print("No se pudo cargar los datos, verifique los parametros envíados")
        return False


def loadDataExperiment():
    strain = input ("Escriba el nombre del experimento a cargar: ")
    folder = input ("Escriba la ubicación de los datos: ")
    repetition = input("Escriba el número de repetición: ")
    path = folder + '/' + strain + '_' + repetition + '/'
    parameters = [path,'Sample_p',strain,repetition,0,2482]

    experimentName = strain + '_' + repetition + '.pkl'
    if not experimentName in loaded_dfs:
        try:
            df = readData(parameters)
            df.to_pickle(os.getcwd() + '/' + experimentName)
            loaded_dfs.append(experimentName)
            return False
        except:
            print("No existe un experimento ya precargado con esos parametros")
            return False
    return False

def getEntropy():
    strain = input ("Escriba el nombre del experimento: ")
    repetition = input("Escriba el número de repetición: ")
    experimentName = strain + '_' + repetition + '.pkl'
    entropyName = strain + '_' + repetition + '_entropy.pkl'
    if not experimentName in loaded_dfs:
        print ("Primero debe cargar los datos del experimento")
        return False
    else:
        dfAux=pd.read_pickle(os.getcwd()+'/'+experimentName)
        df = getEntropyExperiment(os.getcwd(),strain,repetition,dfAux)
        df.to_pickle(os.getcwd() + '/' + entropyName)
        loaded_dfs.append(entropyName)
    return False

def loadEntroy():
    strain = input ("Escriba el nombre del experimento: ")
    repetition = input("Escriba el número de repetición: ")
    experimentName = strain + '_' + repetition + '.pkl'
    entropyName = strain + '_' + repetition + '_entropy.pkl'
    if not entropyName in loaded_dfs:
        try:
            dfAux = pd.read_pickle(os.getcwd()+'/'+experimentName)
            df = getEntropyExperiment(os.getcwd(), strain, repetition, dfAux)
            df.to_pickle(os.getcwd() + '/' + entropyName)
            loaded_dfs.append(entropyName)
            return False
        except:
            print('Primero debe calcular la entropia')
            return False

def interpolateExperiment():
    strain = input ("Escriba el nombre del experimento a interpolar: ")
    repetition = input("Escriba el número de repetición: ")
    pasaje = input("Escriba el pasaje: ")
    experimentName = strain + '_' + repetition+'_entropy.pkl'
    if not experimentName in loaded_dfs:
        print ("Primero debe cargar la entropia")
    else:
        try:
            df = pd.read_pickle(os.getcwd()+'/'+experimentName)
            df = interpolationPosition(pasaje,df)
            df.to_pickle(os.getcwd() + '/' + experimentName)
            return False
        except:
            print("El pasaje otorgado no es correcto")
            return False

    return False

def plotEntropySurface():
    strain = input ("Escriba el nombre del experimento a plotear: ")
    repetition = input("Escriba el número de repetición: ")
    experimentName = strain + '_' + repetition+'_entropy.pkl'
    if not experimentName in loaded_dfs:
        print ("Primero debe cargar la entropia")
    else:
        df = pd.read_pickle(os.getcwd()+'/'+experimentName)
        getEntropySurface(df)
    return False

def getPCA():
    finish = False
    dfAux = []
    position = input('Escriba la posición que desea resaltar: ')
    while not finish:
        strain = input ("Escriba el nombre del experimento: ")
        repetition = input("Escriba el número de repetición: ")
        experimentName = strain + '_' + repetition + '_entropy.pkl'
        if not experimentName in loaded_dfs:
            print ("La entropia no está calculada")
        else:
            dfAux.append(pd.read_pickle(os.getcwd()+'/'+experimentName))
            salir = input ("Escriba 'S' si desea cargar otro experimento, 'N' en caso contrario: ")
            if salir=='N' and len(dfAux) > 1:
                finish = True
            elif salir=='N' and len(dfAux) == 1:
                print('Debe cargar al menos 2 experimentos')
            elif salir!='N' and salir!='S':
                control = False
                while not control:
                    salir = input ("Escriba unicamente 'S' si desea cargar otro experimento, 'N' en caso contrario: ")
                    if salir == 'N':
                        finish = True
                        control = True
                    elif salir == 'S':
                        control = True
    plotPCA(dfAux,int(position))


def getCodonDecay():
    strain = input ("Escriba el nombre del experimento: ")
    repetition = input("Escriba el número de repetición: ")
    th = input("Escriba el valor del umbral: ")
    while float(th) >= 1:
        th = input("Escriba un valor de umbral menor que 1: ")

    experimentName = strain + '_' + repetition + '.pkl'
    if not experimentName in loaded_dfs:
        print ("Primero debe cargar los datos del experimento")
    else:
        df = pd.read_pickle(os.getcwd() + '/' + experimentName)
        plotPopularDecay(df, 1, 2000, float(th))
    return False

def plotEntropyPositionExperiment():
    strain = input ("Escriba el nombre del experimento: ")
    repetition = input("Escriba el número de repetición: ")
    position = input("Escriba la posición: ")
    experimentName = strain + '_' + repetition+'_entropy.pkl'
    if not experimentName in loaded_dfs:
        print ("Primero debe cargar la entropia del experimento")
    else:
        df = pd.read_pickle(os.getcwd()+'/'+experimentName)
        plotEntropyPosition(int(position), df, 'red')
        name = 'Entropy_' + str(position) + '.png'
        img = Image.open(name)
        titleAux = "Entropy for position "+position
        img.show(title=titleAux)
    return False



def getLoadedExperiments():
    listExp = ''
    for exp in loaded_dfs:
        listExp += exp + ' '
    print ('Los Experimentos cargados: '+listExp)
    return False





if __name__ == "__main__":

    main()
