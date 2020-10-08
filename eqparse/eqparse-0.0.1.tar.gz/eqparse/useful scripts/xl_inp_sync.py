'''
a series of functions allowing user to collect objects in equest
and assign new values to them and also update existing values.

NEED SOME WAY TO ADD AN AUTO-DETECT BDLTYPE (MAYBE 'SYSTEM' OR 'ZONE' IN FIRST COLUMN OF SPREADSHEET?)

TOP LEVEL FUNCTIONS TO USE: xlmatrixupdate

'''

from collections import OrderedDict
import re
import numpy as np
import pandas as pd
import operator
import inp.objects as objects
import xlwings as xw

def inp_to_xl(wkbk, sht, bdltype, oldinp,tocsv=False):
    '''
    top level function
    update excel file with matrix from specified input file
    dependent upon writeinp
    needs:
    get, writeinp, update
    if tocsv = True, csv file will be created.
        in this case, "wkbk" will be used as 'csv' file
        and will return an error
    '''

    flist = objects.openinp(oldinp)
    bdldict = objects.get(flist,bdltype)
    for key, value in bdldict.items():
        value.popitem(0)    
    numsystems = len(bdldict)
    bdldf = pd.DataFrame.from_dict(bdldict).transpose()
    
    
    
    if not tocsv:
        if ".xls" not in wkbk:
            print ("ERROR: ARG 'TOCSV=FALSE' PASSED, BUT\nNON-XLS FILE PASSED TO WKBK")
            return "error"
    
        wb = xw.Book(wkbk)
        writesht = wb.sheets[sht]
        
        
        writesht.range('A:ZZ').clear()
        writesht.range('A1').value= bdldf
    #    writesht.range('A:ZZ').options(pd.DataFrame).value
    if tocsv:
        if ".csv" in wkbk:
            
            with open (wkbk, 'a') as f:
                bdldf.to_csv(f, header = True)
        else:
            print ("ERROR: ARG 'TOCSV=TRUE' PASSED, BUT\nNON-CSV FILE PASSED TO WKBK")
            
    return bdldf





def xl_to_inp(wkbk, sheet, bdltype, oldinp, newinp):

    '''
    top level function
    update inp file with matrix from specified excel document
    dependent upon writeinp
    needs:
    get, writeinp, update
    '''
    
    flist = objects.openinp(oldinp)
    
    bdldict = objects.get(flist, bdltype)
    bdlupdate = pd.read_excel(wkbk, sheet_name=sheet)
    
    collist = bdlupdate.columns.tolist()
    print (collist)
#    print (bdlupdate)
 
    for index, row in bdlupdate.iterrows():
        for num, line in enumerate(row):
            try:
                objects.updatedict(bdldict, index, collist[num], line)
            except KeyError:
                print (line)
#                print (index)
#                print (row)
#                print (bdltype)

    objects.writeinp(flist, newinp, bdldict)
    
    return bdldict       
    




