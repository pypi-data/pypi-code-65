import numpy as np
from zla_utilities import \
    db_connector as dbcon
import warnings
warnings.filterwarnings("ignore")

def customer_parentable(customer,parent):
    if customer is not None:
        ans = np.array([customer])
        if parent == True:
            db = 'partsdatabase'
            msql = "select customerid from customerlistsap where parent = '{}'".format(customer)
            cus_list = dbcon.opendata(msql,db)['customerid'].values
            if len(cus_list) > 0:
                ans = cus_list
    else:
        ans = None
    return ans

def get_partsmaster(_partno):
    db = 'partsdatabase'
    msql =  "select partname,mrpcn,pdt+grt as LT, weight,MS,submodel from partsmaster where partno = '{}'".format(_partno)
    _ans = dbcon.opendata(msql,db).loc[0].to_dict()
    return _ans

def get_partscharacter(_partno):
    db = 'partsdatabase'
    msql =  "select groupid, frequency ,notice, controller,charc as chars,createon from partscharacter where partno = '{}'".format(_partno)
    _ans = dbcon.opendata(msql,db).loc[0].to_dict()
    return _ans

def get_partspurchasing(_partno):
    db = 'partsdatabase'
    msql =  "select pgr,spt,proctype from partspurchasing where partno = '{}'".format(_partno)
    _ans = dbcon.opendata(msql,db).loc[0].to_dict()
    return _ans