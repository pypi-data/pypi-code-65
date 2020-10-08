'''dont change any of the below'''
import sys


import inp.objects

def sync_sys_zn_assign(slaveinp,masterinp,inpout,slavesysname,mastersysname):
    '''
	take zone assignments from a system in one input file,
	pushes the zones to a system in another file.
	e.g. go through a proposed model and move a bunch of systems
	on various floors to a unit heater zone (stairwells, boh, etc.
	then link it up to 	your baseline and all the same zones
	will be updated to the new system.
	
    arguments:
        
        slaveinp: the inp file to be changed
        masterinp: the inp file to pull info from
        slavesysname : name of system to change.
        mastersysname : name of system from master to push to 
          slavesys to other

        inpout = desired output
        takes any zones under the 'sysname' in 'slaveinp',
        deletes their current reference and places them under
        the system to which they refer in 'masterinp'
        returns new inpfile as list
		
		should separate functions so you can pass a function just a list (not
		an inpfile and manually change, then write
    
    '''

    slavelist = inp.objects.openinp(slaveinp)
    
    presyslist = []
    syslist  = []
    postsyslist = []
    pre = True
    during = False
    post = False
    for f in slavelist:
        if "= SYSTEM " in f:
            pre = False
            during = True
        if "Metering & Misc" in f:
            pre = False
            during = False
            post = True
        if pre:
            presyslist.append(f)    
        if during:
            syslist.append(f)    
        if post:
            postsyslist.append(f)

    slavesyslist = inp.objects.get_sys_zones(slaveinp)
    mastersyslist= inp.objects.get_sys_zones(masterinp)
    
    slaveznlist = inp.objects.get(slavelist,'ZONE')
#    return slaveznlist

    masterznlist = list(mastersyslist[mastersysname]["attached_zones"])

#    return slaveznlist
    for m in masterznlist:
        for k, v in slavesyslist.items():
            try:
                if m in v['attached_zones']:
                    v['attached_zones'].remove(m)
            except:
                pass
    slavesyslist[slavesysname]["attached_zones"] = masterznlist
    
    newsyslist = []
    
    
#    return slaveznlist
    for k, v in slavesyslist.items():
        for k1, v1 in v.items():
            if "parent" not in k1 and "attached_zones" not in k1:
                newsyslist.append(str(k1) + " = " + str(v1))
        newsyslist.append("..")
        
        for line in v["attached_zones"]:
            for k2, v2 in slaveznlist[line].items():
                if "parent" not in k2 and "attached_zones" not in k2:
                    newsyslist.append(str(k2) + " = " + str(v2))
            newsyslist.append("..")
#    return slaveznlist            
    comblist = presyslist + newsyslist + postsyslist
    
    with open(inpout,'w') as new:
        new.writelines(["%s\n" % item for item in comblist])
    
    return comblist
    
    
