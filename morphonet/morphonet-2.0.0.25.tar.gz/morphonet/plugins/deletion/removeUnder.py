# -*- coding: latin-1 -*-
from morphonet.plugins import MorphoPlugin

#Remove Small Voxels Element under a certain size for all time points
class removeUnder(MorphoPlugin):
    def __init__(self): #PLUGIN DEFINITION 
        MorphoPlugin.__init__(self) 
        self.set_Name("Remove Under")
        self.set_Parent("Remove objects")
        self.add_InputField("Voxel Size",20)

    def process(self,t,dataset,objects): #PLUGIN EXECUTION
        if not self.start(t,dataset,objects):
            return None

        import numpy as np
        data=dataset.get_seg(t)
        if data is not None:
            cells=np.unique(data)
            cells=cells[cells!=dataset.background]
            for c in cells:
                coords=np.where(data==c)
                nb=len(coords[0])
                if nb<float(self.get_InputField("Voxel Size")):
                     print("     ----->>>  delete object "+str(c)+" at "+str(t) + " with "+str(nb)+" pixels")
                     data[coords]=dataset.background
                     o=dataset.getObject(t,c)
                     dataset.del_link(o)
                     dataset.set_seg(t,data)
              
        self.restart() #ADD At the end 
         




