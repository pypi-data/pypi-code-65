
'''
problem with this is the manual labor associated with
organizing file structures for "source" vs. "dest" lists.
maybe open up an excel document (or use a template)and
change within the program rather than bouncing to
a bunch of random text files?


use:

book = xw.Book()
input('Complete Book')
so it's a logical, step-by-step format. output
is a new input file and pd2 file in the same folder


'''
import xlwings as xw
import os
import shutil
from collections import OrderedDict
#deal with directories and file names
directory = "Zone Reassign"

try:
    os.makedirs(directory)
except os.error:
    pass

filename = 'zone_reassign.inp'
tochange = 'Base Extell 221 West 57th St'
inpfile = tochange + ".inp"
pd2file = tochange + ".pd2"
newpd2file = filename[0:-4] + '.pd2'

#make blank lists / dictionaries
zonenames = []
zonestart = []
zoneend = []
zoneval = []
zonedict = {}
sysassign = []
zonesysdict = {}

###############read inp file
with open(inpfile) as f:
    f_list = f.readlines()



#get system and zone assignments, populate lists
for num, line in enumerate(f_list):
    if "= SYSTEM" in line:
        splitter1 = line.split("\"")
        newline1 = splitter1[1]
        currentsys = newline1

    if "= ZONE" in line:
        splitter = line.split("\"")
        newline = splitter[1]
        zonenames.append(newline)
        zonestart.append(num)
        zoneend.append(num-1)
        sysassign.append(currentsys)

    if "Metering & Misc HVAC" in line:
        zoneend.append(num-3)
        zoneend = zoneend[1:]

###############write system names to text file
with open(directory + "\\" + 'zonenames.csv', 'w') as output:
    for num, f in enumerate(zonenames):
        str(output.write(f))
        str(output.write(","))
        str(output.write(sysassign[num]))
        output.write("\n")

####writing logic
for num, line in enumerate(zonenames):
    key = line
    start = zonestart[num]
    end = zoneend[num]
    val = f_list[start:end]
    truncateval = []

    for v in val:
        truncateval.append(v)
        if ".." in v:
            break
    if ".." not in truncateval[-1]:
        truncateval.append("..\n")
    zoneval.append(truncateval)
    zonedict[line] = truncateval
    zonesysdict[line] = sysassign[num]




#read user-defined csv file and make ordered dictionary and dictionary of all zone inp text
with open(directory + "\\" +  'zonenamesnew.csv', 'r') as f:
    zonereassign = f.readlines()

reassigndict = {}
for z in zonereassign:
    splitter = z.split(",")
    sys = splitter[1].strip("\n")
    reassigndict[splitter[0]] = sys

    orderedsystems = OrderedDict((x, True) for x in sysassign).keys()




#make system inp text and blank lists
sysinfo = []
sysdict = {}
sysstart = []
sysend = []
sysval = []
sysnames = []
write = False
last = False
for num, line in enumerate(f_list):
    if "= SYSTEM" in line:
        splitter = line.split("\"")
        newline = splitter[1]
        sysnames.append(newline)
        sysstart.append(num)

        write = True
    if ".." in line:

        if write:
            sysinfo.append(line)
            sysend.append(num)
        write = False
    if write:
        sysinfo.append(line)

for num, line in enumerate(sysnames):
    key = line
    start = sysstart[num]
    end = sysend[num] + 1
    val = f_list[start:end]
    sysval.append(val)
    sysdict[line] = val



#make new inp text for hvac systems and zones

newhvac = []
for line in orderedsystems:
    newhvac.append(sysdict[line])
    for k2, v2 in reassigndict.items():
        if v2 in line and len(v2) == len(line):
            newhvac.append(zonedict[k2])

newhvacstring = ''.join(str(r) for v in newhvac for r in v)



###############write new inp
f_listnew = []
list1 = f_list[0:sysstart[0]]
list2 = newhvacstring
list3 = f_list[zoneend[-1]:]

f_listnew.append(list1)
for l in list2:
    f_listnew.append(l)
f_listnew.append(list3)
f_liststring = ''.join(str(r) for v in f_listnew for r in v)



###############write files / remove existing
if os.path.exists(filename):
    os.remove(filename)

with open(directory + "\\" + filename, 'w') as output:
    output.write(f_liststring)


try:
    shutil.copy(pd2file, (directory + "\\" + newpd2file))
except shutil.Error:
    pass
