import numpy as np
import pandas as pd
def experimentToPassages(df):
    #Función que toma el experimento (dataframe df) y convierte cada pasaje en una fila
    
    #Busco los pasajes
    passages=df['Passage'].unique()
    
    #Obtengo la info
    info_df=str(df['info'].iloc[0])
    strain_df=info_df.split(',')[0]
    repetition_df=info_df.split(',')[1]
    
  
    arrayDF_P  = []
    arrayInfo = []
    arrayStrain = []

    for p in passages:
#        dfP=df[df.Passage.eq(p)]
#        dfP_val=dfP[dfP.Position.isin(posVal)].copy()
#        passageArray=np.array(dfP_val[['Entropy']])

        dfP=df[df.Passage.eq(p)]
#        print(isinstance(dfP,pd.DataFrame))
        dfPE=dfP[['Entropy']]
#        print(isinstance(dfPE,pd.DataFrame))
        passageArray=np.array(dfPE)
        
        pA = np.squeeze(np.array([passageArray]))
        arrayDF_P.append(pA)
        arrayInfo.append(str(strain_df)+','+str(repetition_df)+','+str(p))
        arrayStrain.append(str(strain_df))
    return np.array(arrayDF_P), np.array(arrayInfo), np.array(arrayStrain)

        
def totalExperimentsToPassages(parameters):
    #Función que toma todos los experimentos que haya cargados en parameters y convierte cada experimento a una fila por pasaje
    
    #Arrays donde se guardan los pasajes como filas y la info
    arrayT_DF_P  = []
    arrayT_Info = []
    arrayT_Strain = []
    
    totalArrayData = []
    totalArrayInfo = []
    totalArrayStrain = []
#    firstIteration = True
    
    for df in parameters:
        arrayP, arrayI, arrayS=experimentToPassages(df)
        arrayT_DF_P.append(arrayP)
        arrayT_Info.append(arrayI)
        arrayT_Strain.append(arrayS)
    
    totalArrayData = np.concatenate(arrayT_DF_P)
    totalArrayInfo = np.concatenate(arrayT_Info)
    totalArrayStrain = np.concatenate(arrayT_Strain)
        
    return totalArrayData, totalArrayInfo, totalArrayStrain

def experimentToPositions(df):
    #Función que toma el experimento (dataframe df) y convierte cada pasaje en una fila
    
    #Busco los pasajes
    positions=df['Position'].unique()
    
    #Obtengo la info
    info_df=str(df['info'].iloc[0])
    strain_df=info_df.split(',')[0]
    repetition_df=info_df.split(',')[1]
    
    arrayDF_P  = []
    arrayInfo = []
    arrayStrain = []
    
    for p in positions:
        dfP=df[df.Position.eq(p)]
#        print(isinstance(dfP,pd.DataFrame))
        dfPE=dfP[['Entropy']]
#        print(isinstance(dfPE,pd.DataFrame))
        positionArray=np.array(dfPE)
        
        pA = np.squeeze(np.array([positionArray]))
        arrayDF_P.append(pA)
        arrayInfo.append(str(strain_df)+','+str(repetition_df)+','+str(p))
        arrayStrain.append(str(strain_df))
    return np.array(arrayDF_P), np.array(arrayInfo), np.array(arrayStrain)

def totalExperimentsToPositions(parameters):
    #Función que toma todos los experimentos que haya cargados en parameters y convierte cada experimento a una fila por pasaje
    
    #Arrays donde se guardan las posiciones como filas y la info
    arrayT_DF_P  = []
    arrayT_Info = []
    arrayT_Strain = []
    
    totalArrayData = []
    totalArrayInfo = []
    totalArrayStrain = []
#    firstIteration = True
    
    for df in parameters:
        arrayP, arrayI, arrayS=experimentToPositions(df)
        arrayT_DF_P.append(arrayP)
        arrayT_Info.append(arrayI)
        arrayT_Strain.append(arrayS)
    
    totalArrayData = np.concatenate(arrayT_DF_P)
    totalArrayInfo = np.concatenate(arrayT_Info)
    totalArrayStrain = np.concatenate(arrayT_Strain)
        
    return totalArrayData, totalArrayInfo, totalArrayStrain

def formatStrains(strainT):
    #Función que toma el array de strains y le asigna a cada una un int a partir del 0
    #Ademas calcula el valor que debe tomar el parámetro perplexity de tSNE de acuerdo a la cantidad de puntos de cada cepa
    
    #Paso a dataframe las cepas de los experimentos cargados
    df = pd.DataFrame(strainT,columns=["Strain"])
    df = df.assign(StrainNumber = df['Strain'])
    #Busco la cantidad de pasajes de cada cepa
    strainsU=df.Strain.unique()
    dataRows = []
    i=0
    for s in strainsU:
        n=df[df.Strain.eq(s)].count()
        dataRows.append(n)
        df.loc[df['Strain'] == s, 'StrainNumber'] = i
#        df[df.Strain.eq(s)]["StrainNumber"]=i
        i+=1
    arNum = np.array(dataRows)
    num = arNum.min()
#    perp = p//3
#    print(perp)
#    print(df.shape)
    return num, df