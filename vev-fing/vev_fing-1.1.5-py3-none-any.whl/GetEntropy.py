import pandas as pd
import numpy as np
import math
import os
import time
import os
pathPip=str(os.path.dirname(pd.__file__)).split('pandas')[0]

path_pkl = pathPip+'src/data_experiments/'


def getEntropyExperiment(strain,repetition,fvp,lvp,dataFrame):
    filePath=path_pkl +str(strain)+'_' +str(repetition)+'('+str(fvp)+'-'+str(lvp)+')_entropy.parquet'

    if os.path.isfile(filePath):
        return pd.read_parquet(filePath)
    else:
        entropyList = []
        epsilon = 2.2204e-16
        for index, row in dataFrame.iterrows():
            i = 0
            entropy = float(0)
            for freq in row:
                i += 1
                if i > 2 and i < 67: # i=1 está pasaje, i=2 está coverage y apartir de i=3 tenes los 64 codones
                    entropy -= np.multiply(freq, (math.log(freq + epsilon)))  # logaritmo en base e de la frequencia
            entropyList.append(entropy)

        dataFrame['Entropy'] = np.asarray(entropyList)
        df = dataFrame[['Position','Coverage','Strain','Repetition','Passage','Entropy','info']]

        return df
    

def getEntropyExperimentAminos(strain,repetition,fvp,lvp,dataFrame):
    filePath=path_pkl +str(strain)+'_' +str(repetition)+'('+str(fvp)+'-'+str(lvp)+')_aminos_entropy.parquet'

    if os.path.isfile(filePath):
        return pd.read_parquet(filePath)
    else:

        entropyList = []
        epsilon = 2.2204e-16
        for index, row in dataFrame.iterrows():
            i = 0
            entropy = float(0)
            for freq in row:
                i += 1
                if i > 1 and i < 23: # i=1 está pasaje, i=2 está coverage y apartir de i=3 tenes los 64 codones
                    entropy -= np.multiply(freq, (math.log(freq + epsilon)))  # logaritmo en base e de la frequencia
            entropyList.append(entropy)

        dataFrame['Entropy'] = np.asarray(entropyList)
        dataFrame.to_parquet(filePath)
        return dataFrame
