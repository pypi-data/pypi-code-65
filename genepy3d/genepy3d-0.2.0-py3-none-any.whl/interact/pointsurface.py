import numpy as np

from genepy3d.obj.points import Points
from genepy3d.util.geo import l2

def inonout(pnts,surf,extreme_coors=None,return_flag=False):
    """Check points inside, lying on or outside of the surface.
    
    https://en.wikipedia.org/wiki/Point_in_polygon
    
    Args:
        pnts (Points): points object.
        surf (Surface): surface object.
        
    Returns:
        if return_flag is True, then three flags where True marks point inside/lying on/outside of the surface.
        Else return three Points objects for inside, onside and outside of the surf.
    
    """
    
    from CGAL.CGAL_Kernel import Point_3, Ray_3, Triangle_3
    from CGAL.CGAL_AABB_tree import AABB_tree_Triangle_3_soup
    
    # get list of triangles from surf
    triangles = []
    for i in range(len(surf.simplices)):
        coors = surf.vertices[surf.simplices[i,0]]
        p1 = Point_3(float(coors[0]), float(coors[1]), float(coors[2]))
        coors = surf.vertices[surf.simplices[i,1]]
        p2 = Point_3(float(coors[0]), float(coors[1]), float(coors[2]))
        coors = surf.vertices[surf.simplices[i,2]]
        p3 = Point_3(float(coors[0]), float(coors[1]), float(coors[2]))
        triangles.append(Triangle_3(p1,p2,p3))
        
    # initialize AABB tree for surf
    tree = AABB_tree_Triangle_3_soup(triangles)
    
    # a point far from surface
    if extreme_coors is None:
        extcoors = np.max(surf.vertices,axis=0)*1.5
    else:
        extcoors = extreme_coors
    
    extp = Point_3(float(extcoors[0]),float(extcoors[1]),float(extcoors[2]))
    
    inside_flag = np.zeros(len(pnts.coors),dtype=np.bool)
    onside_flag = np.zeros(len(pnts.coors),dtype=np.bool)
    outside_flag = np.zeros(len(pnts.coors),dtype=np.bool)
    
    for i in range(len(pnts.coors)):
        x, y, z = tuple(pnts.coors[i])
        p = Point_3(float(x),float(y),float(z))
        
        if(tree.squared_distance(p)==0):
            onside_flag[i] = True
        else:
            intersected_pnts = [] # intersected points with surface
            intersected_dst = [] # distance from extcoors to intersected points
            
            ray_query = Ray_3(extp,p)
            if tree.do_intersect(ray_query):
                intersections = []
                tree.all_intersections(ray_query,intersections)
                for inter in intersections:
                    if inter[0].is_Point_3(): # point intersection
                        tmp = inter[0].get_Point_3()
                        interp = np.array([tmp.x(),tmp.y(),tmp.z()])
                        if all(interp[i] in surf.vertices[:,i] for i in range(3)):
                            continue
                    # elif inter[0].is_Segment_3(): # line segment intersection
                    #     l = inter[0].get_Segment_3()
                    #     p1 = np.array([l.vertex(0).x(),l.vertex(0).y(),l.vertex(0).z()])
                    #     p2 = np.array([l.vertex(1).x(),l.vertex(1).y(),l.vertex(1).z()])
                    #     if l2(p1,extcoors)<l2(p2,extcoors):
                    #         interp = p1
                    #     else:
                    #         interp = p2
                            
                        intersected_dst.append(l2(interp,extcoors))
                        intersected_pnts.append(interp)
            
            # remove duplicates (strange thing in CGAL)      
            if len(intersected_pnts)>0:
                intersected_pnts, uix = np.unique(np.array(intersected_pnts),axis=0,return_index=True)
                intersected_dst = np.array(intersected_dst)[uix]
            
            if len(intersected_pnts)==0:
                outside_flag[i] = True
            else:
                sortix = np.argsort(intersected_dst)
                intersected_pnts = intersected_pnts[sortix]
                intersected_dst = intersected_dst[sortix]
                
                for j in range(len(intersected_pnts)):
                    # check if checking point from point cloud is within even/odd intersected segment
                    if l2(extcoors,pnts.coors[i]) < l2(extcoors,intersected_pnts[j]):
                        if j % 2 != 0: # if odd segment
                            inside_flag[i] = True
                        else:
                            outside_flag[i] = True
                        break
                
                # check the last j
                last_j = len(intersected_pnts)-1
                if l2(extcoors,pnts.coors[i]) > l2(extcoors,intersected_pnts[last_j]):
                    if last_j % 2 == 0: # inverse conditions
                        inside_flag[i] = True
                    else:
                        outside_flag[i] = True
    
    if return_flag==False:
        pnts_in, pnts_on, pnts_out = None, None, None
        if len(pnts.coors[inside_flag])>0:
            pnts_in = Points(pnts.coors[inside_flag])
        if len(pnts.coors[onside_flag])>0:
            pnts_on = Points(pnts.coors[onside_flag])
        if len(pnts.coors[outside_flag])>0:
            pnts_out = Points(pnts.coors[outside_flag])
        return (pnts_in,pnts_on,pnts_out)
    else:
        return (inside_flag,onside_flag,outside_flag)
            
        
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
