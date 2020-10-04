
import pandas as pd
import numpy as np
import os
import glob
from src.NumericalSort import numericalSort
import re

import os
pathPip=str(os.path.dirname(pd.__file__)).split('pandas')[0]


#format name_passage_strain_repetition.csv
path_pkl =pathPip+ 'src/data_experiments/'
def readData(parameters):
    i = 0
    strainControl = ''
    repetitionControl = ''
    path=parameters[0]
    fvp=parameters[1]
    lvp=parameters[2]

    df_list = []
    for filename in sorted(glob.glob(os.path.join(path, '*.csv')) , key=numericalSort):
        auxInfo = filename.split('/')
        auxInfo = auxInfo[len(auxInfo)-1]
        auxInfo = auxInfo.split('_')
        auxPassage = auxInfo[1]
        strain = auxInfo[2]
        auxRepetition = auxInfo[3]
        repetition = re.sub("\D+", '', auxRepetition)
        passage = re.sub("\D+",'',auxPassage)
        if i == 0: #to check only one type of strain and repetition
            strainControl = strain
            repetitionControl = repetition
            i = i +1
        if repetition != repetitionControl or strainControl != strain:
            raise Exception("Error, there are csv files from other experiment")
        df=pd.read_csv(filename)
        df['Passage']=passage
        df_list.append(df)



    df_T = pd.concat(df_list)
    df_T['Strain']=strain
    df_T['Repetition']=repetition
    df_T['info'] = df_T.apply(lambda row: str(row.Strain) + ',' + str(row.Repetition) + "," + str(row.Passage) + "," + str(row.Position),axis=1)


    positions = df_T['Position'].unique()
    lvpAux = positions[len(positions) - 1]
    if lvp ==0 or lvpAux < lvp:
        lvp = lvpAux
    df_T =keepValidPositions(df_T,fvp,lvp)


    return df_T, strain, repetition, lvp


def keepValidPositions(dfE, fvp, lvp):
    # Función que toma el dataframe y se queda solamente con las posiciones válidas

    # Busco el valor de las posiciones en el dataframe
    posiciones = dfE.Position.unique()

    # Encuentro los indices donde las posiciones son validas
    idx = np.where((posiciones >= fvp) & (posiciones <= lvp))

    # Guardo en posVal las posiciones validas
    posVal = posiciones[idx]

    # Me quedo con las posiciones validas del dataframe
    dfE_val = dfE[dfE.Position.isin(posVal)].copy()

    return dfE_val
