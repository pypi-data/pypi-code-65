import inp.objects as obj

from collections import OrderedDict

def plenums_to_end_of_sys(inpfile,newinpfile):
    '''
    takes all plenum zones under each system, and
    inserts them at the bottom of the system
    for better parsing/visualization
    '''
    flist = obj.openinp(inpfile)
    systems = obj.get(flist,"SYSTEM")
    zones = obj.get(flist,"ZONE")
 
    sysorder = OrderedDict()
    for s in systems:
        condzones = []
        uncondzones = []
            
        for k, v in zones.items():
            if v['parent'] == s:
                if v['TYPE'] == 'CONDITIONED':
                    condzones.append(v)
                else:
                    uncondzones.append(v)
                         
        sysorder[(s+"cond")] = condzones
        sysorder[(s+"uncond")] = uncondzones
             
    sysreorderlist = []
    for name, s in systems.items():
        syslist = []
        obj.objectdump(s,sysreorderlist)
    
        for k1, v1 in sysorder.items():
            for k2 in v1:
                if k2['parent'] == name:
                    obj.objectdump(k2,sysreorderlist)
                
    startreplace = "= SYSTEM"
    endreplace = "Metering & Misc HVAC"
    flistnew = obj.replace_inp_section(flist,sysreorderlist,startreplace,endreplace)

    basedirectory = os.path.dirname(inpfile)
    subdirname = "PyPlenum"
    obj.writeinp_fromlist(flistnew,newinpfile,basedirectory,subdirname)
    

inpfile = 'P:/_Projects/180000/180840-000/D-Design Mgmt/Calc/Energy/Energy Model/eQuest/BRB.inp'
plenums_to_end_of_sys(inpfile,"PyPlenum.inp")

