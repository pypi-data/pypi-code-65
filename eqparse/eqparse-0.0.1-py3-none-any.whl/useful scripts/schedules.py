'''
a series of functions allowing user to collect schedule objects
from either an inp file or from an xl file, and
update existing values into new inpfile.
'''
from collections import OrderedDict
import pandas as pd


def xlschedtolist(wkbk, sheet, cols, header):
    '''
    pull info from excel and make lists out of it
    returns list of ordereddict
    needs: getschedfromlist
    '''
    xlschedules = pd.read_excel(wkbk, sheet_name=sheet, usecols=cols, header=header)
    xlschedules = xlschedules.values.tolist()
    xlschedules = [item for sublist in xlschedules for item in sublist]
    xlschcollapse = []

    for line in xlschedules:
        splitter = line.split("\n")
        for s in splitter:
            xlschcollapse.append(s)

    dayscheds = getschedfromlist(xlschcollapse, "DAY-SCHEDULE-PD")
    weekscheds = getschedfromlist(xlschcollapse, "WEEK-SCHEDULE-PD")
    annscheds = getschedfromlist(xlschcollapse, "= SCHEDULE-PD")

    schedlist = [dayscheds, weekscheds, annscheds]
    return schedlist




def schedfrominp(inpfile):
    '''
    read an existing inp file and return list of ordereddict
    returns list of ordereddict
    needs: getschedfromlist

    '''
    allschedlist = []
    write = False
    
    with open(inpfile) as f:
        f_list = f.readlines()

    for f in f_list:
        if "DAY-SCHEDULE-" in f:
            write = True
        if write and "$" not in f:
            allschedlist.append(f)

        if "Polygons" in f:
            write = False
            break

    dayscheds = getschedfromlist(allschedlist, "DAY-SCHEDULE-PD")
    weekscheds = getschedfromlist(allschedlist, "WEEK-SCHEDULE-PD")
    annscheds = getschedfromlist(allschedlist, "= SCHEDULE-PD")

    schedlist = [dayscheds, weekscheds, annscheds]
    return schedlist


	
def getschedfromlist(listname, criteria):
    '''
    STATUS: WORKS make dictionary of schedules out of list pulled in from excel
    returns ordereddict of schedules with 'criteria' in name
    '''
    keylist = []
    vallist = []
    vals = []
    write = False
    #ESTABLISH WHEN TO WRITE
    for line in listname:
        if criteria in line:
            write = True
            topkey = line.split("=")[0].strip().strip("\"")
            keylist.append(topkey)

        if write:
            vals.append(line)

        if ".." in line:
            vallist.append(vals)
            write = False
            #vals.append('..')
            vals = []

    vallist = [i for i in vallist if len(i) > 1]
    topdict = OrderedDict(zip(keylist, vallist))
    return topdict

	
	
def updatescheds(newinp, schedlist):
    '''
    look through newinp for items within schedlist and update any schedules it finds
    also returns the new list
    '''

    with open(newinp) as f:
        f_list = f.readlines()

    keysininp = []

    delete = False
    for num, line in enumerate(f_list):
        topkey = line.split("=")[0].strip().strip("\"")
        if topkey != 'LOCATION' and topkey in schedlist.keys():
            delete = True
            tlist = []
            keysininp.append(topkey)
            for l in schedlist[topkey]:
                tlist.append(l)
            f_list[num] = [t for t in tlist]

    n_list = []
    delete = False
    for f in f_list:
        if not delete:
            n_list.append(f)
        if type(f) == list:
            delete = True
        if "   .." in f:
            delete = False

    flat_list = []
    for n in n_list:
        if type(n) == str:
            flat_list.append(n)
        if type(n) == list:
            for i in range(len(n)):
                flat_list.append(n[i])

    #not sure why i need all of these but they all seem to only work together
    for num, line in enumerate(flat_list):
        if len(line) < 2:
            flat_list[num] = "$"

    flat_list = list(filter(lambda x: x != "$", flat_list))
    flat_list = [i for i in flat_list if len(i) != 0]

    with open(newinp, 'w') as f:
        f.writelines(["%s\n" % item for item in flat_list])

    keysnotininp = list(set(schedlist) - set(keysininp))
    return keysnotininp


#top-level functions, to be called directly by user:

def updatefrominp(inp_from,inp_to):
    '''
    top level command. pull schedules from an inp file
    and replaces it into a second inp file.
	needs: schedfrominp,updatescheds,getschedfromlist
    '''

    y = schedfrominp(inp_from)
    for  f in y:
        xx = updatescheds(inp_to, f)


def updatefromxls(xl_file,xl_sheet,xl_cols,xl_header,inp_to):
    '''
    top level command. pull schedules from an excel file
    (excel file must be a single column, top-down
    and replaces it into an inp file.
	needs: xlschedtolist,updatescheds,getschedfromlist
    '''
    z = xlschedtolist(xlfile, xlsheet, xlcols, xlheader)
    for  f in z:
        xx = updatescheds(inp_to, f)





#FUNCTIONS TO MAKE:


 #def schedclean ---- look at each schedule and find if it references anything--if not, remove it.
 #update options - if inp = inp, backup, option for from excel, etc, option to push unfound schedules ('keysnotininp')
 #in oldinp to newinp and even take care of schedule/changes (i.e. adding a holiday week and
 #holiday day)and 

 
 
 
 
 
 
 