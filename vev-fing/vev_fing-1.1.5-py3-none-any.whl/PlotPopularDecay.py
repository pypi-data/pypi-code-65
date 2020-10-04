import numpy as np
import matplotlib.pyplot as plt

def plotPopularDecay(df):
    #Busco el valor del primer pasaje
    minPassage=df['Passage'].min()
    
    #Busco los pasajes
    passages=df['Passage'].unique()
    
    #Obtengo la info
    info_df=str(df['info'].iloc[0])
    strain_df=info_df.split(',')[0]
    repetition_df=info_df.split(',')[1]
    
    #Busco el valor de las posiciones en el dataframe
    posVal=df.Position.unique()

    
    #Busco los valores de las probs. para el primer pasaje
    dfFirstPassage=df[df.Passage.eq(minPassage)]
    dfFirstPassage_val=dfFirstPassage[dfFirstPassage.Position.isin(posVal)].copy()
    dfFirstPassage_val_aux=dfFirstPassage_val.drop(['Position','Coverage','Passage','Strain','Repetition','info'], axis=1)
    maxColumnsCodon=dfFirstPassage_val_aux.idxmax(axis=1)
    dfFirstPassage_val['MaxFreqCodon']=maxColumnsCodon
    dfFirstPassage_val=dfFirstPassage_val[['Position','MaxFreqCodon']]
    return dfFirstPassage_val
#    pos=366
#    maxF=dfFirstPassage_val.loc[dfFirstPassage_val['Position'] == pos].MaxFreq.astype(str)
#    print('Codon: ',maxF)
#    freqEvol=df.loc[df['Position']==pos]#.columns.str.startswith('ATT')
#    freqEvol=freqEvol[maxF.astype(str)]
    plt.figure(1)
#    curve=[]
    for pos in dfFirstPassage_val['Position']:
        maxF_Cod=dfFirstPassage_val.loc[dfFirstPassage_val['Position'] == pos].MaxFreqCodon.astype(str)
        freqEvol=df.loc[df['Position']==pos]
        freqEvol=freqEvol[maxF_Cod.astype(str)]
        freqEvol=np.array(freqEvol)
        if (np.amin(freqEvol)<th):
            str_label=str(pos)+' - '+str(maxF_Cod.values.item())
#            print(maxF_Cod)
            plt.plot(passages,freqEvol, label=str_label)
            plt.legend(loc='best',borderaxespad=0., title='Posición - Codón')
#            print(str(pos))
#            print(str(maxF_Cod))
#            plt.text(freqEvol[0],np.amin(freqEvol),str_label)
#            item=[pos,maxF,freqEvol]
#            print('Minima frecuencia: ',np.amin(freqEvol))
#            curve.append(item)
    
        
#        print('Position: ',pos)
#        print('Codon: ',maxF)
    plt.xlabel('Passages')
    plt.ylabel('Frequencies')

        
#    curveArray=np.array(curve)
#    return curveArray


    
    
    
