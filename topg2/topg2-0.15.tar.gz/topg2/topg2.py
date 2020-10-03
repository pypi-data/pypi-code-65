#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 12:13:13 2020
Dataframe methods to implement cursor copy to postgress. 

Assumptions: 
    The dataframe should have a unique integer field named id, because the 
    create table cooks that in. 
    
    For the test in __main__, there would need be a file ~/secret/db.json with
    {'host': '##', 'database': 'postgres', 'user': '##', 'password': '##'}

Following methods are added to DataFrame
    rdbType - return a dataframe of fieldName, fieldType for creating rdb table
    createTableS - return a string sql create_table 
    createTable - execute the createTableS
    pg2Append - use cursor copy_from to append dataframe to table
    topg2 - creates table if needed, appends dataframe to table 

@author: johnlichtenstein@gmail.com
"""

import pandas as pd # for testing in __main__
from pandas import DataFrame # import DataFrame separately to act on
import psycopg2 as pg2 
import tempfile
import os

FMTD = {"int64": "bigint", "object": "text", "float64": "double precision" \
        , "bool": "boolean", "datetime64[ns]": "date" \
        , "float32": "double precision"}
NULLS = "~"

def rdbType(self):
    """
    Build a dataframe of formats to use for table creation. The normal way 
    to call this is from createTableS. But in case you want to review or 
    change some mappings, it can be called on its own    

    Parameters
    ----------
        
    Returns
    -------
    Dataframe 
        cName: from self.columns
        cType: from self.dtypes
        sType: string representation of cType
        dbFmt: format to use for column in relational table 
    """

    nameL = "cName cType dbFmt".split()
    tR = self.dtypes.reset_index()
    tR.columns=nameL[:2]
    tR["sType"] = tR.cType.astype(str)
    
    tempL = []
    for i, obs in tR.iterrows():
        try:
            fmt = FMTD[obs.sType]
        except KeyError:
            fmt = "text"
                
        tempL.append(fmt)
    
    tR["dbFmt"] = tempL

    return tR

def createTableS(self, tableName, schema="public"):
    """
    Creates a string to create table. Expects a unique integer id. 
    
    Parameters
    ----------
    tableName : string
        Name of table to create.
    schema : string, optional
        Name of schema to place table in. The default is "public".

    Returns
    -------
    str.

    """

    fmtR = self.rdbType() 
       
    headS = "CREATE TABLE {schemaN}.{tabN} ("

    othR = fmtR.query("cName != 'id'")
    bodyL = ['"id" SERIAL PRIMARY KEY']
    for (cN, tN) in zip(othR.cName, othR.dbFmt):
        bodyL.append(""""{cN}" {tN}""".format(cN=cN, tN=tN))

    bodyS = "\n\t, ".join(bodyL)
    
    ctS = "".join((headS, bodyS, ");"))
        
    return ctS.format(schemaN=schema, tabN=tableName)

def createTable(self, conn, tableName, schema="public"):
    """
    Create a table for self named schema.tableName on conn. Connection will 
    *not* be closed weather or not table is created. So the connection will 
    need closing. The normal way to call this is from topg2. But you might 
    want to check that table creation works as expected.

    Parameters
    ----------
    conn : psycopg2.extensions.connection
        open connection to postgress.
    tableName : string
        Name of table to create.
    schema : string, optional
        Name of schema to place table in. The default is "public".

    Returns
    -------
    None.
    """
       
    sqlS = self.createTableS(tableName, schema=schema)
        
    cur = conn.cursor()
    # print ("opened cursor")
    try:
        cur.execute(sqlS)
    except pg2.errors.DuplicateTable:
        # this is fine
        cur.close()
        return None
    except (Exception, pg2.DatabaseError) as error:
        cur.close()
        print (error)
        return error
    else:
        conn.commit()
        cur.close()
        return None

def pg2Append(self, tableName, conn, schema="public", sep="|", null=NULLS):
    """
    Save self in pg2 table, creating table if needed. Creates a tempfile and 
    uses cursor copy. Tempfile is not deleted on failure in case user needs 
    to check it out. 

    Parameters
    ----------
    conn : psycopg2.extensions.connection
        open connection to postgress.
    tableName : string
        Name of table to create.
    index : string, optional
        Name of single column to use as index. 
        The default is None, and no index is created in that case.
    schema : string, optional
        Name of schema to place table in. The default is "public".
    sep : str, optional
        delimiter for temp file. The default is "|".

    Returns
    -------
    None : success
    str: Name of tempfile serialization of self
    """
    
    # first check for mad id
    try:
        maxId = pd.read_sql("select max(id) as mid from %s" %(tableName) \
                            , conn).iloc[0].mid + 1
    except:
        maxId = 0

    if maxId == None:
        maxId = 0

    tempR = self.copy()
    tempR.id = tempR.id + [maxId] * len(tempR)
        
    tempF = tempfile.NamedTemporaryFile(mode="w", delete=False)
    tempName = tempF.name
    tempR.to_csv(tempName, sep=sep, index=False, header=False)
    tempF.close()
    
    tempF = open(tempName)
    
    cur = conn.cursor()
    try:
        cur.copy_from(tempF, tableName, sep=sep, null=null)
        conn.commit()
    except (Exception, pg2.DatabaseError) as error:
        print("Error: %s" %(error))
        print("in topg2 with %s" %(tempName))
        conn.rollback()
        cur.close()
        tempF.close()
        return tempName
    else:
        tempF.close()
        os.remove(tempName)
        return None

    return None     


def topg2(self, tableName, conn, schema="public", sep="|", null=NULLS):   
    """
    Save self in pg2 table, creating table if needed. Creates a tempfile and 
    uses cursor copy. Tempfile is not deleted on failure in case user needs 
    to check it out.

    Parameters
    ----------
    conn : psycopg2.extensions.connection
        open connection to postgress.
    tableName : string
        Name of table to create.
    schema : string, optional
        Name of schema to place table in. The default is "public".
    sep : str, optional
        delimiter for temp file. The default is "|".
    null : str, optional
        string to use for null values. defaults to "~"

    Returns
    -------
    None : success
    str: Name of tempfile serialization of self
    """
       
    # check for existing
    Q = """select count(*) as n
    from information_schema.tables
    where table_schema = '{sn}' 
        and table_name = '{tn}'
    """.format(sn=schema, tn=tableName)
    
    N = pd.read_sql(Q, conn).iloc[0].n
    if N:
        # table exists, we can just append
        pass
    else:
        self.createTable(conn, tableName, schema=schema)
        
    self.fillna(value=null) \
        .pg2Append(tableName, conn, schema=schema, sep=sep, null=null)
    
    return None

DataFrame.rdbType = rdbType
DataFrame.createTableS = createTableS
DataFrame.createTable = createTable
DataFrame.pg2Append = pg2Append
DataFrame.topg2 = topg2 

if __name__ == "__main__":
    import json
    TABNAME = "table0" 

    SECRET = os.path.join(os.path.join(os.path.expanduser("~") \
                                        , "secret"), "db.json")
    tD = json.load(open(SECRET))
    # print (tD)
    
    conn = pg2.connect(**tD)
    
    # create dataframes to store
    exampleD = {"sv": "a a a a a b b b b b".split() \
                , "x": [1, "two", 3, 2, 3, 4, 4, 5, 6, 1]}
    extraD = {"sv": "c c c c c d d d d d".split() \
                , "x": [1, 2, 3, 2, 3, 4, 4, 5, 6, 1]}

    exampleR = pd.DataFrame(exampleD).reset_index() \
        .rename(columns={"index": "id"}) 
    exampleR.x = pd.to_numeric(exampleR.x, errors='coerce', downcast="float")
    extraR = pd.DataFrame(extraD).reset_index().rename(columns={"index": "id"})
    # extraR.id = extraR.id + [len(exampleR)] * len(extraR) # now internal
    

    test = exampleR.topg2(TABNAME, conn)   
    print (test) # none is good
    test = extraR.topg2(TABNAME, conn)   
    print (test) # none is good
    print (pd.read_sql("select count(*) from %s" %(TABNAME), conn))
    conn.close() # expecting 20

