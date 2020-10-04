import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import os

pathPip=str(os.path.dirname(np.__file__)).split('numpy')[0]

def getEntropySurface(dataFrame,strain,repetition):

    positions=np.array(dataFrame['Position'].astype(int))
    passages=np.array(dataFrame['Passage'].astype(int))
    entropy=np.array(dataFrame['Entropy'])


    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.grid(True)

    Y = positions/3

    X = passages


    Z = entropy


    surf = ax.plot_trisurf(X, Y, Z,  cmap='viridis')

    ax.zaxis.set_major_locator(LinearLocator(10))
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

# Add a color bar which maps values to colors.
    fig.colorbar(surf, shrink=0.5, aspect=5)



    ax.set_xlabel('Passages')
    ax.set_ylabel('Positions')
    ax.set_zlabel('Entropy')

    name =pathPip+ 'src/plot_images/entropySurface_' +strain+'_' +repetition+ '.png'
    plt.savefig(name, transparent=True)
    plt.close()


def getEntropySurface_Filtrados(df,strain,repetition):

    pos = df['Position'].unique()
    pos = list(map(int, pos))

    df_C=df.copy()
    df_C.drop(df_C.columns[[-3, -2, -1]], axis=1, inplace=True)

    passages = df_C.columns
    passages = list(map(int, passages))

    entropy = df_C.values

    X, Y = np.meshgrid(passages, pos)

    fig = plt.figure()
    ax = fig.gca(projection='3d')

    surf = ax.plot_surface(X, Y, entropy, rstride=1, cstride=1, cmap='viridis', linewidth=1, antialiased=True)
#    surf = ax.plot_surface(X, Y, entropy, linewidth=0, antialiased=False)

    fig.colorbar(surf, shrink=0.5, aspect=5)

#    plt.show()

    return fig
