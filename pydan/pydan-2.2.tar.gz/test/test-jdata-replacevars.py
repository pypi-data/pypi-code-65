#!/usr/bin/env python3

#from pydan import jdata

import sys
sys.path.append('..')
from src import jdata

ret=0

# Comprobamos reemplazo de multiples variables en un string
data={"numbers":"$n1$,$n2$,$n3$,$nx$"}
repl=jdata.replacevars(data, {"n1":"one", "n2":"two", "n3":"three", "n4":"four"})
if repl["numbers"]!="one,two,three,$nx$":
	print("ERROR reemplazando multiples variables en un mismo string")
	print(repl["numbers"])
	ret=1
else:
	print("OK: Reemplazo de multiples variables en un mismo string")

# Comprobamos reemplazo de distintos tipos de datos
data={
	"rep_str":"$str$",
	"rep_num":"$num$",
	"rep_list":"$list$",
	"rep_dict":"$dict$",
	"rep_null":"$null$",
	"rep_empty":"$empty$",
	"rep_unk":"$unk$",
	"ori_empty":"",
	"ori_null":None,
	"ori_list": [ "a", "b" ],
	"ori_dict": { "ori_a":0, "ori_b":1 },
}
repl=jdata.replacevars(data, {"str":"str", "num":1, "list":["a","b"], "dict":{"a":0,"b":1},"null":None,"empty":""})
repljson=jdata.tojson(repl)
if repljson!='{"rep_str":"str","rep_num":1,"rep_list":["a","b"],"rep_dict":{"a":0,"b":1},"rep_null":null,"rep_empty":"","rep_unk":"$unk$","ori_empty":"","ori_null":null,"ori_list":["a","b"],"ori_dict":{"ori_a":0,"ori_b":1}}':
	print("Error reemplazando distintos tipos de datos")
	jdata.colprint(data, "Original")
	jdata.colprint(repl, "Replaced")
	exit(1)
print("OK: Reemplazo de diferentes tipos de datos")

# Comprobamos borrado de variables con reemplazo a null
data={
	"rep_str":"$str$",
	"rep_num":"$num$",
	"rep_list":"$list$",
	"rep_dict":"$dict$",
	"x_rep_null":"$null$",
	"x_rep_empty":"$empty$",
	"x_rep_unk":"$unk$",
	"ori_empty":"",
	"ori_null":None,
	"ori_list": [ "a", "b" ],
	"ori_dict": { "ori_a":0, "ori_b":1 },
}
repl=jdata.replacevars(data, {"str":"str", "num":1, "list":["a","b"], "dict":{"a":0,"b":1},"null":None,"empty":""}, flags=["nullremove","emptyremove", "unkremove"])
#jdata.colprint(data, "Original")
jdata.colprint(repl, "Replaced")

exit(ret)
