def from_points_surface_reconstruction(points): # TODO
    """Create surface object from point cloud via CGAL surface reconstruction algorithms.
    
    Args:
        afile (string): path to load
    
    Returns:
        a Surface object
    """       
    return

# def from_points_alpha_shape(points,alpha=None):
#     """Create surface object from point cloud via CGAL alpha-shape algorithms. if 'alpha is none, it id estimated as the smallest alpha that gives a single connected component. the estimated surface is formes by the triangles of the regularised alpha-complex facing outward.
  
#     Args:
#         points (nx3 array of float): coordinates of point cloud
#         alpha (float): value of alpha
    
#     Returns:
#         a Surface object
#     """
    
#     from genepy3d.obj.surfaces import Surface
    
#     from CGAL import CGAL_genepy3d
#     from CGAL.CGAL_Kernel import Point_3
#     from CGAL import CGAL_Point_set_processing_3 as psp

#     pointsCGAL= []
#     pointsCGALas= []
#     pointsCGALastri= []
#     for i in range(points.shape[0]):
#         pointsCGAL.append(Point_3(points[i,0],points[i,1],points[i,2]))
    
#     psp.jet_smooth_point_set(pointsCGAL,24)
#     if alpha is not None:
#         CGAL_genepy3d.getAlphaShape(pointsCGAL,pointsCGALas,pointsCGALastri,alpha)
#     else :
#         alpha=CGAL_genepy3d.getOptimalAlphaShape(pointsCGAL,pointsCGALas,pointsCGALastri)
#     # print('alpha:'+str(alpha))
#     simplicesc=np.array([tuple([p.x(),p.y(),p.z()]) for t in pointsCGALastri for p in [t.vertex(0),t.vertex(1),t.vertex(2)] ])
#     vertices=list({tuple(x) for x in [simplicesc[i,:] for i in range(len(simplicesc))]})
#     simplices=[vertices.index(tuple(simplicesc[i])) for i in range(len(simplicesc))]
#     simplices=np.reshape(np.array(simplices),(-1,3))
    
#     return Surface(np.array(vertices), simplices)

# def get_optimal_alpha_shape(points):
#     """Return optimal alpha shape parameter from point cloud using CGAL.
    
#     Args:
#         points (nx3 array of float): coordinates of point cloud.
    
#     Returns:
#         alpha value.
    
#     """
    
#     from CGAL import CGAL_genepy3d
#     from CGAL.CGAL_Kernel import Point_3
#     from CGAL import CGAL_Point_set_processing_3 as psp
    
#     pointsCGAL= []
#     pointsCGALas= []
#     pointsCGALastri= []
#     for i in range(points.shape[0]):
#         pointsCGAL.append(Point_3(points[i,0],points[i,1],points[i,2]))
        
#     psp.jet_smooth_point_set(pointsCGAL,24)
    
#     return CGAL_genepy3d.getOptimalAlphaShape(pointsCGAL,pointsCGALas,pointsCGALastri)


