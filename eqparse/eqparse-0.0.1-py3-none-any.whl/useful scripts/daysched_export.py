import glob as gb
import os
import numpy as np
import pandas as pd
import xlwings as xw

def daysched_export(inpfile):
#varexplore = True
#if varexplore:
    
    fname = "__day_schedules.csv"
    if os.path.isfile(fname):
        os.remove(fname)

    inpschedules = []
    schednames = []
    types = []
    valuestart = []
    valueend = []
    
    with open(inpfile, encoding="Latin1") as f:
        f_list = f.readlines() 
    
    for num, line in enumerate(f_list):
        if "$              Day Schedules" in line:
            start = num
        if "$              Week Schedules" in line:
            end = num
            
    inpschedules.append(f_list[start:end])
    
    for num, l in enumerate(inpschedules[0]):
        if "DAY-SCHEDULE-PD" in l:
            name = l.strip(" = DAY-SCHEDULE-PD")
            schednames.append(name)
        
        if "TYPE             =" in l:
            name = l.strip().strip('TYPE             =')
            types.append(name)
        
        if "VALUES           =" in l:
            valuestart.append(num)
        
        if ".." in l:
            valueend.append(num)
  
    for num, t in enumerate(types):
        if "RESET" in t:
            types.pop(num)
            schednames.pop(num)
            valueend.pop(num)
	
	#i dont know why but the above has to be done again to get all the schedules. 
	#if you're getting an error, try adding more of the enumerate(types) object
	#until it works? or just debug.
    for num, t in enumerate(types):
        if "RESET" in t:
            types.pop(num)
            schednames.pop(num)
            valueend.pop(num)

    valstring = []
    for num, l in enumerate(valuestart):
        val = str(inpschedules[0][valuestart[num]:valueend[num]])
        val = val[25:-5]
        val = val.replace('\\n\', \'         ', '')
        valstring.append(val.strip())
         
    valstringsplit = []        
    for v in valstring:
        splitter = v.split(", ")
        valstringsplit.append(splitter)
        v.replace('&D','jklsdfjklfsd'[:])
    
    schednamesclean = []
    for s in schednames:
        r = s.replace("\" = DAY-SCHEDULE-PD","").replace("\"","")
        schednamesclean.append(r)
                    
    valdf = pd.DataFrame(valstringsplit,index=schednamesclean)
    valdf = valdf.astype(float, errors='ignore')
    valdf = valdf.fillna(method='ffill', axis=1)
    valdf = valdf.replace("&D",np.nan)
    valdf = valdf.fillna(method='ffill',axis=1)
    valdf['Schedule Type'] = types
    valdf = valdf.replace("MPERATUR","TEMPERATURE")
    cols = valdf.columns.tolist()
    cols = cols[-1:]+cols[:-1]
    valdf = valdf[cols]

    with open(fname, 'a') as f:
        valdf.to_csv(f)
    wb = xw.Book(fname)
    wb.close()
