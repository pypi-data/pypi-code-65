# -*- coding: utf-8 -*-

import numpy as np

from genepy3d.obj.points import Points
from genepy3d.obj.curves import Curve
from genepy3d.util.geo import l2
from genepy3d.interact import pointsurface

def intersect(crv, surf):
    """Intersection between curve and surface.
    
    Args:
        crv (Curve): curve object.
        surf (Surface): surface object.
        
    Return:
       intersected points and their corresponding curve segments.
        
    TODO: remove lflag. Not useful.
        
    """
    
    from CGAL.CGAL_Kernel import Point_3, Segment_3, Triangle_3
    from CGAL.CGAL_AABB_tree import AABB_tree_Triangle_3_soup
    
    plst = [] # intersected point list
    lflag = [] # intersected line segment flag
    crvseglst = [] # curve segment where intersected point lying on
    
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
    
    # searching intersection between each curve segment and surf.
    for i in range(len(crv.coors)-1):
        # get segment query
        p1 = Point_3(float(crv.coors[i][0]),float(crv.coors[i][1]),float(crv.coors[i][2]))
        p1coors = np.array([p1.x(),p1.y(),p1.z()])
        p2 = Point_3(float(crv.coors[i+1][0]),float(crv.coors[i+1][1]),float(crv.coors[i+1][2]))
        segment_query = Segment_3(p1,p2)
        
        subpntlst = [] # intersected points
        subpntdst = [] # distance from intersected points to p1 (for sorting)
        sublflag = [] # intersected line flag
        subcrvseglst = []
        
        if tree.do_intersect(segment_query):
            intersections = []
            tree.all_intersections(segment_query,intersections)
            for inter in intersections:
                if inter[0].is_Point_3():
                    p = inter[0].get_Point_3()
                    pcoors = np.array([p.x(),p.y(),p.z()])
                    subpntdst.append(l2(p1coors,pcoors))
                    subpntlst.append(pcoors)
                    sublflag.append(False)
                    subcrvseglst.append(i)
                elif inter[0].is_Segment_3():
                    l = inter[0].get_Segment_3()
                    for j in [0,1]:
                        p = l.vertex(j)
                        pcoors = np.array([p.x(),p.y(),p.z()])
                        subpntdst.append(l2(p1coors,pcoors))
                        subpntlst.append(pcoors)
                        sublflag.append(True)
                        subcrvseglst.append(i)
        
        if len(subpntdst)>0:
            # remove duplicates (strange thing in CGAL) 
            subpntlst, uix = np.unique(np.array(subpntlst),axis=0,return_index=True)
            subpntdst = np.array(subpntdst)[uix]
            sublflag = np.array(sublflag)[uix]
            subcrvseglst = np.array(subcrvseglst)[uix]
            
            # sorting
            sortix = np.argsort(subpntdst)
            subpntlst = subpntlst[sortix]
            sublflag = sublflag[sortix]
            subcrvseglst = subcrvseglst[sortix]
            
            plst = plst + subpntlst.tolist()
            lflag = lflag + sublflag.tolist()
            crvseglst = crvseglst + subcrvseglst.tolist()
    
    # remove duplicates
    if len(plst)>0:
        _, uix = np.unique(np.array(plst),axis=0,return_index=True)
        plst = np.array(plst)[np.sort(uix)]
        lflag = np.array(lflag)[np.sort(uix)]
        crvseglst = np.array(crvseglst)[np.sort(uix)]
        return (Points(plst), crvseglst)
    else:
        return (None, None)

def inonout(crv,surf):
    """Return curve segments inside/lying on/outside of the surface.
    
    Args:
        crv (Curve): curve object.
        surf (Surface): surface object.
        
    Return:
        inside, onside and outside curve lists.
    
    """
    
    # get intersection between crv and surf
    intpnts, crvseglst = intersect(crv,surf)
    
    if intpnts is None: # no intersection
        return ([],[],[])
    else:
        incoors, oncoors, outcoors = [], [], []
        
        # add intersected points to curve points (here all points are ordered)
        fullpntlst = []
        for i in range(len(crv.coors)-1):
            fullpntlst.append(crv.coors[i].tolist())
            ix = np.argwhere(crvseglst==i).flatten()
            if len(ix)!=0:
                fullpntlst = fullpntlst + intpnts.coors[ix].tolist()
        fullpntlst.append(crv.coors[-1].tolist())
        
        # remove duplicate
        _, uix = np.unique(np.array(fullpntlst),axis=0,return_index=True)
        fullpntlst = np.array(fullpntlst)[np.sort(uix)]
#        print(fullpntlst)
        
        # middle points between two points of fullpntlst
        checkpntlst = (fullpntlst[:-1]+fullpntlst[1:])/2.
#        print(checkpntlst)
        
        # check middle points lying on the surf
        inside, onside, outside = pointsurface.inonout(Points(checkpntlst),surf,return_flag=True)
#        print(inside)
#        print(onside)
#        print(outside)
        
        # assignment
        subincoors, suboncoors, suboutcoors = [], [], []
        prevflag = "none" # previous curve segment label
        for i in range(len(fullpntlst)-1):
            if inside[i]==True:
                if prevflag == "inside":
                    subincoors = subincoors + fullpntlst[i:i+2].tolist()
                else:
                    subincoors = []
                    subincoors = subincoors + fullpntlst[i:i+2].tolist()
                    if (prevflag=="onside")&(len(suboncoors)!=0):
                        _, uix = np.unique(np.array(suboncoors),axis=0,return_index=True)
                        suboncoors = np.array(suboncoors)[np.sort(uix)]
                        oncoors.append(Curve(suboncoors))
                    elif (prevflag=="outside")&(len(suboutcoors)!=0):
                        _, uix = np.unique(np.array(suboutcoors),axis=0,return_index=True)
                        suboutcoors = np.array(suboutcoors)[np.sort(uix)]
                        outcoors.append(Curve(suboutcoors))
                    prevflag = "inside"
            elif onside[i]==True:
                if prevflag == "onside":
                    suboncoors = suboncoors + fullpntlst[i:i+2].tolist()
                else:
                    suboncoors = []
                    suboncoors = suboncoors + fullpntlst[i:i+2].tolist() 
                    if (prevflag=="inside")&(len(subincoors)!=0):
                        _, uix = np.unique(np.array(subincoors),axis=0,return_index=True)
                        subincoors = np.array(subincoors)[np.sort(uix)]
                        incoors.append(Curve(subincoors))
                    elif (prevflag=="outside")&(len(suboutcoors)!=0):
                        _, uix = np.unique(np.array(suboutcoors),axis=0,return_index=True)
                        suboutcoors = np.array(suboutcoors)[np.sort(uix)]
                        outcoors.append(Curve(suboutcoors))
                    prevflag = "onside"
            else:
                if prevflag == "outside":
                    suboutcoors = suboutcoors + fullpntlst[i:i+2].tolist()
                else:
                    suboutcoors = []
                    suboutcoors = suboutcoors + fullpntlst[i:i+2].tolist() 
                    if (prevflag=="inside")&(len(subincoors)!=0):
                        _, uix = np.unique(np.array(subincoors),axis=0,return_index=True)
                        subincoors = np.array(subincoors)[np.sort(uix)]
                        incoors.append(Curve(subincoors))
                    elif (prevflag=="onside")&(len(suboncoors)!=0):
                        _, uix = np.unique(np.array(suboncoors),axis=0,return_index=True)
                        suboncoors = np.array(suboncoors)[np.sort(uix)]
                        oncoors.append(Curve(suboncoors))
                    prevflag = "outside"
                    
        # last check
        if (prevflag=="inside")&(len(subincoors)!=0):
            _, uix = np.unique(np.array(subincoors),axis=0,return_index=True)
            subincoors = np.array(subincoors)[np.sort(uix)]
            incoors.append(Curve(subincoors))
        elif (prevflag=="onside")&(len(suboncoors)!=0):
            _, uix = np.unique(np.array(suboncoors),axis=0,return_index=True)
            suboncoors = np.array(suboncoors)[np.sort(uix)]
            oncoors.append(Curve(suboncoors))
        elif (prevflag=="outside")&(len(suboutcoors)!=0):
            _, uix = np.unique(np.array(suboutcoors),axis=0,return_index=True)
            suboutcoors = np.array(suboutcoors)[np.sort(uix)]
            outcoors.append(Curve(suboutcoors))
        
        return (incoors,oncoors,outcoors)
                
                
                
                
    
            
            
    
    


    





















