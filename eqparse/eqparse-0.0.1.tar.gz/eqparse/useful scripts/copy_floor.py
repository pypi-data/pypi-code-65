'''
one-off module to take a floor, duplicate it based on user input criteria and
copy all associated spaces / children / zones.
TOP-LEVEL FUNCTION FOR USER TO RUN:

    
system assignment options for new zones? use zone reassign for now if needed.
needs: inp.objects
to do: fix so that spaces that have been renamed in detailed mode can be accounted for
to do: clean up/re-factor. this feels like too much code.

'''

from collections import OrderedDict
import re
import inp.objects as objects

def openinp(inpread):
    '''opens input file (.inp), returns it in list form '''
    with open(inpread) as f:
        inpfile = f.readlines()
    return inpfile



def getflr(listname, flrname):
    '''opens input file, returns list of entire specified floor'''
    write = False
    flrlist = []
    for f in listname:
        if flrname in f and "= FLOOR " in f:
            write = True
        if flrname not in f and "= FLOOR " in f:
            write = False
        if write:
            flrlist.append(f)
    return flrlist






def prepfloor(flrlist, oldtag):
    '''if space in floor doesn't have oldtag in it, add to beginning.'''
    nlist = flrlist
    for num, f in enumerate(flrlist):
        if "= SPACE " in f and oldtag not in f:
            nlist[num] = f[0] + oldtag + "_" + f[1:]
    return nlist






def splitflr(flrlist, oldtag, newtag1, newtag2):
    '''splits floor  / space / children into two new, based on newtags'''
    newflr1 = []
    newflr2 = []
    for f in flrlist:
        if "POLYGON" not in f and "CONSTRUCTION" not in f:
            f1 = f.replace(oldtag, newtag1)
            f2 = f.replace(oldtag, newtag2)
            newflr1.append(f1)
            newflr2.append(f2)
        if "POLYGON" in f or "CONSTRUCTION" in f:
            newflr1.append(f)
            newflr2.append(f)
    #handle duplicates (i.e. custom-made windows)
    newflrduplicates = []
    for f in newflr1:
        matcher = ""
        if re.match("\".*\" = ", f) is not None:
            matcher = f
        try:
            if matcher in newflr2:
                newflrduplicates.append(matcher)
        except:
            pass
    for n in range(len(newflr2)):
        if newflr2[n] in newflrduplicates:
            newflr2[n] = newflr2[n].replace("\" = ", "_2\" = ")
    bothfls = newflr1 + newflr2
    return bothfls




def flrreplace(bothfls, flrlist, listname):
    '''actually replace and make new concatenated inp file'''

    for num, f in enumerate(listname):
        if flrlist[0] in f:
            startnum = num
            break

    f_listnew = listname[0:startnum] + bothfls + listname[startnum+len(flrlist):]
    return f_listnew




def getzn(inpread, flrlist, oldtag):
    znlist = objects.get(inpread, "ZONE", parent=False)
    spctext = [line for line in flrlist if oldtag in line and "= SPACE " in line]
    spclist = []
    for s in spctext:
        splitter = s.split("\"")
        spclist.append(splitter[1])
    return znlist



def prepzn(znlist, oldtag):
    '''if zone and assigned space doen't have oldtag in it, add to beginning.'''
    nlist = znlist
    for num, f in enumerate(znlist):
        if "= ZONE " in f and oldtag not in f:
            nlist[num] = f[0] + oldtag + "_" + f[1:]
    return nlist




def splitzn(znlist, oldtag, nwtg1, nwtg2):  
    '''splits zns into two new, based on newtags'''

    newzn1 = []
    newzn2 = []
    for f in znlist:
        if "POLYGON" not in f:
            f1 = f.replace(oldtag, nwtg1)
            f2 = f.replace(oldtag, nwtg2)
            newzn1.append(f1)
            newzn2.append(f2)
        else:
            newzn1.append(f1)
            newzn1.append(f2)
    bothzns = newzn1 + newzn2
    return bothzns





def znreplace(listname, oldtag, nwtg1, nwtg2): 
    ''' replaces zones in list'''
    
    f_list_zn_replace = []
    zonewrite = False
    for f in listname:
        if "= ZONE"  in f and oldtag in f:
            f = f.replace(oldtag, nwtg1)
            f_list_zn_replace.append(f)
            zonewrite = True
        elif " SPACE " in f and zonewrite:
            f = f.replace(oldtag, nwtg1)
            f_list_zn_replace.append(f)
            zonewrite = False
        else:
            f_list_zn_replace.append(f)
    return f_list_zn_replace





def separatezones(f_list_flr_replace, znlist, oldtag, nwtg1, nwtg2):
    '''gets all zones and splits into two new lists'''
    
    bothzones = splitzn(znlist, oldtag, nwtg1, nwtg2)
    newzndict1 = objects.get(bothzones, "ZONE", parent=False)
    newzndict2 = objects.get(bothzones, "ZONE", parent=False)
    newzndict1 = OrderedDict({k: v for k, v in newzndict1.items() if nwtg1 in k})
    newzndict2 = OrderedDict({k: v for k, v in newzndict2.items() if nwtg2 in k})
    newznlist1 = list(newzndict1.items())
    newznlist2 = list(newzndict2.items())
    newzncrossdict = OrderedDict()
    for num, line in enumerate(newznlist1):
        newzncrossdict[newznlist1[num][0]] = newznlist2[num][0]
    zn_replace = znreplace(f_list_flr_replace, oldtag, nwtg1, nwtg2)
    zn_replace_2 = []
    for num, line in enumerate(zn_replace):
        if "Metering & Misc HVAC" not in line:
            zn_replace_2.append(line)
        if "Metering & Misc HVAC" in line:
            for k, v in newzndict2.items():
                for k2, v2 in v.items():
                    zn_replace_2.append(str(k2) + " = " + str(v2))
                zn_replace_2.append('..')
            zn_replace_2.append(line)
    return zn_replace_2





def write_flrrepl_inp(inpoutname, listname):
    '''writes input file, with special language for addfloor function'''
    
    with open(inpoutname, 'w') as f:
        for line in listname:
            if "parent = " not in line:
                f.write("%s\n" % line)





def copy_floor(inpin, inpout, oldtag, newtag1, newtag2):
    '''user runs this function.'''
    
    f_list = openinp(inpin)
    flrlist = getflr(f_list, oldtag)
    prepfloorlist = prepfloor(flrlist, oldtag) 
    bothfls = splitflr(prepfloorlist, oldtag, newtag1, newtag2)
    f_list_flr_replace = flrreplace(bothfls, prepfloorlist, f_list)
    
    znlist = getzn(f_list, flrlist, oldtag)
    znlist = prepzn(znlist, oldtag)
    zn_replace_2 = separatezones(f_list_flr_replace, f_list, oldtag, newtag1, newtag2)
    
    write_flrrepl_inp(inpout, zn_replace_2)
    print ("Input File:\n" +
            inpin +
           "Has been read and processed.\n"
            "Floor " + 
            oldtag + " has been duplicated and split into:\nFloor " +
            newtag1 + " and Floor " + newtag2 + 
            ".\n" +
            "New Input File:\n" +
            inpout +
            "\nHas been created and populated with both floors/zones."
            + "\nPress Enter to Continue...")
    
    input()
    return zn_replace_2    
    



#
##example for how to run file
#inp_in = ('C:/Users/msweeney/Desktop/MS EM Tools/Python/311 add/311 Broad Prop.inp')
#inp_out = ('C:/Users/msweeney/Desktop/MS EM Tools/Python/311 add/311 Broad Prop_addfl.inp')
#copy_floor(inp_in, inp_out, "5-31", "5-18", "19-31")   
