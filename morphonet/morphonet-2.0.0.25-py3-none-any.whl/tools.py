# -*- coding: latin-1 -*-
import os,sys
import numpy as np
import datetime
#****************************************************************** SPECIFC ASTEC FUNCTIONS

#READ AND SAVE IMAGES
def imread(filename):
    """Reads an image file completely into memory

    :Parameters:
     - `filename` (str)

    :Returns Type:
        |numpyarray|
    """
    print(" --> Read "+filename)
    if filename.find('.inr')>0 or filename.find('mha')>0:
        from morphonet.ImageHandling import SpatialImage
        from morphonet.ImageHandling import imread as imreadINR
        return imreadINR(filename)
    else:
        from skimage.io import imread as imreadTIFF
        return imreadTIFF(filename)
    return None

def imsave(filename,img):
    """Save a numpyarray as an image to filename.

    The filewriter is choosen according to the file extension. 

    :Parameters:
     - `filename` (str)
     - `img` (|numpyarray|)
    """

    print(" --> Save "+filename)
    if filename.find('.inr')>0 or  filename.find('mha')>0:
        from morphonet.ImageHandling import SpatialImage
        from morphonet.ImageHandling import imsave as imsaveINR
        return imsaveINR(filename,img)
    else:
        from skimage.io import imsave as imsaveTIFF
        return imsaveTIFF(filename,img)
    return None
        
#FOR ASTEC LINEAGE
def read_lineage_tree(filename, t=None):
    """
    Return a lineage tree from a file if exist until time t other return an empty lineage tree
    :param filename:
    :param t:
    :return:
    """
    import pickle
    lin_tree_information = {}
    if os.path.exists(filename):
        print('Read Lineage from '+filename)
        with open(filename, "rb") as f:
            lin_tree_information = pickle.load(f, encoding="latin1")
        if t is not None:
            out = {}
            for k, v in lin_tree_information.iteritems():
                tmp = {}
                if k != 'lin_tree':
                    time = t + 1
                else:
                    time = t
                for key, val in v.iteritems():
                    if key / 10 ** 4 < time:
                        tmp[key] = val
                out[k] = tmp
            lin_tree_information = out
            
    else:
        print('Lineage file missing '+filename)
    return lin_tree_information

#Return t, cell_id from long name : t*10**4+id (to have an unique identifier of cells)
def getidt(idl):
    t=int(int(idl)/(10**4))
    cell_id=int(idl)-int(t)*10**4
    return t,cell_id

#Return Cell name as string
def getName(t,id):
    return str(t)+","+str(id)

def _getObject(o):
    """ Construct an object (as a tuple) from a string
        
    """
    to=0
    ido=0
    cho=0
    oss=o.split(',')
    if len(oss)==1:
        ido=int(o)
    if len(oss)>1:
        to=int(oss[0])
        ido=int(oss[1])
    if len(oss)>2:
        cho=int(oss[2])
    return (to,ido,cho)



def _getObjects(infos):
        """ Get the list of object from an information data
        
        Parameters
        ----------
        infos : string
            The information data

        Returns
        -------
        objects : list
            List of key/value corresponding to a split of the data

        """
        infos=infos.split('\n')
        objects={}
        for line in infos:
            if len(line)>0 and line[0]!="#":
                if line.find("type")==0:
                    dtype=line
                else:
                    tab=line.split(":")
                    ob=_getObject(tab[0])
                    if ob in objects: #Multiple times the same value (we put in list)
                        val1=objects[ob]
                        if type(val1)!=list :
                            objects[ob]=[]
                            objects[ob].append(val1)
                        objects[ob].append(tab[1])
                        #print(objects[tab[0]])
                    else:
                        objects[ob]=tab[1]
        return objects



def _getType(infos):
        """ Get the type from an information data
        
        Parameters
        ----------
        infos : string
            The information data

        Returns
        -------
        type : string
            the type (float, string, ...)

        """
        infos=infos.split('\n')
        for line in infos:
            if len(line)>0 and line[0]!="#":
                if line.find("type")==0:
                    return line.split(":")[1]
        return None

def _getString(ob):
    return str(ob[0])+","+str(ob[1])+","+str(ob[2])

def _getLastCuration(l):
    if type(l)==list:
        lastD=datetime.datetime.strptime('1018-06-29 08:15:27','%Y-%m-%d %H:%M:%S')
        value=""
        for o in l:
            d=o.split(";")[2] #1 Value, 2 Guy, 3 Date
            d2 = datetime.datetime.strptime(d,'%Y-%m-%d-%H-%M-%S')
            if d2>lastD:
                lastD=d2
                value=o
        return value
    return l



def isfile(filename):
    if os.path.isfile(filename):
        return True
    elif os.path.isfile(filename+".gz"):
        return True
    elif os.path.isfile(filename+".zip"):
        return True
    return False

def copy(filename1,filname2):
    if os.path.isfile(filename1):
        os.system('cp '+filename1+" "+filname2)
    elif os.path.isfile(filename1+".gz"):
        os.system('cp '+filename1+".gz "+filname2+".gz")
    elif os.path.isfile(filename1+".zip"):
        os.system('cp '+filename1+".zip "+filname2+".zip")
    else:
        print("ERROR didn't found to copy "+filename1)

def loadMesh(filename):
    f=open(filename,'r')
    obj=''
    for line in f:
        obj+=line
    f.close()
    return obj


def getObjectsByTime(dataset,objects):
    times=[]
    for cid in objects: #List all time points
        o=dataset.getObject(cid)
        if o is not None and o.t not in times:
            times.append(o.t)
    times.sort() #Order Times
    return times

from vtk import vtkImageImport,vtkDiscreteMarchingCubes,vtkWindowedSincPolyDataFilter,vtkQuadricClustering,vtkDecimatePro        
from threading import Thread
_dataToConvert=None
class convertOneToOBJ(Thread):
    def __init__(self, elt,Smooth,Decimate,Reduction):
        Thread.__init__(self)
        self.elt = elt
        self.Smooth = Smooth
        self.Decimate = Decimate
        self.Reduction = Reduction

        self.polydata=None
    def run(self):
        global _dataToConvert
        nx, ny, nz = _dataToConvert.shape
        eltsd=np.zeros(_dataToConvert.shape,np.uint8)
        coord=np.where(_dataToConvert==self.elt)
        #print('     ----->>>>> Create cell '+str(self.elt) + " with "+str(len(coord[0]))+' pixels ')
        eltsd[coord]=255

        data_string = eltsd.tostring('F')
        reader = vtkImageImport()
        reader.CopyImportVoidPointer(data_string, len(data_string))
        reader.SetDataScalarTypeToUnsignedChar()

        reader.SetNumberOfScalarComponents(1)
        reader.SetDataExtent(0, nx - 1, 0, ny - 1, 0, nz - 1)
        reader.SetWholeExtent(0, nx - 1, 0, ny - 1, 0, nz - 1)
        reader.Update()

        #MARCHING CUBES
        contour = vtkDiscreteMarchingCubes()
        contour.SetInputData(reader.GetOutput())
        contour.ComputeNormalsOn()
        contour.ComputeGradientsOn()
        contour.SetValue(0,255)
        contour.Update()
        self.polydata= contour.GetOutput()

        if self.Smooth and self.polydata.GetPoints() is not None:
            smooth_angle=120.0
            smoth_passband=0.01
            smooth_itertations=25
            smoother = vtkWindowedSincPolyDataFilter()
            smoother.SetInputData(self.polydata)
            smoother.SetFeatureAngle(smooth_angle)
            smoother.SetPassBand(smoth_passband)
            smoother.SetNumberOfIterations(smooth_itertations)
            smoother.NonManifoldSmoothingOn()
            smoother.NormalizeCoordinatesOn()
            smoother.Update()
            self.polydata= smoother.GetOutput()


        if self.Decimate and self.polydata.GetPoints() is not None:
            mesh_fineness=1.0
            decimater = vtkQuadricClustering()
            decimater.SetInputData(self.polydata)
            decimater.SetNumberOfDivisions(*np.uint16(tuple(mesh_fineness*np.array(np.array(_dataToConvert.shape)/2))))
            decimater.SetFeaturePointsAngle(30.0)
            decimater.CopyCellDataOn()
            decimater.Update()
            self.polydata= decimater.GetOutput()

        if self.Reduction and self.polydata.GetPoints() is not None:
            decimatePro  = vtkDecimatePro()
            decimatePro.SetInputData(self.polydata)
            decimatePro.SetTargetReduction(0.8) 
            decimatePro.Update()
            self.polydata= decimatePro.GetOutput()
       


def convertToOBJ(dataFull,t,background=0,factor=4,Smooth=True,Decimate=True,Reduction=True,center=[0,0,0]): ####  CONVERT SEGMENTATION IN MESH 
        global _dataToConvert
        _dataToConvert=dataFull[::factor,::factor,::factor]
        elts=np.unique(_dataToConvert)
        elts=elts[elts!=background] #Remove Background
        obj=""
        shiftFace=1
        threads=[]
        for elt in elts:
            tc=convertOneToOBJ(elt,Smooth,Decimate,Reduction)
            tc.start()
            threads.append(tc)

        for tc in threads:
            tc.join()
            if tc.polydata.GetPoints() is not None:
                obj+="g "+str(t)+","+str(tc.elt)+"\n"
                if not tc.polydata.GetPoints() is None :
                    for p in range(tc.polydata.GetPoints().GetNumberOfPoints()):
                        v=tc.polydata.GetPoints().GetPoint(p) 
                        obj+='v ' + str(v[0]*factor-center[0]) +' '+str(v[1]*factor-center[1]) +' '+str(v[2]*factor-center[2])+'\n'
                    for f in range(tc.polydata.GetNumberOfCells()):
                        obj+='f ' + str(shiftFace+tc.polydata.GetCell(f).GetPointIds().GetId(0)) +' '+str(shiftFace+tc.polydata.GetCell(f).GetPointIds().GetId(1)) +' '+str(shiftFace+tc.polydata.GetCell(f).GetPointIds().GetId(2))+'\n'
                    shiftFace+=tc.polydata.GetPoints().GetNumberOfPoints()
                         
                #f=open('temp.obj','w');f.write(obj); f.close()
        return obj
'''
def convertToOBJ(dataFull,t,background=0,factor=4,Smooth=True,Decimate=True,Reduction=True,center=[0,0,0]): ####  CONVERT SEGMENTATION IN MESH 
        from vtk import vtkImageImport,vtkDiscreteMarchingCubes,vtkWindowedSincPolyDataFilter,vtkQuadricClustering,vtkDecimatePro
        data=dataFull[::factor,::factor,::factor]
        nx, ny, nz = data.shape
        elts=np.unique(data)
        elts=elts[elts!=background] #Remove Background
        obj=""
        shiftFace=1
        for elt in elts:
            eltsd=np.zeros(data.shape,np.uint8)
            coord=np.where(data==elt)
            #print('     ----->>>>> At ' +str(t)+ ' create cell '+str(elt) + " with "+str(len(coord[0]))+' pixels ')
            eltsd[coord]=255

            data_string = eltsd.tostring('F')
            reader = vtkImageImport()
            reader.CopyImportVoidPointer(data_string, len(data_string))
            reader.SetDataScalarTypeToUnsignedChar()

            reader.SetNumberOfScalarComponents(1)
            reader.SetDataExtent(0, nx - 1, 0, ny - 1, 0, nz - 1)
            reader.SetWholeExtent(0, nx - 1, 0, ny - 1, 0, nz - 1)
            reader.Update()

            #MARCHING CUBES
            contour = vtkDiscreteMarchingCubes()
            contour.SetInputData(reader.GetOutput())
            contour.ComputeNormalsOn()
            contour.ComputeGradientsOn()
            contour.SetValue(0,255)
            contour.Update()
            polydata= contour.GetOutput()

            if Smooth and polydata.GetPoints() is not None:
                smooth_angle=120.0
                smoth_passband=0.01
                smooth_itertations=25
                smoother = vtkWindowedSincPolyDataFilter()
                smoother.SetInputData(polydata)
                smoother.SetFeatureAngle(smooth_angle)
                smoother.SetPassBand(smoth_passband)
                smoother.SetNumberOfIterations(smooth_itertations)
                smoother.NonManifoldSmoothingOn()
                smoother.NormalizeCoordinatesOn()
                smoother.Update()
                polydata= smoother.GetOutput()


            if Decimate and polydata.GetPoints() is not None:
                mesh_fineness=1.0
                decimater = vtkQuadricClustering()
                decimater.SetInputData(polydata)
                decimater.SetNumberOfDivisions(*np.uint16(tuple(mesh_fineness*np.array(np.array(data.shape)/2))))
                decimater.SetFeaturePointsAngle(30.0)
                decimater.CopyCellDataOn()
                decimater.Update()
                polydata= decimater.GetOutput()

            if Reduction and polydata.GetPoints() is not None:
                decimatePro  = vtkDecimatePro()
                decimatePro.SetInputData(decimater.GetOutput())
                decimatePro.SetTargetReduction(0.8) 
                decimatePro.Update()
                polydata= decimatePro.GetOutput()


            if polydata.GetPoints() is not None:
                obj+="g "+str(t)+","+str(elt)+"\n"
                if not polydata.GetPoints() is None :
                    for p in range(polydata.GetPoints().GetNumberOfPoints()):
                        v=polydata.GetPoints().GetPoint(p) 
                        obj+='v ' + str(v[0]*factor-center[0]) +' '+str(v[1]*factor-center[1]) +' '+str(v[2]*factor-center[2])+'\n'
                    for f in range(polydata.GetNumberOfCells()):
                        obj+='f ' + str(shiftFace+polydata.GetCell(f).GetPointIds().GetId(0)) +' '+str(shiftFace+polydata.GetCell(f).GetPointIds().GetId(1)) +' '+str(shiftFace+polydata.GetCell(f).GetPointIds().GetId(2))+'\n'
                    shiftFace+=polydata.GetPoints().GetNumberOfPoints()
                         
                #f=open('temp.obj','w');f.write(obj); f.close()
        return obj

'''
def addslashes(s):
    d = {'"':'\\"', "'":"\\'", "\0":"\\\0", "\\":"\\\\"}
    return ''.join(d.get(c, c) for c in s)


def tryParseInt(value):
    try:
        return int(value), True
    except ValueError:
        return value, False

class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

ss=" --> "
def strblue(strs):
    return bcolors.BLUE+strs+bcolors.ENDC
def strred(strs):
    return bcolors.RED+strs+bcolors.ENDC
def strgreen(strs):
    return bcolors.BOLD+strs+bcolors.ENDC

def nodata(data):
    if data=="" or data==[] or len(data)==0:
        return True
    return False
    