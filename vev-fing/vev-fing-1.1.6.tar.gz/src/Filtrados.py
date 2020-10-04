import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage.filters import uniform_filter1d
from src.Format_DF import totalExperimentsToPassages, formatStrains, experimentToPositions



def filtradoPromedioMovil_DF(df,vent):

    """
    Función que toma el datafame de un experimento completo y le hace el promedio móvil
    del tamaño indicado por vent
    """

    df_FPM=df.copy(deep=True)
    df_FPM['EntrPromMov']=None
#    df_FPM=df_FPM.astype({'Passage':int})

    passages=df['Passage'].unique()
    positions=df['Position'].unique()

    indMax=passages.size


    for pos in positions:
        for pas in passages:
            '''Encuentro el índice dentro del array passages del elemento pass'''
            result = np.where(passages == pas)

#            print(result[0])

            sumandos=0
            promediados=0
            sumandos+=1

            for i in range(int(np.floor(vent/2))):
                if ((result[0]-(i+1))>=0):
                    sumandos+=1
#                    print('Posicion: '+str(pos)+', pasaje: '+str(pas)+', valor de i por el -: '+str(i+1))
                    indice = result[0] - (i+1)
                    pass_i=passages[indice]
                    valor = df_FPM.loc[(df_FPM['Passage'] == pass_i[0]) & (df_FPM['Position'] == pos), 'Entropy']
#                    print(valor)
                    promediados = promediados + valor
                if((result[0]+(i+1))<indMax):
                    sumandos+=1
#                    print('Posicion: '+str(pos)+', pasaje: '+str(pas)+', valor de i por el +: '+str(i+1))
                    indice = result[0] - (i+1)
                    pass_i=passages[indice]
                    valor = df_FPM.loc[(df_FPM['Passage'] == pass_i[0]) & (df_FPM['Position'] == pos), 'Entropy']
#                    print(valor)
                    promediados = promediados + valor
            ent_PM=promediados/sumandos
            df_FPM.loc[(df_FPM['Passage'] == pass_i[0]) & (df_FPM['Position'] == pos), 'EntrPromMov'] = ent_PM



    return df_FPM


#def movingAverage_1(arr,n):
#
#    ret = np.cumsum(arr, axis=0, dtype=float)
##    return ret
#    ret[n:] -= ret[:-n]
#    return ret[n - 1:] / n
#
#def movingAverage_2(arr, n=3):
#
#    ma=np.zeros(arr.shape)
#
#    for i in range(arr.shape[0]):
#        ma[i,:]=np.convolve(arr[i,:], np.ones(arr.shape[1]), mode='valid')
#
#    return ma


def movingAverage_1D(arr, n=3):

    y_f = uniform_filter1d(arr, mode='constant', size=n)

    r=int(np.floor(n/2)+1)

#    print('El principio')

    for i in range(r-1):
        d=((np.floor(n/2)+1)+i)
#        print(d)
        y_f[i]=n*y_f[i]/d

#    print('El final')

    for i in range(y_f.shape[0]-r+1,y_f.shape[0]):
        d=y_f.shape[0]-i+np.floor(n/2)
#        print(d)
        y_f[i]=n*y_f[i]/d


    return y_f


def movingAverage(arr, n=3):

    arr_MA = np.zeros_like(arr)

    for i in range(arr.shape[0]):
        arr_MA[i]=movingAverage_1D(arr[i],n)
    return arr_MA


def filtradoPromedioMovil(df, ventana):

    ar_Data, ar_Info, ar_Strain = experimentToPositions(df)

    df_I = pd.DataFrame([sub.split(",") for sub in ar_Info])
    df_I.columns=["Strain", "Repetition", "Position"]

    passages=df['Passage'].unique()

    arr_Low = movingAverage(ar_Data, n=ventana)
    arr_High=np.abs(ar_Data-arr_Low)

    df_Data=pd.DataFrame(ar_Data)
    df_Data.columns=[passages]
#    df_Data['Position']=positions
    df_D = pd.concat([df_Data, df_I], axis=1)

    df_Data_Low=pd.DataFrame(arr_Low)
    df_Data_Low.columns=[passages]
#    df_Data_Low['Position']=positions
    df_D_L = pd.concat([df_Data_Low, df_I], axis=1)

    df_Data_High=pd.DataFrame(arr_High)
    df_Data_High.columns=[passages]
#    df_Data_High['Position']=positions
    df_D_H = pd.concat([df_Data_High, df_I], axis=1)

    return df_D, df_D_L, df_D_H


def descomposicion_PM_LV_RV(df, ventana):

    ar_Data, ar_Info, ar_Strain = experimentToPositions(df)

    df_I = pd.DataFrame([sub.split(",") for sub in ar_Info])
    df_I.columns=["Strain", "Repetition", "Position"]

    arr_Low = movingAverage(ar_Data, n=ventana)
    arr_High=np.abs(ar_Data-arr_Low)

    ar_Data_Sum=np.sum(ar_Data, axis=1)
    arr_Low_Sum=np.sum(arr_Low, axis=1)
    arr_HighSum=np.sum(arr_High, axis=1)

    data_Aux=pd.DataFrame(columns=["Info", "Position", "Strain", "Repetition", "Entropy_Acum", "Entropy_Low", "Entropy_High"])

    data_Aux['Info']=ar_Info
    data_Aux['Position']=df_I.Position
    data_Aux['Strain']=df_I.Strain
    data_Aux['Repetition']=df_I.Repetition
    data_Aux['Entropy_Acum']=ar_Data_Sum
    data_Aux['Entropy_Low']=arr_Low_Sum
    data_Aux['Entropy_High']=arr_HighSum

    return data_Aux


def descomposicion_PM_LV_RV_Experiments(experiments, ventana):

    l_LV_RV=[]

    for df in experiments:

        descomposicion = descomposicion_PM_LV_RV(df, ventana)
        l_LV_RV.append(descomposicion)

    return l_LV_RV


def filtradoPoly(df, grado):

    ar_Data, ar_Info, ar_Strain = experimentToPositions(df)

    df_I = pd.DataFrame([sub.split(",") for sub in ar_Info])
    df_I.columns=["Strain", "Repetition", "Position"]

    passages=df['Passage'].unique()

    passages = list(map(int, passages))

    arr_Low = np.zeros_like(ar_Data)

    for i in range(ar_Data.shape[0]):
        z = np.polyfit(passages, ar_Data[i], grado)
        p = np.poly1d(z)
        arr_Low[i]=p(passages)

    arr_High=np.abs(ar_Data-arr_Low)

    df_Data=pd.DataFrame(ar_Data)
    df_Data.columns=[passages]
    df_D = pd.concat([df_Data, df_I], axis=1)

    df_Data_Low=pd.DataFrame(arr_Low)
    df_Data_Low.columns=[passages]
    df_Data_Low = pd.concat([df_Data_Low, df_I], axis=1)

    df_Data_High=pd.DataFrame(arr_High)
    df_Data_High.columns=[passages]
    df_Data_High = pd.concat([df_Data_High, df_I], axis=1)

    return df_D, df_Data_Low, df_Data_High


def descomposicion_Poly_LV_RV(df, grado):

    ar_Data, ar_Info, ar_Strain = experimentToPositions(df)

    df_I = pd.DataFrame([sub.split(",") for sub in ar_Info])
    df_I.columns=["Strain", "Repetition", "Position"]

    passages=df['Passage'].unique()

    passages = list(map(int, passages))

    arr_Low = np.zeros_like(ar_Data)

    for i in range(ar_Data.shape[0]):
        z = np.polyfit(passages, ar_Data[i], grado)
        p = np.poly1d(z)
        arr_Low[i]=p(passages)

    arr_High=np.abs(ar_Data-arr_Low)

    ar_Data_Sum=np.sum(ar_Data, axis=1)
    arr_Low_Sum=np.sum(arr_Low, axis=1)
    arr_HighSum=np.sum(arr_High, axis=1)

    data_Aux=pd.DataFrame(columns=["Info", "Position", "Strain", "Repetition", "Entropy_Acum", "Entropy_Low", "Entropy_High"])

    data_Aux['Info']=ar_Info
    data_Aux['Position']=df_I.Position
    data_Aux['Strain']=df_I.Strain
    data_Aux['Repetition']=df_I.Repetition
    data_Aux['Entropy_Acum']=ar_Data_Sum
    data_Aux['Entropy_Low']=arr_Low_Sum
    data_Aux['Entropy_High']=arr_HighSum

    return data_Aux


def descomposicion_Poly_LV_RV_Experiments(experiments, grado):

    l_LV_RV=[]

    for df in experiments:

        descomposicion = descomposicion_Poly_LV_RV(df, grado)
        l_LV_RV.append(descomposicion)

    return l_LV_RV




#def polynomialFilter(df):
#
#    ar_Data, ar_Info, ar_Strain = experimentToPositions(df)
#
#    passages = df['Passage'].unique()
#    passages = list(map(int, passages))
#
#    f = interpolate.interp1d(passages, ar_Data, kind='cubic')
#
#    return f

def plot_LV_RV(exps):

    fig, ax = plt.subplots()
    for df in exps:
        info=(df.loc[0].Info).split(",")
        x=df.Entropy_Low
        y=df.Entropy_High
#        ax.scatter(x, y, alpha=0.5)
        ax.scatter(x, y, alpha=0.5, label="Cepa {s}, repetición {r}".format(s=info[0], r=info[1]))
    plt.grid()
    plt.legend(bbox_to_anchor=(1.1, 1.05))
    return fig
