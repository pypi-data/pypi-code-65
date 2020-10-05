#!/usr/bin/env python3

from datetime import date,datetime,timezone,timedelta
#import time
import collections
import re

import sys
sys.path.insert(1, '../src')
import jdata

# Some test dates
utc=datetime(2020,8,20,10,20,30)
utcoffset = round((datetime.now()-datetime.utcnow()).total_seconds())
loc=utc+timedelta(seconds=utcoffset)
unix=utc.timestamp()
#utc=datetime.now(timezone.utc)
#loc=datetime.now().replace(microsecond=0)
#unix=utc.timestamp()

# Test object creation
data={}
data["none"]=None
data["str"]="String"
data["bool"]=True
data["num"]=42
data["float"]=4.2
data["date"]={"local":loc,"utc":utc,"unix":unix}
data["list"]=["a1","a2","a3"]
data["dict"]={"x":20,"y":22}
data["complex"]=[{"var":"uno","val":1},{"var":"dos","val":2}]

# Pretty print
jdata.colprint(data, "data")

# Convertimos a json
jsonverify='{"none":null,"str":"String","bool":true,"num":42,"float":4.2,"date":{"local":"2020-08-20T12:20:30","utc":"2020-08-20T10:20:30","unix":1597911630.0},"list":["a1","a2","a3"],"dict":{"x":20,"y":22},"complex":[{"var":"uno","val":1},{"var":"dos","val":2}]}'
json=jdata.tojson(data)
if json!=jsonverify:
	print("Error converting data to json!")
	print("converted: "+json)
	print("should be: "+jsonverify)
	print
	exit(1)
jdata.colprint(json, "json")

# Convertimos otra vez a dict
data2=jdata.fromjson(json)
if data!=data2:
	print("Error converting json to data!")
	exit(1)

# Guardamos y leemos fichero json
jdata.writejson(data,"test.json", tabs=1)
data2=jdata.readjson("test.json")
if data!=data2:
	print("Error writing or reading json!")
	exit(1)

# Guardamos y leemos fichero yaml
jdata.writeyaml(data,"test.yaml")
data2=jdata.readyaml("test.yaml")
if data!=data2:
	print("Error writing or reading yaml!")
	exit(1)
