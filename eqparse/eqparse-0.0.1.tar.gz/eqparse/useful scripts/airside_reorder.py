'''
add docstring
'''

import glob as gb
import os
import shutil


#deal with directories and file names
filename = 'newinp.inp'
directory = "Airside Rezone"
tochange = 'Base Extell 221 West 57th St'
inpfile = tochange + ".inp"
pd2file = tochange + ".pd2"
newpd2file = filename[0:-4] + '.pd2'

try:
    os.makedirs(directory)
except os.error:
    pass


#make blank lists / dictionaries
sysnames = []
sysstart = []
sysend = []
sysval = []
sysdict = {}


#start to parse
with open(inpfile) as f:
    f_list = f.readlines()

for num, line in enumerate(f_list):

    if "= SYSTEM" in line:
        splitter = line.split("\"")
        newline = splitter[1]
        sysnames.append(newline)
        sysstart.append(num)
        sysend.append(num-1)

    if "Metering & Misc HVAC" in line:
        sysend.append(num-3)
        sysend = sysend[1:]


#write system names to text file 
with open(directory + "\\" + 'sysnames.txt', 'w') as output:
    for f in sysnames:
        output.write(f)
        output.write("\n")

for num, line in enumerate(sysnames):
    key = line
    start = sysstart[num]
    end = sysend[num] + 1
    val = f_list[start:end]
    sysval.append(val)
    sysdict[line] = val


#read user-defined system order
with open(directory + '\sysnamesnew.txt') as f:
    systext = f.readlines()

newsysorder = []
for s in systext:
    s = s.strip("\n")
    newsysorder.append(sysdict[s])


#write new inp
f_listnew = []
list1 = f_list[0:sysstart[0]]
list2 = newsysorder
list3 = f_list[sysend[-1]:]

f_listnew.append(list1)
for l in list2:
    f_listnew.append(l)
f_listnew.append(list3)

f_liststring =  ''.join(str(r) for v in f_listnew for r in v)


#write files / remove existing
if os.path.exists(filename):
    os.remove(filename)

with open(directory + "\\" + filename, 'w') as output:
    output.write(f_liststring)

try:
    shutil.copy(pd2file,(directory + "\\" + newpd2file))
except shutil.Error:
    pass
