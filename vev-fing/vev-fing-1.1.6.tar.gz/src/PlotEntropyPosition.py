import matplotlib.pyplot as plt
import os
pathPip=str(os.path.dirname(plt.__file__)).split('matplotlib')[0]

def plotEntropyPosition(position, dataFrame,strain,repetition,color = 'red'):
    passage=dataFrame.loc[dataFrame.Position==position,'Passage']
    entropy=dataFrame.loc[dataFrame.Position==position,'Entropy']
    fig1, ax = plt.subplots()
    ax.plot(passage, entropy,color=color)
    ax.set_xlabel('Passages')
    ax.set_ylabel('Entropy')
    ax.set_title("Entropy over passages for position "+str(position))
    plt.grid()
    name =pathPip+ 'src/plot_images/Entropy_' + str(position) +'_'+strain+'_'+repetition+ '.png'
    plt.savefig(name)
    plt.close()


def plotEntropiesPosition(position, dataFrames):
    fig1, ax = plt.subplots()
    for df in dataFrames:
        passage=df.loc[df.Position==position,'Passage']
        entropy = df.loc[df.Position == position, 'Entropy']
        ax.plot(passage, entropy)
    ax.set_xlabel('Passages')
    ax.set_ylabel('Entropy')
    ax.set_title("Entropy over passages for position " + str(position))
    plt.grid()
    name = pathPip+'src/plot_images/Entropy_' + str(position) +'.png'
    plt.savefig(name)
    plt.close()

    
    
    
