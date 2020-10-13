import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import numpy as np

def to_CGAL(pnts):
    """Return the points as a list of CGAL Point_3 objects, for use in CGAL aglorithms.
                            
    Returns:
        a list of CGAL.Point_3 objects
    
    """
    
    from CGAL.CGAL_Kernel import Point_3
    
     #import CGAL? needs to be done from the caller, TODO: test that it's done
    return [Point_3(pnts.coors[i,0],pnts.coors[i,1],pnts.coors[i,2]) for i in range(len(pnts.coors))]

def process(pnts,removed_percentage = 5.0,nb_neighbors = 24, smooth=True):
    
    from genepy3d.io.points import Points    
    from CGAL.CGAL_Point_set_processing_3 import remove_outliers,jet_smooth_point_set

    pointsCgal= to_CGAL(pnts)
     
    if removed_percentage:
        new_size=remove_outliers(pointsCgal, nb_neighbors, removed_percentage)
        pointsCgal=pointsCgal[0:new_size]
        
    if smooth:
        jet_smooth_point_set(pointsCgal,nb_neighbors)

    return Points(np.array([[p.x(),p.y(),p.z()] for p in pointsCgal]))
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
