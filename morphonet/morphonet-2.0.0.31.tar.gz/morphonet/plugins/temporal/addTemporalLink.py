# -*- coding: latin-1 -*-
from morphonet.plugins import MorphoPlugin


#Create links with objects in time
class addTemporalLink(MorphoPlugin):
    def __init__(self): #PLUGIN DEFINITION 
        MorphoPlugin.__init__(self) 
        self.set_Name("Create Links")
        self.set_Parent("Temporal Relation")

    def process(self,t,dataset,objects): #PLUGIN EXECUTION
        if not self.start(t,dataset,objects): 
            return None

        #List Objects by selections
        selections={}
        for cid in objects:
            o=dataset.getObject(cid)
            if o is not None:
                if o.s not in selections:
                    selections[o.s]=[]
                selections[o.s].append(o)
        if len(selections)>1:
            print(" --> Found  "+str(len(selections))+ " selections ")
        for s in selections:
            #Order objects by time
            times={}  #List all times
            for o in selections[s]:
                if o.t not in times:
                    times[o.t]=[]
                times[o.t].append(o)
            
            for t in sorted(times):
                if t+1 in times:
                    cellT=times[t]
                    cellTP=times[t+1]
                    for daughter in cellTP:
                        for mother in cellT:
                            dataset.add_link(daughter,mother)
                            print(" ----> Link object "+str(daughter.id)+" at "+str(daughter.t)+" with "+str(mother.id)+ " at "+str(mother.t))

        self.restart()
