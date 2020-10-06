#!/usr/bin/env python3

# Data Helpers

import re
import collections
import os
import sys
import io
import binascii
import random
from datetime import datetime,timezone
import base64
import platform # platform.node() -> hostname
# for yaml
#from ruamel.yaml.comments import CommentedMap
import ruamel.yaml
# for json
import json
# for xml
import dicttoxml
# self tools
from pydan import run

# repair LANG=C -> utf8
if(sys.getfilesystemencoding()=="ascii" and sys.getdefaultencoding()=="utf-8"):
	sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

c={
	"none":"\033[0m",
	"header":"\033[38;5;166m",  # orange
	"group":"\033[1;34m",       # light blue
	"item":"\033[0;36m",        # cian
	"null":"\033[1;30m",        # gray
	"date":"\033[38;5;105m",    # xviolet
	"str":"\033[0;32m",         # green
	"int":"\033[1;32m",         # light green
	"float":"\033[38;5;112m",   # xolive
	"bool":"\033[1;36m",        # white
	"unk":"\033[0;31m",         # red
	"varint":"\033[1;35m",      # magentab
	"varenv":"\033[0;35m",      # magenta
	"varcmd":"\033[1;31m",      # red
	"err":"\033[1;31m",         # light red
	"important":"\033[1;33m",   # light red
}

#{{{ colprint: Imprime un dict por pantalla con colores según el tipo de datos
def colprint(d,header=None,key=None,indent="",crop=True):
	indentchars="    "
	if(header): print(c["header"]+header+c["none"]);indent=indent+indentchars

	# Si es diccionario iteramos
	if(type(d)==dict or type(d)==collections.OrderedDict): # or type(d)==CommentedMap):
	#if(type(d)==dict or type(d)==collections.OrderedDict or type(d)==CommentedMap):
	#if hasattr(d,'__iter__') and type(d)!=str:
		if key is not None : print(indent+c["group"]+key+":"+c["none"]); indent+=indentchars
		if len(d)==0: print(indent+c["null"]+"empty"+c["none"])
		else:
			for k in d: colprint(d[k], key=k, indent=indent)
		return

	# Si es lista listamos con [indice]
	#if(type(d)==list):
	#	i=0
	#	print(indent+c["group"]+key+":"+c["none"])
	#	indent=indent+indentchars
	#	# Lista de strings
	#	#if type(key[0])==str:
	#	#	for k in d:
	#	#		print(indent+c["item"]+"["+str(i)+"]: "+c["none"], end='')

	#	#for k in d:
	#	#	#print(indent+c["group"]+key+"["+str(i)+"]:"+c["none"])
	#	#	#colprint(k, indent=indent+indentchars)
	#	#	#print(indent+c["item"]+"["+str(i)+"]: "+c["none"], end='')
	#	#	colprint(k, indent=indent+c["item"]+"["+str(i)+"]: ")
	#	#	i=i+1
	#	#	#print(k);
	#
	#	for k in d:
	#		#print(indent+c["group"]+key+"["+str(i)+"]:"+c["none"])
	#		print(indent+c["group"]+"["+str(i)+"]:"+c["none"])
	#		colprint(k, indent=indent+indentchars)
	#	#	#print(indent+c["item"]+"["+str(i)+"]: "+c["none"], end='')
	#		#colprint(k, indent=indent+c["item"]+"["+str(i)+"]: ")
	#		i=i+1
	#		#print(k);
	#	return

	if type(d)==list or type(d)==tuple:
		# Vacia
		if len(d)==0:
			if(key!=None):
				print(indent+c["group"]+key+"[]: "+c["null"]+"empty"+c["none"]);
			else:
				print(indent+c["null"]+"empty"+c["none"])
			return

		# Lista de strings o ints
		if type(d[0])==str or type(d[0])==int:
			i=0
			if key!=None:
				print(indent+c["group"]+key+":"+c["none"])
				for k in d:
					colprint(str(k), key="["+str(i)+"]", indent=indent+indentchars)
					i+=1
			else:
				for k in d:
					colprint(str(k), key="["+str(i)+"]", indent=indent)
					i+=1
			return

		#for k in d:
		#	#print(indent+c["group"]+key+"["+str(i)+"]:"+c["none"])
		#	#colprint(k, indent=indent+indentchars)
		#	#print(indent+c["item"]+"["+str(i)+"]: "+c["none"], end='')
		#	colprint(k, indent=indent+c["item"]+"["+str(i)+"]: ")
		#	i=i+1
		#	#print(k);

		# Lista de objetos
		if(type(d[0])==dict or type(d[0])==collections.OrderedDict):
			i=0
			for k in d:
				if key is None: key=""
				print(indent+c["group"]+key+"["+str(i)+"]:"+c["none"])
				colprint(k, indent=indent+indentchars)
				i=i+1
			return

		print(c["err"]+"¿list of "+type(d[0]).__name__+"?"+c["none"])
		return
		#print("unknown "+type(d).__name__)
		#return

	# Mostramos key
	if(key!=None): print(indent+c["item"]+key+": ", end='')
	else: print(indent, end='')

	# Mostramos valor
	t=type(d)
	if(t==str):
		p=re.compile("\$([a-zA-Z0-9_]*)\$")
		vars=set(p.findall(d))
		for k in vars: d=re.sub("\$"+k+"\$", c["varenv"]+"$"+k+"$"+c["str"], d)
		p=re.compile("\%([a-zA-Z0-9_]*)\%")
		vars=set(p.findall(d))
		for k in vars: d=re.sub("\%"+k+"\%", c["varint"]+"%"+k+"%"+c["str"], d)
		p=re.compile("\(\(([^)]*)\)\)")
		vars=set(p.findall(d))
		for k in vars: d=re.sub("\(\(.*\)\)", c["varcmd"]+"(("+k+"))"+c["str"], d)
		if crop and len(d)>4000:
			print(c["important"]+"###DATA-"+str(len(d))+"###"+c["none"])
		else:
			print(c["str"]+d+c["none"])
	elif(t==datetime):
		dtstr=re.sub("\+00:00", "Z", d.isoformat())
		#dtstr=d.__str__()
		print(c["date"]+dtstr+c["none"])
	elif(t==int):
		print(c["int"]+str(d)+c["none"])
	elif(t==float):
		print(c["float"]+str(d)+c["none"])
	elif(t==bool):
		print(c["bool"]+str(d)+c["none"])
#	elif(t==list):
#		print
#		for i in d:
#			colprint(i,header="x",indent=indent)
#			#print(indent+indentchars+c["str"]+i)
#			#print(d)
	elif(t==type(None)):
		print(c["null"]+"null"+c["none"])
	else:
		print(c["err"]+"¿"+str(t.__name__)+"?"+c["none"])
#}}}

# Por cada item en d reemplaza $var$ por el valor de la variable en la lista varlist
#{{{ replacevars
def replacevarsold(d, varlist, unknownempty=False, emptyremove=False, unknownnull=False, emptynull=False, __debugiter=0):
	#o=collections.OrderedDict()
	o={}
	#for di in range(0,__debugiter): print("    ", end="")
	#print("replacevars:")
	__debugiter=__debugiter+1
	for k in d:
		#for di in range(0,__debugiter): print("    ", end="")
		#print(f"- {k} [{type(d[k]).__name__}]")
		if type(d[k])==dict or type(d[k])==collections.OrderedDict:
			d[k]=replacevarsold(d[k], varlist, unknownempty=unknownempty, emptyremove=emptyremove, unknownnull=unknownnull, emptynull=emptynull, __debugiter=__debugiter)
			o[k]=d[k]
			continue
		elif type(d[k])==list:
			o[k]=[]
			__debugiter=__debugiter+1
			for i in d[k]:
				for di in range(0,__debugiter): print("    ", end="")
				#print(f"* item {i}")
				o[k].append(replacevarsold(i, varlist, unknownempty=unknownempty, emptyremove=emptyremove, unknownnull=unknownnull, emptynull=emptynull, __debugiter=__debugiter))
			continue
		else:
			if(type(d[k])==str):
				#if(d[k][0]=='$'):
				#	var=d[k][1:-1]
				#	v=varlist.get(var)
				#	if(v): o[k]=v
				#else:
				#	o[k]=d[k]

				# Buscamos variables en varlist
				p=re.compile("\\$([a-zA-Z0-9_]*)\\$")
				vars=set(p.findall(d[k]))
				# No hay variables
				if vars is None:
					o[k]=d[k]
					continue
				# Hay variables
				for sk in vars:
					val=varlist.get(sk)
					if val is None:
						if(unknownempty): val=""
						else:
							if(unknownnull):
								if emptynull: val="$null$"
								else: val="null"
							else:
								continue
					#if d[k]==f"${sk}$":  # python 3.6
					if d[k]=="$"+sk+"$":  # python 3.6
						# si el valor es exacto ("$var$"), reemplazamos por el tipo de objeto de varlist
						d[k]=val
					else:
						# reemplazamos dentro del string
						d[k]=re.sub("\\$"+sk+"\\$", str(val), d[k])

				if(d[k]=="$null$" and emptynull): continue
				if(d[k]=="" and emptyremove): continue
				o[k]=d[k]
			else:
				o[k]=d[k]
	return o
#}}}

def replacevars(data, varlist, flags=[], __debugiter=0):
	__debug=False
	#__debug=True

	unkvar=re.compile("^\\$([a-zA-Z0-9_]*)\\$$")

	if __debug:
		for di in range(0,__debugiter): print("    ", end="")
		print("\033[1;33mreplacevars:\033[0m")
		__debugiter=__debugiter+1

	if type(data)==str:
		return replacevars_str(data, varlist, __debugiter=__debugiter)

	if type(data)==dict:
		if __debug:
			for di in range(0,__debugiter): print("    ", end="")
			print("\033[32mdict:\033[0m")
			__debugiter=__debugiter+1
		o={}
		for k,v in data.items():
			if __debug:
				for di in range(0,__debugiter): print("    ", end="")
				#print(f"\033[33m- Item '{k}' [{type(data[k]).__name__}]\033[0m")  # python 3.6
				print("\033[33m- Item '"+k+"' ["+type(data[k]).__name__+"]\033[0m")  # python 3.6
			if type(v)==str:
				r=replacevars_str(v, varlist, __debugiter=__debugiter)
				add=True
				if "nullremove" in flags and r is None and v is not None: add=False
				if "emptyremove" in flags and r=="" and v!="": add=False
				if "emptynull" in flags and r=="" and v!="": r=None
				if "unkremove" in flags and type(r)==str and unkvar.match(r): add=False
				if "unkempty" in flags and type(r)==str and unkvar.match(r): r=""
				if "unknull" in flags and type(r)==str and unkvar.match(r): r=None
				if add: o[k]=r
			else:
				o[k]=replacevars(v, varlist, flags=flags, __debugiter=__debugiter)
		return o

	if type(data)==list:
		o=[]
		if __debug:
			for di in range(0,__debugiter): print("    ", end="")
			print("\033[32mlist:\033[0m")
			__debugiter=__debugiter+1
		for k in data:
			if __debug:
				for di in range(0,__debugiter): print("    ", end="")
				#print(f"\033[33m- Item '{k}' [{type(k).__name__}]\033[0m")
				print("\033[33m- Item '"+k+"' ["+type(k).__name__+"]\033[0m")
			oi=replacevars(k, varlist, flags=flags, __debugiter=__debugiter)
			o.append(oi)
		return o

	if type(data)==set:
		o=set()
		if __debug:
			for di in range(0,__debugiter): print("    ", end="")
			print("\033[32mset:\033[0m")
			__debugiter=__debugiter+1
		for k in data:
			if __debug:
				for di in range(0,__debugiter): print("    ", end="")
				#print(f"\033[33m- Item '{k}' [{type(k).__name__}]\033[0m")
				print("\033[33m- Item '"+k+"' ["+type(k).__name__+"]\033[0m")
			oi=replacevars(k, varlist, flags=flags, __debugiter=__debugiter)
			o.add(oi)
		return o

	# unknown!
	if __debug:
		for di in range(0,__debugiter): print("    ", end="")
		#print(f"\033[1;31m¿{type(data).__name__}?\033[0m")
		print("\033[1;31m¿"+type(data).__name__+"?\033[0m")
	return data

#	for k in d:
#		for di in range(0,__debugiter): print("    ", end="")
#		print(f"\033[33m- {k} [{type(d[k]).__name__}]\033[0m")
#		if type(d[k])==dict or type(d[k])==collections.OrderedDict:
#			d[k]=replacevars2(d[k], varlist, unknownempty=unknownempty, emptyremove=emptyremove, unknownnull=unknownnull, emptynull=emptynull, __debugiter=__debugiter)
#			o[k]=d[k]
#			continue
#		elif type(d[k])==list:
#			o[k]=[]
#			__debugiter=__debugiter+1
#			for i in d[k]:
#				for di in range(0,__debugiter): print("    ", end="")
#				print(f"* item {i}")
#				o[k].append(replacevars2(i, varlist, unknownempty=unknownempty, emptyremove=emptyremove, unknownnull=unknownnull, emptynull=emptynull, __debugiter=__debugiter))
#			continue
#		else:
#			if(type(d[k])==str):
#				o[k]=replacevars2_str(d[k], varlist, unknownempty=unknownempty, emptyremove=emptyremove, unknownnull=unknownnull, emptynull=emptynull, __debugiter=__debugiter)
#	return o
#}}}

def replacevars_str(data, varlist, __debugiter=0):
	__debug=False
	#__debug=True
	if __debug:
		for di in range(0,__debugiter+1): print("    ", end="")
		#print(f"\033[34mreplacevars2_str: '{data}'\033[0m", end="")
		print("\033[34mreplacevars2_str: '"+data+"'\033[0m", end="")
	out=data
	p=re.compile("\\$([a-zA-Z0-9_]*)\\$")
	vars=p.findall(data)
	# No hay variables
	if len(vars)==0:
		if __debug:
			print(" (no vars)", end="")
		out=data
	else:
		if __debug:
			print(" (vars found)", end="")
		# Hay variables
		for sk in vars:
			if __debug:
				print(" (repl "+sk+")", end="")
			if sk not in varlist: continue
			val=varlist.get(sk)
			#if val is None:
			#	if(unknownempty): val=""
			#	else:
			#		if(unknownnull):
			#			if emptynull: val="$null$"
			#			else: val="null"
			#		else:
			#			continue

			# TODO: no borrar variables que no existen!
			if data=="$"+sk+"$":
				# si el valor es exacto ("$var$"), reemplazamos por el tipo de objeto de varlist
				out=val
			else:
				# reemplazamos dentro del string
				out=re.sub("\\$"+sk+"\\$", str(val), out)

		#if(out=="$null$" and emptynull): out=None
		#if(out=="$null$"): out=None
		#if(out=="" and emptyremove): out=None  # ???? TODO
	if __debug: print("\033[34m -> '"+out+"' ["+type(out).__name__+"]\033[0m")
	return out
#}}}

# Por cada item en d reemplaza $e$var$ por variable de entorno
#{{{ replaceenv
def replaceenv(d, unknownempty=False, emptyremove=None):
	o=collections.OrderedDict()
	for k in d:
		if(type(d[k])==dict or type(d[k])==collections.OrderedDict):
			d[k]=replaceenv(d[k], unknownempty=unknownempty, emptyremove=emptyremove)
			o[k]=d[k]
			continue
		else:
			if(type(d[k])==str):
				p=re.compile("\$e$([a-zA-Z0-9_]*)\$")
				vars=set(p.findall(d[k]))
				# No hay variables
				if(vars is None):
					o[k]=d[k]
					continue
				# Hay variables
				for sk in vars:
					if (sk=="HOSTNAME"): val=platform.node()
					else: val=os.environ.get(sk)
					if(val is None):
						if(unknownempty): val=""
						else: continue
					d[k]=re.sub("\$e\$"+sk+"\$", val, d[k])

				if(d[k]=="" and emptyremove): continue
				o[k]=d[k]
			else:
				o[k]=d[k]
	return o
#}}}

# Por cada item en d reemplaza ((cmd)) por la ejecución de cmd
# Por cada item en d reemplaza $b$file$ por el fichero en b64
# Por cada item en d reemplaza $t$file$ por el contenido del fichero
#{{{ runvars
def runvars(d, unknownempty=False, emptyremove=None):
	o=collections.OrderedDict()
	for k in d:
		if(type(d[k])==dict or type(d[k])==collections.OrderedDict):
			d[k]=runvars(d[k], unknownempty=unknownempty, emptyremove=emptyremove)
			o[k]=d[k]
			continue
		else:
			if(type(d[k])==str):
				modified=False

				# Comando a ejecutar
				r_buscacmd=re.compile("\(\((.*)\)\)")
				vars=set(r_buscacmd.findall(d[k]))
				# No hay variables
				if(vars==None):
					o[k]=d[k]
				#	continue
				else:
					modified=True
					# Hay variables
					for sk in vars:
						# b|fichero -> base64 fichero
						#sk=re.sub(r"^t\|(.*)$", r"cat '\g<1>'", sk)
						sk=re.sub(r"^b\|(.*)$", r"cat '\g<1>'|base64 -w0", sk)
						pars=["bash","-c",sk]
						ex=run.cmd(pars)
						#if ex.retcode==0:
						val=ex.out
						if(val==None):
							if(unknownempty): val=""
							else: continue
						#d[k]=re.sub("\(\("+sk+"\)\)", val, d[k])
						d[k]=re.sub("\(\(.*\)\)", val, d[k])

				# Fichero base64
				r_buscacmd=re.compile(r"$b$(.*)$")
				vars=set(r_buscacmd.findall(d[k]))
				# No hay variables
				if(vars==None):
					o[k]=d[k]
				else:
					modified=True
					# Hay variables
					for sk in vars:
						f=open(sk, "rb")
						fdata=base64.b64encode(f.read()).decode()
						d[k]=re.sub(r"$b$.*$", fdata, d[k])

				# Fichero directo
				r_buscacmd=re.compile(r"$t$(.*)$")
				vars=set(r_buscacmd.findall(d[k]))
				# No hay variables
				if(vars==None):
					o[k]=d[k]
				else:
					modified=True
					# Hay variables
					for sk in vars:
						f=open(sk, "r")
						fdata=f.read()
						d[k]=re.sub(r"$t$.*$", fdata, d[k])

				if modified and d[k]=="" and emptyremove: continue
				o[k]=d[k]
			else:
				o[k]=d[k]
	return o
#}}}

# Values of dict contained in another dict
def contained(d1, d2):
	for k in d1:
		if d2.get(k)==None: return False
		if(type(d1[k])==dict or type(d1[k])==collections.OrderedDict):
			if not contained(d1[k], d2[k]): return False
		else:
			if d1[k]!=d2[k]: return False
	return True


#{{{ xml tools

# XML -> dict
def fromxml(xmldata):
	return xmltodict.parse("<xml>"+xmldata+"</xml>", disable_entities=True)[xml]

#}}}

#{{{ json tools
def fromjson(jsondata):
	return json.loads(jsondata,object_pairs_hook=json_parser_hook)

def readjson(jsonfile):
	f=open(jsonfile,"rt")
	json=f.read()
	data=fromjson(json)
	return data

def tojson(data,indent=None):
	return json.dumps(data,separators=(',',':'),default=json_serializer_hook,indent=indent)

def writejson(data,filename,tabs=0,spaces=0):
	f=open(filename, "w")
	indent=None
	if spaces!=0:
		indent=spaces
	if (tabs==1):
		indent='\t'
	jsondata=tojson(data,indent=indent)
	f.write(jsondata)
	f.write("\n")
	f.close()

# json -> dict
def json_parser_hook(js):
	#out=collections.OrderedDict(js)
	out=dict(js)
	for (key, value) in out.items():
		# Hora con timezone sin milisegundos
		try:
			dt=re.sub("Z$", "UTC",value)
			dt=datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S%Z")
			#dt=dt.replace(tzinfo=datetime.timezone(datetime.timedelta(0)))
			dt=dt.replace(tzinfo=timezone.utc)
			out[key]=dt
			continue
		except Exception: pass
		# Hora con timezone con milisegundos
		try:
			dt=re.sub("Z$", "UTC",value)
			dt=datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.%f%Z")
			dt=dt.replace(tzinfo=timezone.utc)
			out[key]=dt
			continue
		except Exception: pass
		# Hora sin timezone sin milisegundos
		try:
			out[key]=datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
			continue
		except Exception: pass
		# Hora sin timezone con milisegundos
		try:
			out[key]=datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
			continue
		except Exception: pass
	return out

# dict -> json
def json_serializer_hook(o):
	if isinstance(o, datetime):
		return re.sub("\+00:00", "Z", o.isoformat())

#}}}

#{{{ yaml tools
def fromyaml(yamldata):
	yaml=yamldata.replace("\t", "  ")
	data=ruamel.yaml.load(yaml, Loader=ruamel.yaml.Loader)
	return data

def readrawyaml(filename):
	# Cargar fichero yaml en dict
	import collections
	ruamel.yaml.representer.RoundTripRepresenter.add_representer(
	collections.OrderedDict, ruamel.yaml.representer.RoundTripRepresenter.represent_ordereddict)
	f=open(filename,"rt")
	yamldata=f.read()
	data=fromyaml(yamldata)
	return data

def readyaml(filename):
	data=readrawyaml(filename)
	if data.get("yaml-include"):
		for f in data["yaml-include"]:
			if os.path.isfile(f):
				subdata=readyaml(f)
				data.update(subdata)
			else:
				path=os.path.dirname(filename)
				f=path+os.path.sep+f
				if os.path.isfile(f):
					subdata=read(f)
					data.update(subdata)
		#data["include"]=None
		data.pop("yaml-include")
	return data

def yamlupdate(filename,var,val,node=None):
	yaml=ruamel.yaml.YAML()
	yaml.width=4096
	f=open(filename,"r")
	data=yaml.load(f.read())
	f.close()
	datamod=data
	if node:
		for n in node:
			datamod=datamod.get(n)
	datamod[var]=val
	f=open(filename, "w")
	yaml.dump(data, f)
	f.close()

def writeyaml(data,filename):
	yaml=ruamel.yaml.YAML()
	f=open(filename, "w")
	yaml.dump(data, f)
	f.close()

#}}}
