'''
inserts modifiers into each window height as
multiplier, for the event that initial window
params weren't set up or detailed windows were created and must now be granularly changed

can sort by exposure (windowmult_byexposure), but this is a relatively lazy parsing method.

'''


import inp.objects as objects

def windowmult_byexposure(inpfile,inpfileout):
    winparms = {'N': '* #pa("N_Win_Mult")}',
                'E': '* #pa("E_Win_Mult")}',
                'S': '* #pa("S_Win_Mult")}',
                'W': '* #pa("W_Win_Mult")}'
               }
    
    
    with open(inpfile, encoding="Latin1") as f:
        f_list = f.readlines()
    
    toggle = 0
    
    winname = []
    newinp = []
    explist = []
    
    #add multipliers to windows
    for line in f_list:
        if not toggle and "= WINDOW" not in line:
            newinp.append(line)
        if "= WINDOW" in line:
            toggle = 1
    
            winname.append(line)
            exposure = line.split('.', 1)[-1]
            exposure = exposure[0]
            explist.append(exposure)
            newinp.append(line)
    
        if toggle:
            if "GLASS-TYPE" in line:
                newinp.append(line)
            if "FRAME-WIDTH" in line:
                newinp.append(line)
            if "   X " in line:
                newinp.append(line)
            if "   Y " in line:
                newinp.append(line)
            if "FRAME-COND" in line:
                newinp.append(line)
            if ".." in line:
                newinp.append(line)
                toggle = 0
    
            if "HEIGHT" in line:
                line = line.replace('\r\n', '')
                toggle = 0
    
                if 'N' in exposure or 'S' in exposure or 'E' in exposure or 'W' in exposure:
                    toreplace = winparms[exposure]
                    replaceline = line.strip('\\n') + winparms[exposure]
                    replaceline = replaceline.replace('\n', ' ')
                    replaceline = replaceline.replace("=", "= {")
                    newinp.append(replaceline)
                else:
                    newinp.append(line)
   				
    #add global parameters
    globalparamtext = "$              Global Parameters"
    
    paramtext = "PARAMETER\n\"N_Win_Mult\"= 1.0 .. \nPARAMETER\n\"E_Win_Mult\"= 1.0 .. \nPARAMETER\n\"S_Win_Mult\"= 1.0 .. \nPARAMETER\n\"W_Win_Mult\"= 1.0 .. \n "
    
    newinp = [w.replace(globalparamtext, (globalparamtext+"\n"+paramtext)) for w in newinp]

    with open(inpfileout, 'w') as f:
        f.write("\n".join(newinp))
    	

  

def windowmult(inpfile,inpfileout):
    flist = objects.openinp(inpfile)
    windows = objects.get(flist,"WINDOW")


    windowlist = []
    for k, v in windows.items():
        if 'HEIGHT' in v.keys():
            value = "{" + v['HEIGHT'] + "* #PA(\"Win_Mult\")"+"}"
            tup = k, value
            windowlist.append(tup)            
    for w in windowlist:
        windows[w[0]]['HEIGHT'] = w[1]
    for k1, v1 in windows.items():
        v1 = {k:v for k2, v2 in v1.items() if v2 is not None}
    
    
    flistnew = []           
    current_default = False
    for f in flist:
        if "Global Parameters" in f:
            flistnew.append("PARAMETER\n\"Win_Mult\" = \"1.0\" ..")
            current_default = True 
        
        if "SET-DEFAULT" in f and "WINDOW" in f:
            current_default = True
        
        if current_default and "*#P3(\"FLOOR-HEIGHT\")" in f:            
            default_to_append =  "* #PA(\"Win_Mult\")"
            flistnew.append(f + default_to_append)                
       
        else:
            flistnew.append(f)
            
        if "SET-DEFAULT" in f and "WINDOW" not in f:     
            current_default = False 
                   
    objects.writeinp(flistnew,inpfileout,windows)    
    return flistnew
    


#inpfile = "P:/_Projects/180000/180728-000/D-Design Mgmt/Calc/Energy/Energy Model/eQuest Model/Baseline/311 Broad Base.inp"
#inpfileout = "P:/_Projects/180000/180728-000/D-Design Mgmt/Calc/Energy/Energy Model/eQuest Model/Baseline/windowmult/311 Broad Base_win.inp"

#a = windowmult(inpfile,inpfileout)
#for b in a[7800:7850]:
##    print (b)
##    print (len(b))


#windowmult_byexposure(inpfile,inpfileout)
