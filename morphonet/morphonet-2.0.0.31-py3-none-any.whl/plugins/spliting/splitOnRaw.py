# -*- coding: latin-1 -*-
from morphonet.plugins import MorphoPlugin
from .functions import *

#Split Selected Objects based on Distance between Two Peaks in Segmentation Cells  -> GOOD to separate 2 fused cells
class splitOnRaw(MorphoPlugin):
    def __init__(self): #PLUGIN DEFINITION 
        MorphoPlugin.__init__(self) 
        self.set_Name("Split On Raw")
        self.add_InputField("Volume Minimum",default=2000)
        self.add_InputField("Min Distance",default=20)
        self.set_Parent("Split objects")

    def process(self,t,dataset,objects): #PLUGIN EXECUTION
        if not self.start(t,dataset,objects):
            return None
            
        from skimage.morphology import label,watershed
        from skimage.feature import peak_local_max
        import numpy as np
        min_distance=int(self.get_InputField("Min Distance"))
        minVol=int(self.get_InputField("Volume Minimum"))
        for cid in objects:
            o=dataset.getObject(cid)
            if o is not None:
                
                data=dataset.get_seg(o.t) 
                cellCoords=np.where(data==o.id)
                print('     ----->>>  Split object '+str(o.getName()) + " with "+str(len(cellCoords[0]))+ " voxels ")
                xmin,xmax,ymin,ymax,zmin,zmax=getBorders(data,cellCoords)
                cellShape=[1+xmax-xmin,1+ymax-ymin,1+zmax-zmin]
                markers=np.zeros(cellShape,dtype=np.uint8) #PREPARE SEEDS FOR WATERSEED
                mask=np.zeros(cellShape,dtype=np.bool)
                mask[cellCoords[0]-xmin,cellCoords[1]-ymin,cellCoords[2]-zmin]=True
                rawdata=dataset.get_raw(o.t)
                rawdata=rawdata[xmin:xmax+1,ymin:ymax+1,zmin:zmax+1]
                rawdata[np.where(mask==False)]=rawdata.max() #Remove where mask is not 
                coordinates = peak_local_max(rawdata.max()-rawdata, min_distance=min_distance,num_peaks=2) 
                print("     ----->>>  Found "+str(len(coordinates))+ " peaks ")
                l=1
                for coord in coordinates:
                    markers[coord[0],coord[1],coord[2]]=l
                    l+=1
                labelw=watershed(rawdata,markers, mask=mask)
                
                data,newId=applyNewLabel(data,xmin,ymin,zmin,labelw,minVol=minVol)
                if newId:
                    dataset.del_link(o)
                    dataset.set_seg(t,data)


        self.restart()