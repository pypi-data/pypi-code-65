import pandas as pd
import math
import matplotlib.pyplot as plt
import scipy
import os



def dgumbel(x,mu,s): #density function
    return math.exp((mu - x)/s - math.exp((mu - x)/s))/s

def pgumbel(q,mu,s): #distribution function
    return math.exp(-(math.exp(-((q - mu)/s))))

def qgumbel(p,mu,s): #Quantile function
    return (mu - s) * math.log(-math.log(p))

def gumbelPlot(df,strain,repetition):
    dataframe= extraerMaximos(df)
    gumbelAdjust(dataframe,strain,repetition)

def extraerMaximos(df):
    df_positions =df.Position.unique()

    entropies = []
    i=0
    for position in df_positions:
        entropy=df.loc[df.Position==position,'Entropy'].max(axis=0)
        entropies.append(entropy)
        i=i+1
    df = pd.DataFrame(entropies)

    return df

def get_hist(ax):
    n,bins = [],[]
    for rect in ax.patches:
        ((x0, y0), (x1, y1)) = rect.get_bbox().get_points()
        n.append(y1-y0)
        bins.append(x0) # left edge of each bin
    bins.append(x1) # also get right edge of last bin

    return n,bins




def gumbelAdjust(dfMax,strain,repetition):
    pathPip=str(os.path.dirname(pd.__file__)).split('pandas')[0]
    #fig, ax = plt.subplots()

    sub = dfMax.quantile(.95, axis = 0)
    quantil= sub.iloc[0]
    listDF = dfMax.values.tolist()
    subsample=[]
    for value in listDF:
        if value[0] <= quantil:
            subsample.append(value)
    dfHist = pd.DataFrame(subsample)
    dfHist.columns=['Entropy']
    axsub=dfHist['Entropy'].hist(bins=20,grid=False, xlabelsize=12, ylabelsize=12, density=True)
    n, bins = get_hist(axsub)


    plt.xlabel("Entropy", fontsize=15)
    plt.ylabel("Frequency", fontsize=15)
    plt.xlim([0.0, 0.2])
    mu, sigma = scipy.stats.norm.fit(subsample)

    x=[]

    y=[]
    for point in bins:
        x.append(point)
        a=dgumbel(point,mu,sigma)
        y.append(a)
        #plt.plot(a,x,'bo')
        #aux=aux+sum
    plt.plot(x,y, 'r-', label='density gumbel', linewidth=1)
    name = pathPip+'src/plot_images/Gumbel'+'_'+strain+'_'+repetition + '.png'
    plt.savefig(name)
    plt.close()



