'''
	updates inp_to_file to have the same # and dimension of
	windows, floors and space
    as inp_from_file, placed in newinp within subdirectory.
'''	
	
from collections import OrderedDict
import inp.objects as obj





def vision_sync(inp_from_file,inp_to_file,subdirectory):
    '''
	updates inp_to_file to have the same # and dimension of
	windows as inp_from_file, placed in newinp within subdirectory.
    '''	
    #handle from_inp
    flist_from = obj.openinp(inp_from_file)
    windows = obj.get(flist_from,"WINDOW")
    
    wall2windict = {}
    for k1, v1 in windows.items():
        wall = v1['parent']
        if wall in wall2windict.keys():
            wall2windict[wall].append(v1)
        else:
            wall2windict[wall] = [v1]
        
    
    #handle to_inp
    flist_to = obj.openinp(inp_to_file)
    windows_to = obj.get(flist_to,"WINDOW")
    windows_to_update = obj.get(flist_to,"WINDOW")
    
    #update existing windows and populate list of windows to add 
    windowaddlist = []
    for k1, v1 in windows.items():
        for k2, v2 in v1.items():
            
            if k1 in windows_to_update.keys():            
                windows_to_update[k1][k2] = v2
                windows_to[k1][k2] = v2
                
            if k1 not in windows_to_update.keys():
                windowaddlist.append(k2)
                windows_to_update[k1] = OrderedDict()
                windows_to_update[k1][k2] = v2
                windows_to[k1] = OrderedDict()
                windows_to[k1][k2] = v2
    

    #handle parameters in inp_to but not in inp_from
    for k1, v1 in windows_to_update.items():
        for k2, v2 in v1.items():
            try:
                b = windows[k1][k2]
            except KeyError:
                windows_to[k1].pop(k2)


    
    
    #add missing windows
    for w in windowaddlist:

        objstring = w.replace("\"","").replace("\'","").strip("\"")

        objstringdict = windows_to[objstring]
        parent = windows_to[objstring]['parent']
        flist_to = obj.obj_insert(flist_to,objstringdict,parent)
    
    #remove windows not in new one:
    windowremovelist = []
    for k1, v1 in windows_to.items():
        if k1 not in windows.keys():
            objstring = k1.replace("\"","")
            windowremovelist.append(objstring)
            
    flist_winremove = flist_to
    for w in windowremovelist:
        flist_winremove = obj.removeobject(flist_to,w,"WINDOW")    
	
	#write it
    updated = obj.writeinp(flist_winremove,"n/a",windows_to,write=False)
    obj.writeinp_fromlist(updated, 'py_window_sync.inp', subdir=subdirectory)



def opaque_sync(inp_from_file,inp_to_file,subdirectory):
    '''handles opaque services. 
    does not currently handle any additional walls/spaces.
    UNFINISHED
    '''
    flist_from = obj.openinp(inp_from_file)
    flist_to = obj.openinp(inp_to_file)

    floor_from = obj.get(flist_from,"FLOOR")
    space_from = obj.get(flist_from,"SPACE")
    wall_from = obj.get(flist_from,"WALL")    
    
    floor_to = obj.get(flist_to,"FLOOR")
    space_to = obj.get(flist_to,"SPACE")
    wall_to = obj.get(flist_to,"EXTERIOR-WALL")



    
floorvars = [ "MULTIPLIER",
              "FLOOR-HEIGHT",
              "SPACE-HEIGHT",
              "X",
              "Y",
              "Z"]

spacevars = [ "FLOOR-MULTIPLIER",
              "MULTIPLIER",
              "HEIGHT",
              "X",
              "Y",
              "Z"]

wallvars = [ "X",
             "Y",
             "Z",
             "HEIGHT",
             "WIDTH"]



def window_sync(inp_from_file,inp_to_file,subdirectory):
    '''user runs this function'''
    
    opaque_sync(inp_from_file,inp_to_file,subdirectory)
    vision_sync(inp_from_file,inp_to_file,subdirectory)
    
        

#to run file:
inp_from_file = 'P:/_Projects/Y150000/Y150248-000/Calculations/Mech/Energy Model/eQuest/Proposed/1185 Broadway Proposed.inp'
inp_to_file = 'P:/_Projects/Y150000/Y150248-000/Calculations/Mech/Energy Model/eQuest/Baseline/1185 Broadway Base.inp'
newinp = 'P:/_Projects/Y150000/Y150248-000/Calculations/Mech/Energy Model/eQuest/Proposed/PyCopyWindows/pytest/py_window_sync.inp'
subdir = 'P:/_Projects/Y150000/Y150248-000/Calculations/Mech/Energy Model/eQuest/Proposed/PyCopyWindows/pytest/'
window_sync(inp_from_file, inp_to_file, subdir)









#TESTING:#S
#prop =obj.get(obj.openinp(inp_from_file),"SPACE") 
#base =obj.get(obj.openinp(inp_to_file),"SPACE") 
#new = obj.get(obj.openinp(newinp),"SPACE") 
#
#testspace = 'F3SSW Perim Spc (G.SSW6)'
##
##for b in base.keys():
##    try:  
#
#print ("   prop : " + testspace + " : " + str(prop[testspace]))
#print ("   base : " + testspace + " : " +  str(base[testspace]))
#print ("   new : " + testspace + " : " + str(new[testspace]))
##    
##    except:
##        pass
#
#
#print (len(prop))
#print (len(new))
#print (len(base))