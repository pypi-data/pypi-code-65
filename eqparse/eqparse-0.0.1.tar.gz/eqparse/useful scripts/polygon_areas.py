'''
a series of functions allowing user to collect schedule objects
from either an inp file or from an xl file, and
update existing values into new inpfile.

'''
from collections import OrderedDict
import pandas as pd
import inp.objects as objects


def irrpolyarea(coords):
    '''returns area from polygon'''
    t=0
    for count in range(len(coords)-1):
        y = coords[count+1][1] + coords[count][1]
        x = coords[count+1][0] - coords[count][0]
        z = y * x
        t += z
    return abs(t/2.0)

def getpolyarea(dictname):
    '''returns ordered dictionary of 
    polygon names as keys, areas as values
    '''
    polyareadict = OrderedDict()
    for k1, v1 in dictname.items():
        polydict = OrderedDict() 
        for k2, v2 in v1.items():
            if "POLYGON" not in v2 and "parent" not in k2:
                strip = v2.strip("(").strip(")").strip()
                splitter = strip.split(", ")
                splitter = [float(s) for s in splitter]
                polydict[k2] =  splitter
                polylist = list(polydict.values())            
        area = round(irrpolyarea(polylist),2)
        key = [k for k in v1.keys()][0]
    #    print (key)
        polyareadict[key] = area
    return polyareadict


def area_spc_dict(spacedict,polygondict):
    '''concatenates dict of space areas
    to spaces'''
    spaceareasdict = OrderedDict()
    for k1, v1 in spacedict.items():
        if v1['SHAPE'] == 'BOX':
            spaceareasdict[k1] = float(spacedict[k1]["WIDTH"]) * float(spacedict[k1]["WIDTH"])
        else:
            if v1['SHAPE'] == 'POLYGON':
                try:
                    polyname = v1["POLYGON"]#.strip("\"")
                    space_area = polygondict[polyname]
                    spaceareasdict[k1] = space_area
                except:
                    pass
        
    return spaceareasdict 



