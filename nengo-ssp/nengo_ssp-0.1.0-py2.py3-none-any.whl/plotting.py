import numpy as np
import matplotlib.pyplot as plt
from nengo_ssp.utils import ssp_vectorized, rssp_vectorized
from nengo_ssp.spatial_semantic_pointer import SpatialSemanticPointer
from nengo_spa.semantic_pointer import SemanticPointer

def similarity_plot(X, Y, xs, ys, x=0, y=0, S_list = None, S0 = None, check_mark= False, **kwargs):
    # Heat plot of SSP similarity of x and y values of xs and ys
    # Input:
    #  X, Y - SSP basis vectors
    #  x, y - A single point to compare SSPs over the space with
    #  xs, ys - The x, y points to make the space tiling
    #  titleStr - (optional) Title of plot
    #  S_list - (optional) A list of the SSPs at all xs, ys tiled points (useful for high dim X,Y so that these do not 
    #           have to recomputed every time this function is called)
    #  S0 - (optional) The SSP representing the x, y point (useful if for some reason you want a similarity plot
    #       of tiled SSPs with a non-SSP vector or a SSP with a different basis)
    #  check_mark - (default True) Whether or not to put a black check mark at the x, y location
    xx,yy = np.meshgrid(xs,ys)
    basis = np.vstack([X.v, Y.v]).T
    positions = np.vstack([xx.reshape(-1), yy.reshape(-1)]).T
    position0 = np.array([x,y])
    sim_dots, S_list = _similarity_values(basis,  positions, position0 = position0, S0 = S0, S_list = S_list)
    plt.pcolormesh(xx, yy, sim_dots.reshape(xx.shape).real, **kwargs)
    if check_mark:
        plt.plot(x,y, 'k+')
    return(sim_dots, S_list)

def recursive_similarity_plot(X, Y, xs, ys, recursive_fun, x=0, y=0, S_list = None, S0 = None, check_mark= False, **kwargs):
    # Heat plot of SSP similarity of x and y values of xs and ys
    # Input:
    #  X, Y - SSP basis vectors
    #  x, y - A single point to compare SSPs over the space with
    #  xs, ys - The x, y points to make the space tiling
    #  titleStr - (optional) Title of plot
    #  S_list - (optional) A list of the SSPs at all xs, ys tiled points (useful for high dim X,Y so that these do not 
    #           have to recomputed every time this function is called)
    #  S0 - (optional) The SSP representing the x, y point (useful if for some reason you want a similarity plot
    #       of tiled SSPs with a non-SSP vector or a SSP with a different basis)
    #  check_mark - (default True) Whether or not to put a black check mark at the x, y location
    xx,yy = np.meshgrid(xs,ys)
    basis = np.vstack([X.v, Y.v]).T
    positions = np.vstack([xx.reshape(-1), yy.reshape(-1)]).T
    position0 = np.array([x,y])
    sim_dots, S_list = _recursive_similarity_values(basis,  positions, recursive_fun, position0 = position0, S0 = S0, S_list = S_list)
    plt.pcolormesh(xx, yy, sim_dots.reshape(xx.shape).real, **kwargs)
    if check_mark:
        plt.plot(x,y, 'k+')
    return(sim_dots, S_list)


def similarity_items_plot(M, Objs, X, Y, xs, ys, S_list = None, S0 = None, markers= False, **kwargs):
    # Unbind each object from memory and add together the results - will be a sum of approximate SSPs 
    # representing the location of each object - and plot heat map
    # Run add_item_pts after to get item positions marked
    xx,yy = np.meshgrid(xs,ys)
    basis = np.vstack([X.v, Y.v]).T
    positions = np.vstack([xx.reshape(-1), yy.reshape(-1)]).T
    position0 = np.array([0,0])
    
    sim_dots, S_list = _similarity_values(basis,  positions, position0 = position0, S0 = M * ~Objs[0], S_list = S_list)
    for i in np.arange(1,len(Objs)):
        obj_dots, _ = _similarity_values(basis,  positions, position0 = position0, S0 = M * ~Objs[i], S_list = S_list)
        sim_dots += obj_dots
    plt.pcolormesh(xx, yy, sim_dots.reshape(xx.shape).real, cmap='viridis')
    if markers:
        _add_item_pts(kwargs['item_locations'], kwargs['items_markers'], kwargs['items_cols'])
    
    
def _add_item_pts(item_locations, items_markers, items_cols):
    # Add items to plot at locations with marker symbols and colors given
    for i in np.arange(item_locations.shape[0]):
        plt.scatter(item_locations[i,0],item_locations[i,1],
                marker=items_markers[i],s=60,c=items_cols[i],edgecolors='w')
        
def _similarity_values(basis, positions, position0 = None, S0 = None, S_list = None):
    if position0 is None:
        position0 = np.zeros(basis.shape[1])
    if S0 is None:
        S0 = ssp_vectorized(basis, position0)
    if S_list is None: 
        S_list = ssp_vectorized(basis, positions)
    sim_dots = S_list.T @ S0
    return(sim_dots, S_list)


def _recursive_similarity_values(basis, positions, recursive_fun, position0 = None, S0 = None, S_list = None):
    if position0 is None:
        position0 = np.zeros(basis.shape[1])
    if S0 is None:
        S0 = rssp_vectorized(basis, position0, recursive_fun)
    elif (type(S0) == SpatialSemanticPointer) | (type(S0) == SemanticPointer):
        S0 = S0.v
    if S_list is None: 
        S_list = rssp_vectorized(basis, positions, recursive_fun)
    sim_dots = S_list.T @ S0
    return(sim_dots, S_list)