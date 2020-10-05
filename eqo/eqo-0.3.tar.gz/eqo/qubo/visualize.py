import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from .analyze      import naive_1opt, randkopt
from .qubotools    import toMatrix
from matplotlib.cm import bwr
#from shiftedcolormap import shiftedColorMap
from tqdm          import trange

import matplotlib
from mpl_toolkits.axes_grid1 import AxesGrid


def draw_graph(Q):
    n = Q.n

    maxField = max(np.abs(Q[(i,)])   for i    in range(n))
    maxW     = max(np.abs(Q[(i, j)]) for i, j in itertools.combinations(range(n), r=2))
    
    scaleField = 500.0 / maxField
    scaleW     = 20.0 / maxW
    
    G = nx.Graph()
    for i in range(n):
        G.add_node(i, weight=np.abs(Q[(i,)]), neg=(Q[(i,)]<0))
                   
    for i, j in itertools.combinations(range(n), r=2):
        G.add_edge(i, j, weight=np.abs(Q[(i, j)]), neg=(Q[(i,j)]<0))

    posNodes = [ i for (i, d) in G.nodes(data=True) if not d['neg'] ]
    negNodes = [ i for (i, d) in G.nodes(data=True) if     d['neg'] ]
    posEdges = [ (i, j) for (i, j, d) in G.edges(data=True) if not d['neg'] ]
    negEdges = [ (i, j) for (i, j, d) in G.edges(data=True) if     d['neg'] ]
              
    pos = nx.spring_layout(G, iterations=200)
    nx.draw_networkx_nodes(G, pos, nodelist=posNodes, node_size=[ G.nodes()[i]['weight'] * scaleField for i in posNodes ], node_color='b')
    nx.draw_networkx_nodes(G, pos, nodelist=negNodes, node_size=[ G.nodes()[i]['weight'] * scaleField for i in negNodes ], node_color='r')
    nx.draw_networkx_edges(G, pos, edgelist=posEdges, width=[ G[i][j]['weight'] * scaleW for (i, j) in posEdges ], edge_color='b', alpha=0.5)
    nx.draw_networkx_edges(G, pos, edgelist=negEdges, width=[ G[i][j]['weight'] * scaleW for (i, j) in negEdges ], edge_color='r', alpha=0.5)
    
    plt.axis('off')
    plt.show()

def histogram(Q, bins='auto'):   
    plt.hist(x=Q.values(), bins=bins)
    plt.xlabel(r'Coefficient value $\beta$')
    plt.ylabel('Frequency')
    plt.show()
    
    


def shiftedColorMap(cmap, start=0, midpoint=0.5, stop=1.0, name='shiftedcmap'):
    '''
    Function to offset the "center" of a colormap. Useful for
    data with a negative min and positive max and you want the
    middle of the colormap's dynamic range to be at zero.

    Input
    -----
      cmap : The matplotlib colormap to be altered
      start : Offset from lowest point in the colormap's range.
          Defaults to 0.0 (no lower offset). Should be between
          0.0 and `midpoint`.
      midpoint : The new center of the colormap. Defaults to 
          0.5 (no shift). Should be between 0.0 and 1.0. In
          general, this should be  1 - vmax / (vmax + abs(vmin))
          For example if your data range from -15.0 to +5.0 and
          you want the center of the colormap at 0.0, `midpoint`
          should be set to  1 - 5/(5 + 15)) or 0.75
      stop : Offset from highest point in the colormap's range.
          Defaults to 1.0 (no upper offset). Should be between
          `midpoint` and 1.0.
    '''
    
    cdict = {
        'red': [],
        'green': [],
        'blue': [],
        'alpha': []
    }

    # regular index to compute the colors
    reg_index = np.linspace(start, stop, 257)

    # shifted index to match the data
    shift_index = np.hstack([
        np.linspace(0.0, midpoint, 128, endpoint=False), 
        np.linspace(midpoint, 1.0, 129, endpoint=True)
    ])

    for ri, si in zip(reg_index, shift_index):
        r, g, b, a = cmap(ri)

        cdict['red'].append((si, r, r))
        cdict['green'].append((si, g, g))
        cdict['blue'].append((si, b, b))
        cdict['alpha'].append((si, a, a))

    newcmap = matplotlib.colors.LinearSegmentedColormap(name, cdict)
    plt.register_cmap(cmap=newcmap)

    return newcmap
    
def heatmap(Q, symmetric=False):
    m = toMatrix(Q, symmetric)
          
    vmin, vmax = np.min(m), np.max(m)
    #vabsmax    = max(abs(vmin), abs(vmax))
    shrunk_cmap = shiftedColorMap(bwr, midpoint=1.0/(1.0-(vmax/vmin))) # TODO: shrink properly
    h = plt.imshow(m, cmap=shrunk_cmap, interpolation='nearest')
    plt.colorbar(h)
    plt.show()


def fitness_distance_plot(Q, x_opt, local_optima=1000, output='fitness_distance_plot.pdf'):

    val_opt = Q.value(x_opt)
    x_opt_  = np.fromiter(x_opt.values(), dtype=np.int64) if isinstance(x_opt, dict) else x_opt

    hamming_dist = lambda u, v: np.linalg.norm(u-v, 0)

    dists = np.empty(local_optima, dtype=np.int64)
    vals  = np.empty(local_optima, dtype=np.float64)

    for i in trange(local_optima):
        x_local_opt = naive_1opt(Q, np.random.binomial(1, 0.5, Q.n)) #randkopt(Q)
        val = Q.value(x_local_opt)
        dists[i] = hamming_dist(x_opt_, x_local_opt)
        vals[i] = val_opt - val

    print(np.c_[dists, vals])

    plt.scatter(x=dists, y=vals)
    plt.xlabel('Hamming distance to optimum')
    plt.ylabel('Fitness difference')
    plt.savefig(output)
