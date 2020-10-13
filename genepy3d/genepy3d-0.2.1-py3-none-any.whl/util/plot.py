import numpy as np

def plot_line(ax,projection,x,y,z,scales=(1.,1.,1.),line_args={}):
    """Support plotting a line.
    
    Args:
        ax: axis to be plotted.
        projection (str): support *3d, xy, xz, yz*.
        x (float): x coordinate.
        y (float): y coordinate.
        z (float): z coordinate.
        scales (tuple of float): axis scales.
        line_args (dic): matplotlib args for line plot.
    
    """
    
    x = x / scales[0]
    y = y / scales[1]
    z = z / scales[2]
    
    if projection=='3d':
        pl = ax.plot(x,y,z,**line_args)
    else:
        if projection=='xy':
            _x, _y = x, y
        elif projection=='xz':
            _x, _y = x, z
        else:
            _x, _y = y, z
            
        pl = ax.plot(_x,_y,**line_args)
        
    return pl
    
def plot_point(ax,projection,x,y,z,scales=(1.,1.,1.),point_args={}):
    """Support plotting points.
    
    Args:
        ax: axis to be plotted.
        projection (str): support *3d, xy, xz, yz*.
        x (float): x coordinate.
        y (float): y coordinate.
        z (float): z coordinate.
        scales (tuple(float)): axis scales.
        point_args (dic): matplotlib args for points plot.
    
    """
    
    x = x / scales[0]
    y = y / scales[1]
    z = z / scales[2]
    
    if projection=='3d':
        pl = ax.scatter(x,y,z,**point_args)
    else:
        if projection=='xy':
            _x, _y = x, y
        elif projection=='xz':
            _x, _y = x, z
        else:
            _x, _y = y, z
            
        pl = ax.scatter(_x,_y,**point_args)
        
    return pl


def fix_equal_axis(data):
    """Fix equal axis bug in matplotlib 3d plot.
    
    Args:
        data (array of float): 3D points.
        
    Returns:
        min and max values in each axis.    
    
    """
    x, y, z = data[:,0], data[:,1], data[:,2]
    scalex = x.max()-x.min()
    scaley = y.max()-y.min()
    scalez = z.max()-z.min()
    maxscale = np.round(np.max(np.array([scalex,scaley,scalez])))/2
    xmed,ymed,zmed = np.median(x),np.median(y),np.median(z)
    scale_params = {}
    scale_params['xmin'] = xmed-maxscale
    scale_params['xmax'] = xmed+maxscale
    scale_params['ymin'] = ymed-maxscale
    scale_params['ymax'] = ymed+maxscale
    scale_params['zmin'] = zmed-maxscale
    scale_params['zmax'] = zmed+maxscale
    
    return scale_params