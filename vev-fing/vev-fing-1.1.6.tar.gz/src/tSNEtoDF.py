import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.manifold import TSNE
from pandas.plotting import scatter_matrix

def keepValidPositions(dfE, fvp, lvp):
    #Función que toma el dataframe y se queda solamente con las posiciones válidas
    
    #Busco el valor de las posiciones en el dataframe
    posiciones=dfE.Position.unique()
    
    #Encuentro los indices donde las posiciones son validas
    idx=np.where((posiciones>=fvp)&(posiciones<=lvp))
    
    #Guardo en posVal las posiciones validas
    posVal=posiciones[idx]
    
    #Me quedo con las posiciones validas del dataframe
    dfE_val=dfE[dfE.Position.isin(posVal)].copy()
    
    return dfE_val
    
def experimentToPassages(df):
    #Función que toma el experimento (dataframe df) y convierte cada pasaje en una fila
    
    #Busco los pasajes
    passages=df['Passage'].unique()
    
    #Obtengo la info
    info_df=str(df['info'].iloc[0])
    strain_df=info_df.split(',')[0]
    repetition_df=info_df.split(',')[1]
    
    #Busco el valor de las posiciones en el dataframe
#    posiciones=df.Position.unique()
    #Encuentro los indices donde las posiciones son validas
#    idx=np.where((posiciones>=fvp)&(posiciones<=lvp))
    #Guardo en posVal las posiciones validas
#    posVal=posiciones[idx]
    
    arrayDF_P  = []
    arrayInfo = []
    arrayStrain = []
#    print(isinstance(df,pd.DataFrame))
    
    for p in passages:
#        dfP=df[df.Passage.eq(p)]
#        dfP_val=dfP[dfP.Position.isin(posVal)].copy()
#        passageArray=np.array(dfP_val[['Entropy']])

        dfP=df[df.Passage.eq(p)]
#        print(isinstance(dfP,pd.DataFrame))
        dfPE=dfP[['Entropy']]
#        print(isinstance(dfPE,pd.DataFrame))
        passageArray=np.array(dfPE)
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

def totalExperimentsToPoints(parameters):
    #Función qur toma todos los experimentos cargados y los convierte en una fila (cada experimento pasa a ser una fila)
    
    #Arrays donde se guardan los pasajes como filas y la info
    arrayDF  = []
    infoDF = []
    strainDF = []
    for df in parameters:
        #Obtengo la info
        info_df=str(df['info'].iloc[0])
        strain=info_df.split(',')[0]
        arrayDF.append(df['Entropy'])
        infoDF.append(df['info'])
        strainDF.append(strain)
    aDFasPoints = np.squeeze(np.array([arrayDF]))
    strainDFasPoints=np.squeeze(np.array(strainDF))
    return aDFasPoints, strainDFasPoints

def formatS_tSNE(strainT):
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
    arPerp = np.array(dataRows)
    p = arPerp.min()
    perp = p//3
#    print(perp)
#    print(df.shape)
    return perp, df


def apply_2D_tSNE(data, infoStrains, randState, perp):
    #Función que calcula los componentes 2D de tSNE

    transformedData = TSNE(perplexity=perp, random_state=randState).fit_transform(data)
    return transformedData

def apply_3D_tSNE(data, randState, perp):
    #Función que calcula los componentes 3D de tSNE
    
    transformedData = TSNE(n_components=3,perplexity=perp, random_state=randState).fit_transform(data)
    return transformedData


def tsne_SB_Scatter2D(datos, strainsDF):
    #Función que plotea como scatter la tSNE 2D basado en seaborn
    
    dfD = pd.DataFrame(datos,columns=["tSNE-2d-1", "tSNE-2d-2"])
#    print(datos.shape)
#    print(strainsDF.shape)
    dfS = pd.DataFrame(strainsDF,columns=["Strain", "StrainNumber"])
#    dfS = pd.DataFrame(strainsDF,columns=["Strain"])
    dfT=pd.concat([dfD,dfS], axis=1)
#    dfS = pd.DataFrame(strainsDF,columns=["Strain", "StrainNumber"])
#    sns.lmplot( x="X", y="Y", data=datos, fit_reg=False, hue=strainsArr, legend=False)
    sns.pairplot( x_vars="tSNE-2d-1", y_vars="tSNE-2d-2", data=dfT, hue="Strain", size=5)
#    sns.lmplot( x="tSNE-2d-1", y="tsne-2d-2", data=df, hue=strainsArr, legend=False)
#    sns.plt.show()
    return


def tSNE_SB_Pairgrid(datos, strainsDF):
    #Función que realiza el pairplot de los primeras 3 componentes de tSNE
    fig, ax = plt.subplots()
    dfD = pd.DataFrame(datos,columns=["tSNE-1", "tSNE-2", "tSNE-3"])
    dfS = pd.DataFrame(strainsDF,columns=["Strain"])
    dfT=pd.concat([dfD,dfS], axis=1)
    strains=dfT.Strain.unique()
    g=sns.PairGrid(dfT, hue="Strain")
    g = g.map(plt.scatter)
    ax.legend()
    name = 'plot_images/tSNE_Pairgrid' +str(strains)+'_'+'.png'
    plt.savefig(name)
    plt.close()
    return strains


def tSNE_SB_Pairplot(datos, strainsDF):
    #Función que realiza el pairplot de los primeras 3 componentes de tSNE
    fig, ax = plt.subplots()
    dfD = pd.DataFrame(datos,columns=["tSNE-1", "tSNE-2", "tSNE-3"])
    dfS = pd.DataFrame(strainsDF,columns=["Strain"])
    dfT=pd.concat([dfD,dfS], axis=1)
    strains=dfT.Strain.unique()
    sns.pairplot(dfT, hue="Strain")
#    g = g.map(plt.scatter)
    ax.legend()
    name = 'plot_images/tSNE_Pairplot' +str(strains)+'_'+'.png'
    plt.savefig(name)
    plt.close()
    return


def tSNE_PD_scatterM(datos, strainsDF):
    #Función que realiza el pairplot de los primeras 3 componentes de tSNE
    fig, ax = plt.subplots()
    dfD = pd.DataFrame(datos,columns=["tSNE-1", "tSNE-2", "tSNE-3"])
    dfS = pd.DataFrame(strainsDF,columns=["Strain", "StrainNumber"])
    dfT=pd.concat([dfD,dfS], axis=1)
    strains=dfT.Strain.unique()
    scatter_matrix(dfT, c=dfT.StrainNumber)
    ax.legend()
    name = 'plot_images/tSNE_ScatterMatrix' +str(strains)+'_'+'.png'
    plt.savefig(name)
    plt.close()
#    plt.show
    return


def tSNE_Pairplot(datos, strainsDF):
    #Función que realiza el pairplot de los primeras 3 componentes de tSNE
    fig, ax = plt.subplots()
    dfD = pd.DataFrame(datos,columns=["tSNE_1", "tSNE_2", "tSNE_3"])
    dfS = pd.DataFrame(strainsDF,columns=["Strain"])
    dfT=pd.concat([dfD,dfS], axis=1)
    strains=dfT.Strain.unique()
    
    ax1=plt.subplot(331)
    for s in strains:
        d=dfT.loc[dfT['Strain'] == s]
        x=d.tSNE_1
        y=d.tSNE_1
        ax1.scatter(x, y, label=s)
        
    ax2=plt.subplot(332)
    for s in strains:
        d=dfT.loc[dfT['Strain'] == s]
        x=d.tSNE_2
        y=d.tSNE_1
        ax2.scatter(x, y, label=s)
    
    ax3=plt.subplot(333)
    for s in strains:
        d=dfT.loc[dfT['Strain'] == s]
        x=d['tSNE_3']
        y=d['tSNE_1']
        ax3.scatter(x, y, label=s)
        
    ax4=plt.subplot(334)
    for s in strains:
        d=dfT.loc[dfT['Strain'] == s]
        x=d['tSNE_1']
        y=d['tSNE_2']
        ax4.scatter(x, y, label=s)
        
    ax5=plt.subplot(335)
    for s in strains:
        d=dfT.loc[dfT['Strain'] == s]
        x=d['tSNE_2']
        y=d['tSNE_2']
        ax5.scatter(x, y, label=s)
        
    ax6=plt.subplot(336)
    for s in strains:
        d=dfT.loc[dfT['Strain'] == s]
        x=d['tSNE_3']
        y=d['tSNE_2']
        ax6.scatter(x, y, label=s)
        
    ax7=plt.subplot(337)
    for s in strains:
        d=dfT.loc[dfT['Strain'] == s]
        x=d['tSNE_1']
        y=d['tSNE_3']
        ax7.scatter(x, y, label=s)
        
    ax8=plt.subplot(338)
    for s in strains:
        d=dfT.loc[dfT['Strain'] == s]
        x=d['tSNE_2']
        y=d['tSNE_3']
        ax8.scatter(x, y, label=s)
        
    ax9=plt.subplot(339)
    for s in strains:
        d=dfT.loc[dfT['Strain'] == s]
        x=d['tSNE_3']
        y=d['tSNE_3']
        ax9.scatter(x, y, label=s)
        
#    plt.show()
    ax.legend()
    name = 'plot_images/tSNE_Pairplot' +str(strains)+'_'+'.png'
    plt.savefig(name)
    plt.close()
    return


def tsne_MPL_Scatter2D(datos, strainsDF):
    #Función que plotea como scatter la tSNE 2D basado en matplotlib
    fig, ax = plt.subplots()
    dfD = pd.DataFrame(datos,columns=["tSNE_2d_1", "tSNE_2d_2"])
#    print(datos.shape)
#    print(strainsDF.shape)
    dfS = pd.DataFrame(strainsDF,columns=["Strain", "StrainNumber"])
#    dfS = pd.DataFrame(strainsDF,columns=["Strain"])
    dfT=pd.concat([dfD,dfS], axis=1)
    strains=dfT.Strain.unique()
    for s in strains:
        d=dfT.loc[dfT['Strain'] == s]
        x=d.tSNE_2d_1
        y=d.tSNE_2d_2
        ax.scatter(x, y, label=s)
    ax.legend()
    name = 'plot_images/tSNE_2D' +str(strains)+'_'+'.png'
    plt.savefig(name)
    plt.close()
#    plt.show()
#    dfS = pd.DataFrame(strainsDF,columns=["Strain", "StrainNumber"])
#    sns.lmplot( x="X", y="Y", data=datos, fit_reg=False, hue=strainsArr, legend=False)
#    sns.pairplot( x_vars="tSNE-2d-1", y_vars="tSNE-2d-2", data=dfT, hue="Strain", size=5)
#    sns.lmplot( x="tSNE-2d-1", y="tsne-2d-2", data=df, hue=strainsArr, legend=False)
#    sns.plt.show()
    return strains


def tsne_MPL_Scatter2D_exp(datos, strainsDF):
    #Función que plotea como scatter la tSNE 2D basado en matplotlib
    #Esta sin hacer
    fig, ax = plt.subplots()
    dfD = pd.DataFrame(datos,columns=["tSNE_2d_1", "tSNE_2d_2"])
#    print(datos.shape)
#    print(strainsDF.shape)
    dfS = pd.DataFrame(strainsDF,columns=["Strain", "StrainNumber"])
#    dfS = pd.DataFrame(strainsDF,columns=["Strain"])
    dfT=pd.concat([dfD,dfS], axis=1)
    strains=dfT.Strain.unique()
    for s in strains:
        d=dfT.loc[dfT['Strain'] == s]
        x=d.tSNE_2d_1
        y=d.tSNE_2d_2
        ax.scatter(x, y, label=s)
    ax.legend()
    name = 'plot_images/tSNE_2D_exp' +str(strains)+'_'+'.png'
    plt.savefig(name)
    plt.close()
#    plt.show()
#    dfS = pd.DataFrame(strainsDF,columns=["Strain", "StrainNumber"])
#    sns.lmplot( x="X", y="Y", data=datos, fit_reg=False, hue=strainsArr, legend=False)
#    sns.pairplot( x_vars="tSNE-2d-1", y_vars="tSNE-2d-2", data=dfT, hue="Strain", size=5)
#    sns.lmplot( x="tSNE-2d-1", y="tsne-2d-2", data=df, hue=strainsArr, legend=False)
#    sns.plt.show()
    return strains


def tsne_MPL_Scatter_3D(datos, strainsDF):
    #Función que plotea como scatter la tSNE 3D basado en matplotlib
    
    dfD = pd.DataFrame(datos,columns=["tSNE_3d_1", "tSNE_3d_2", "tSNE_3d_3"])
    dfS = pd.DataFrame(strainsDF,columns=["Strain", "StrainNumber"])
    strains=dfS.Strain.unique()
    dfT=pd.concat([dfD,dfS], axis=1)
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, facecolor="1.0")
    ax = fig.gca(projection='3d')
    for s in strains:
        d=dfT.loc[dfT['Strain'] == s]
        x=d.tSNE_3d_1
        y=d.tSNE_3d_2
        z=d.tSNE_3d_3
        ax.scatter(x, y, z, label=s)
    ax.legend()
    name = 'plot_images/tSNE_3D' +str(strains)+'_'+'.png'
    plt.savefig(name)
    plt.close()
#    plt.show()
#    ax = fig.add_subplot(111, axisbg="1.0", projection='3d')
#    ax.scatter(x, y, z, alpha=0.8, c=color, edgecolors='none', s=30, label=strains)
#    ax.scatter(x, y, z, alpha=0.8, edgecolors='none', s=30, label=strains)
#    sns.lmplot( x="X", y="Y", data=datos, fit_reg=False, hue=strainsArr, legend=False)
#    plt.scatter( x="tSNE-3d-1", y="tSNE-3d-2", z="tSNE-3d-3")
#    sns.lmplot( x="tSNE-2d-1", y="tsne-2d-2", data=df, hue=strainsArr, legend=False)
#    sns.plt.show()
    return strains
    
    
    # choose a color palette with seaborn.
#    num_classes = len(np.unique(strainsArr))
#    txts = np.unique(strainsArr)
#    palette = np.array(sns.color_palette("hls", num_classes))

    # create a scatter plot.
#    f = plt.figure(figsize=(8, 8))
#    ax = plt.subplot(aspect='equal')
#    sc = ax.scatter(datos[:,0], datos[:,1], alpha=0.7, lw=0, s=40, label=strainsArr)
#    sc = ax.scatter(datos[:,0], datos[:,1], alpha=0.7, lw=0, s=40, c=txts, cmap=cm.brg)
#    sc = ax.scatter(datos[:,0], datos[:,1], lw=0, s=40, c=palette[strainsArr.astype(np.int)])
#    plt.xlim(-25, 25)
#    plt.ylim(-25, 25)
#    ax.axis('off')
#    ax.axis('tight')

    # add the labels for each digit corresponding to the label
    
#    txts = []
    
#    for i in range(num_classes):
#
#        # Position of each label at median of data points.
#
#        xtext, ytext = np.median(datos[strainsArr == i, :], axis=0)
#        txt = ax.text(xtext, ytext, str(i), fontsize=24)
#        txt.set_path_effects([
#            PathEffects.Stroke(linewidth=5, foreground="w"),
#            PathEffects.Normal()])
#        txts.append(txt)

#    return f, ax, sc, txts

def apply_tSNE_2D_SB_passages(experimentsP,randSeed):
    
    todosLosPasajes,todaLaInfo, todasS = totalExperimentsToPassages(experimentsP)
    perplex, tStrain = formatS_tSNE(todasS)
    tDTotal2D = apply_2D_tSNE(todosLosPasajes,tStrain,randSeed, perplex)
    tsne_SB_Scatter2D(tDTotal2D,tStrain)
    return


def apply_tSNE_2D_passages(experimentsP,randSeed):
    
    todosLosPasajes,todaLaInfo, todasS = totalExperimentsToPassages(experimentsP)
    perplex, tStrain = formatS_tSNE(todasS)
    tDTotal2D = apply_2D_tSNE(todosLosPasajes,tStrain,randSeed, perplex)
    strains = tsne_MPL_Scatter2D(tDTotal2D,tStrain)
    return strains


def apply_tSNE_2D_pairgrid_passages(experiments,randSeed):
    
    todosLosPasajes,todaLaInfo, todasS = totalExperimentsToPassages(experiments)
    perplex, tStrain = formatS_tSNE(todasS)
    tDTotal3D = apply_3D_tSNE(todosLosPasajes,randSeed,perplex)
    strains = tSNE_SB_Pairgrid(tDTotal3D,todasS)
    return strains

def apply_tSNE_2D_pairplot_passages(experiments,randSeed):
    
    todosLosPasajes,todaLaInfo, todasS = totalExperimentsToPassages(experiments)
    perplex, tStrain = formatS_tSNE(todasS)
    tDTotal3D = apply_3D_tSNE(todosLosPasajes,randSeed,perplex)
    tSNE_Pairplot(tDTotal3D,todasS)
    return


def apply_tSNE_2D_scatterM_passages(experiments,randSeed):
    
    todosLosPasajes,todaLaInfo, todasS = totalExperimentsToPassages(experiments)
    perplex, tStrain = formatS_tSNE(todasS)
    tDTotal3D = apply_3D_tSNE(todosLosPasajes,randSeed,perplex)
    tSNE_PD_scatterM(tDTotal3D,tStrain)
    return


def apply_tSNE_3D_passages(experiments,randSeed):
    
    todosLosPasajes,todaLaInfo, todasS = totalExperimentsToPassages(experiments)
    perplex, tStrain = formatS_tSNE(todasS)
    tDTotal3D = apply_3D_tSNE(todosLosPasajes,randSeed,perplex)
    strains = tsne_MPL_Scatter_3D(tDTotal3D,tStrain)
    return strains


def apply_tSNE_2D_experiments(experiments,randSeed):
    
    todosLosExp, todasLasStr = totalExperimentsToPoints(experiments)
    perplex2, tStrain2 = formatS_tSNE(todasLasStr)
    tDTotalPoints2D = apply_2D_tSNE(todosLosExp,tStrain2,321, perplex2)
    strains = tsne_MPL_Scatter2D_exp(tDTotalPoints2D,tStrain2)
    return strains



    
    
    


