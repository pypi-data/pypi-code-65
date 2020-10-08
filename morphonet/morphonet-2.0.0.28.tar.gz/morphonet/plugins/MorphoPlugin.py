# -*- coding: latin-1 -*-
import numpy as np
from datetime import datetime

class MorphoPlugin:
    def __init__(self):
        self.name="default plugin name"
        self.parent="None"
        self.inputfields={}
        self.dropdowns={}
        self.dropdowns_sel={}
        self.coordinates={}
        self.exec_time=None #Time of Execution
        self.dataset=None

    #PLUGIN NAME 
    def set_Name(self,text_name):
        self.name=text_name

    #PARENT GROUP 
    def set_Parent(self,text_name):
        self.parent=text_name

    #ADD INPUT FIELD IN UNITY
    def add_InputField(self,text_name,default_value=None):
        self.set_InputField(text_name,default_value)

    def set_InputField(self,text_name,value):
        self.inputfields[text_name]=value

    def get_InputField(self,text_name):
        return self.inputfields[text_name]

    #ADD DROWDOWN IN UNITY
    def add_Dropdown(self,text_name,option):
        self.dropdowns[text_name]=option
        self.set_Dropdown(text_name,0)

    def set_Dropdown(self,text_name,value):
        self.dropdowns_sel[text_name]=int(value)

    def get_Dropdown(self,text_name):
        return self.dropdowns[text_name][self.dropdowns_sel[text_name]]

    #ADD COORDINATES IN UNITY
    def add_Coordinates(self,text_name):
        self.coordinates[text_name]=[]

    def set_Coordinates(self,text_name,coords): #Recieve '(-0.9, 0.2, -3.5); (0.1, -0.2, -3.5); (0.9, -0.6, -3.5)'
        if coords!="":
            self.coordinates[text_name]=[]
            for s in coords.split(";"):
                self.coordinates[text_name].append(np.float32(s[1:-1].split(',')))

    def get_Coordinates(self,text_name):
        return self.coordinates[text_name]

    #INTERNAL COMMAND
    def cmd(self):
        return self.name.replace(' ','_')

    def getBtn(self):
        c=self.cmd()+";"+self.parent
        for tf in self.inputfields:
            c+=";IF_"+str(tf).replace(' ','_')
            if self.inputfields[tf] is not None:
                c+=";DF_"+str(self.inputfields[tf]).replace(' ','_')
        for dd in self.dropdowns:
            c+=";DD_"+str(dd).replace(' ','')+"_"
            for v in self.dropdowns[dd]:
                c+=str(v).replace(' ','-')+"_"
        for cd in self.coordinates:
            c+=";CD_"+str(cd).replace(' ','_')
        return c

    #INTERNAL COMMAND
    def start(self,t,dataset,objects):
        self.exec_time=datetime.now()
        self.dataset=dataset
        self.t=t
        self.objects=objects
        print(">> Process "+self.name)
        isOk=True

        
        for tf in self.inputfields:
            if self.inputfields[tf] is None or self.inputfields[tf]=="":
                print(" --> Please fill the parameter "+str(tf))
                isOk=False
            else:
                print(" --> Found "+str(tf)+" = "+str(self.inputfields[tf]))
        if isOk and objects is not None and len(objects)>0 and objects[0]!='':
            print(" --> with objects :"+str(objects))
        if not isOk:
            self.dataset.restart(self)
        return isOk

    def restart(self):
        log="Plugin:"+self.name+"; Parent:"+self.parent+"; Time:"+str(self.t)+";"
        for tf in self.inputfields:
            log+=" IF:"+str(tf)+":"+str(self.get_InputField(tf))+";"
        for dd in self.dropdowns:
            log+=" DD:"+str(dd)+":"+str(self.get_Dropdown(dd))+";"
        for cd in self.coordinates:
            log+=" CD:"+str(cd)+":"+str(self.get_Coordinates(cd))+";"
        if self.objects is not None and len(self.objects)>0 and self.objects[0]!='':
            log+=" ID:"+str(self.objects)+";"
        self.dataset.save_log(log,self.exec_time)
        self.dataset.restart(self)








