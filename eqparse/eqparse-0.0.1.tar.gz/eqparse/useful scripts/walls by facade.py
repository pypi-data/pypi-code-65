import os
import glob
import sqlite3
import shutil
import re
import xlwings as xw

from string import digits

inpfile = 'Prop Extell  221 West 57th St.inp'

with open(inpfile, encoding="Latin1") as f:
    f_list = f.readlines()   
 
wallnum = []
constnum = []
wallstrip = []
for num, line in enumerate(f_list):
    if "= EXTERIOR-WALL" in line:
        wallnum.append(num)
        wallstrip.append(line)      
        
facade = []       
for w in wallstrip:
    splitter = w.split(" ")
    facade.append(splitter)      
    
facade2 = []  

for f in facade:
    remove_digits = str.maketrans('', '', digits)
    res = f[0].translate(remove_digits)
    res = res[1:]
    if len(res) == 0:
        res = "S"
    facade2.append(res)
    
for f in facade2:
    if len(f) == 0:
        f = "S"
       
exp = []
for f in facade2:
    exp.append(f[0])

expchar = []
for e in exp:
    n = "   CONSTRUCTION     = " + "\"" + e[0] + " - TOWER CONST\""
    expchar.append(n)
#
    
newinp = f_list

for num, line in enumerate(wallnum):
    #print (newinp[n-1])
    #myline = expchar[n]
    newinp[line+1] = expchar[num]
    
fname = 'newinp.inp'

with open(fname, 'w') as f:
    f.write("\n".join(newinp))

