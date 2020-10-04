import pandas as pd
import numpy as np

#para pasajes iniciales y ultimos ver casos

def interpolationPassageFreq(passage, dataframe):
    passages = dataframe.Passage.unique().tolist()
    if not passage in passages:
        passage = str(int(passage) + 1)
    i = passages.index(passage)
    auxPassagePlus = passages[i + 1]
    auxPassageMinus = passages[i - 1]
    columns = dataframe.columns
    i=0
    for c in columns:
       if i > 1 and i < 66: #all the codons
           dataframe.loc[dataframe.Passage == passage, c] = None
           df1 = dataframe.loc[dataframe.Passage == auxPassageMinus, c].tolist()
           df3 = dataframe.loc[dataframe.Passage == auxPassagePlus, c].tolist()
           df2 = dataframe.loc[dataframe.Passage == passage, c].tolist()
           dfs = [df1, df2, df3]
           dfAux = pd.DataFrame(dfs)
           dfAux = dfAux.interpolate()
           aux = dfAux.iloc[[1]].values.tolist()
           dataframe.loc[dataframe.Passage == passage, c] = np.asarray(aux[0])
       i=i+1



    return dataframe


def interpolationPassage(passage, dataframe):
    passages = dataframe.Passage.unique().tolist()
    if not passage in passages:
        passage = str(int(passage) + 1)
    i = passages.index(passage)
    auxPassagePlus = passages[i + 1]
    auxPassageMinus = passages[i - 1]
    dataframe.loc[dataframe.Passage == passage, 'Entropy'] = None
    df1 = dataframe.loc[dataframe.Passage == auxPassageMinus, 'Entropy'].tolist()
    df3 = dataframe.loc[dataframe.Passage == auxPassagePlus, 'Entropy'].tolist()
    df2 = dataframe.loc[dataframe.Passage == passage, 'Entropy'].tolist()
    dfs = [df1, df2, df3]
    dfAux = pd.DataFrame(dfs)
    dfAux = dfAux.interpolate()
    aux = dfAux.iloc[[1]].values.tolist()
    dataframe.loc[dataframe.Passage == passage, 'Entropy'] = np.asarray(aux[0])

    return dataframe
