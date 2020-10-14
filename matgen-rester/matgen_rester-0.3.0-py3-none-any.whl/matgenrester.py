# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 10:56:51 2020

@author: LENOVO
"""

import requests
import json
import warnings
from matdata import MatData
from MatgenError import MatgenError
from concurrent.futures import ThreadPoolExecutor,as_completed
import sys
sys.path.append("../..")
from matgen_tool import *
from args import parse_cml_args

null = ''

class MatgenRester:

  def __init__(self, username=None, password=None, token=None,endpoint=None):
    if endpoint is not None:
      self.preamble = endpoint
    else:
      self.preamble = SETTINGS.get("MATGEN_ENDPOINT")
    if self.preamble != "http://localhost:8081":
      warnings.warn("None-default endpoint used:{}".format(self.preamble))
      
    self.POSCAR_LIMIT = 10
    self.session = requests.Session()
    
    if token is not None:
      self.token = token
    elif (username is not None) and (password is not None):
      print('username is ',username)
      self.username = username
      self.password = password
      self.token = self.login()
    else:
      try:
        self.token = SETTINGS.get("MATGEN_TOKEN")
      except KeyError as k:
        raise MatgenError("Authentication returned wuth {]".format(k))
 
  def __enter__(self):
    return self
  
  def login(self, verbose=True):
    # url=self.preamble + "/token",
    url="http://localhost:8081/token"
    print('url', url)
    payload = {
      "username":"test",
      "logged_in":True
    }
    headers = {
    		'Content-Type': 'application/json'
    }
    try:
      response = self.session.post(url, headers=headers, data = json.dumps(payload))
      if response.status_code not in [200,400]:
        raise MatgenError("Request returned wuth error status code {}"
                          .format(response.status_code))
      else:
        if verbose:
          value = str(response.content,encoding="utf-8")
          print("logged in (MATGEN_TOKEN={})".format(value))
        print('write matgen token:',write_matgen_token(value))
        return value
        
    except Exception as ex:
      raise MatgenError("Authentication returned wuth {}".format(str(ex)))
       
  def __exit__(self, ex_type, ex_value, traceback):
    self.session.close()
  
  def reconnect(self):
    self.login(verbose=True)
  
  def _make_request(self, url=None, param=None, payload=None,  method="GET",matgen_decode=True):
    response = None
    url = self.preamble + url
    print('url:',url)
    if param is None:
      param = {}
    
    if self.token != None:
      param['token']=self.token
    else:
      raise MatgenError("can't get token")
    print('param:',param)
    try:
      if method == "POST":
        # url = "http://localhost:8081/dft/elements/C"
        
        headers = {
        		'Content-Type': 'application/json'
        }
        print(payload)
        response = self.session.post(url, headers=headers, data = json.dumps(payload),params=param)
        
        print(response.status_code)
        # response = self.session.post(url, data = data, params = param)
      else:
        response = self.session.get(url, params = param)
        if response == None:
          print('response is None')
        print(response.text == '')
        print('response',response.text)
      if response.status_code in [200,400]:
        if response.text == '':
          raise MatgenError("Request returned wuth error, nothing return")
        return json.loads(response.text)
      else:
        raise MatgenError("Request returned wuth error status code {}"
                          .format(response.status_code))
    except Exception as ex:
      # print(str(ex))
      raise MatgenError("Request returned wuth {}".format(str(ex)))
  
  def _specific_fields(self,data,fields,matgen_decode=True):
    if matgen_decode:
      ex_fields = set()
      in_fields = set()
      if fields:
        for f in fields:
          if '!' in f:
            if data.__getattribute__(f[1:]):
              ex_fields.add(f[1:])
            else:
              raise MatgenError("Request returned wuth error Key Error, can't \
                                find fields {}".format(f[1:]))
          else:
            if data.__getattribute__(f):
              in_fields.add(f)
            else:
              raise MatgenError("Request returned wuth error Key Error, can't \
                                find fields {}".format(f))
      attr_list = list(filter(lambda m :not callable(getattr(data,m)) 
                              and not m.startswith("__") and not m.endswith("__"),dir(data)))   
      if ex_fields and not in_fields:
        for f in ex_fields:
          try:
            delattr(data,f)
          except KeyError as k:
            print("Request returned doesn't contain {}".format(k))
      elif not ex_fields and in_fields:
        for f in attr_list:
          if f not in in_fields:
            delattr(data,f)
      elif ex_fields and in_fields:
        print(ex_fields)
        print(in_fields)
        in_fields = in_fields - ex_fields
        for f in attr_list:
          if (f not in in_fields):
            delattr(data,f)
      return data
    else:
      ex_fields = set()
      in_fields = set()
      if fields:
        for f in fields:
          if '!' in f:
            if f[1:] in data.keys():
              ex_fields.add(f[1:])
            else:
              raise MatgenError("Request returned wuth error Key Error, can't \
                                find fields {}".format(f[1:]))
          else:
            if f in data.keys():
              in_fields.add(f)
            else:
              raise MatgenError("Request returned wuth error Key Error, can't \
                                find fields {}".format(f))
      
      if ex_fields and not in_fields:
        for f in ex_fields:
          data.pop(f)
          
      elif not ex_fields and in_fields:
        dic = {}
        for f in data.keys():
          if f in in_fields:
            dic[f] = data[f]
        data = dic
        # dic.clear()
      elif ex_fields and in_fields:
        in_fields = in_fields - ex_fields
        for f in data.keys():
          if f in in_fields:
            dic[f] = data[f]
        data = dic
        # dic.clear()
            
      return data
    
  def get_strcuture_by_matid(self,matid,fields=None,matgen_decode=True, verbose=True):
    try:
      url = '/dft/matid/'+str(matid)
      res = self._make_request(url,matgen_decode=matgen_decode)
      print(res)
      if matgen_decode and res:
        print(res)
        res = MatData(res)
        
      if fields and res:
        print("fields",fields)
        res = self._specific_fields(res,fields)
      
      return res
    except Exception as ex:
      raise MatgenError("Request returned wuth {}".format(str(ex)))
  
  def parallel_dft_matid(self,matids,fields):
    if len(matids) > self.POSCAR_LIMIT:
      warnings.warn("query too much POSCAR")
      matids = matids[0:self.POSCAR_LIMIT+1]
    with ThreadPoolExecutor(max_workers=self.max_connection) as executor:
      future_to_filter = []
      for index in range(0,len(elements)):
        executor.submit(self.dft_mat_id,matids[index],fields)
      for future in as_completed(future_to_filter):
          res = future_to_filter[future]
          try:
            yield future.result()
          except Exception as exc:
            raise MatgenError("{} caused exception: {}".format(res,exc))
            
  def get_structure_with_filter(self,elements, filter=None, fields=None, matgen_decode=True,pages=0, pageno=0):
    print(fields)
    param={
      "pages": pages,
      "pageno": pageno
    }
    
    filter_list = ['_volume', '_space_group', 
                       '_crystal_system']
    args_list = ['volume','spaceGroup','crystalSystem']
    
    
    elements_list = elements.split('-')
    if elements_list is None:
      raise MatgenError("Elements is required")
    filter_args = {}
    url_args = ""
    if filter:
      for k in filter:
        if k == '_nelements':
          url_args='/not/'+filter[k]
        elif k in filter_list:
          filter_args[args_list[filter_list.index(k)]]=filter[k]
    try:
      if filter_args and not url_args:
        url = '/dft/elements/'+ elements
        r = self._make_request(url=url,payload=filter_args,param=param,method="POST")
        
      elif not filter_args and url_args:
        url = '/dft/elements/'+ elements + url_args
        r = self._make_request(url,param=param)
        
      elif not filter_args and not url_args:
        url = '/dft/elements/part/'+ elements
        r = self._make_request(url,param=param)
      
      else:
        raise MatgenError("Too much filter")
        
      if r and matgen_decode:
        print(r)
        res = [(lambda x:MatData(x))(x) for x in r]
        print(res)
        print(fields)
        res = [(lambda x :self._specific_fields(x, fields,matgen_decode))(x) for x in res]
        # print(res)
        #res = list(lambda x: self.parallel_dft_matid(res,["bandStructure",'matid']))
        return res
      elif r and not matgen_decode:
        res = [(lambda x :self._specific_fields(x, fields,matgen_decode))(x) for x in r]
        return res
    except:
      print("error is",sys.exc_info())  
            
  def download_data_set(self,context, filename):
    with open(filename, 'w+') as f:
      f.write(context)
  
  def test(self):
    return self._make_request()
          
if __name__ == "__main__":
  matgenrester = MatgenRester()
  parser = parse_cml_args(sys.argv[1:])
  print(parser)
  if parser.id:
    print(parser.id)
    print(parser.f.split(','))
    context = matgenrester.get_strcuture_by_matid(parser.id,fields=parser.f.split(','))
    if parser.o:
      print(str(context))
      print(type(parser.o))
      matgenrester.download_data_set(str(context),parser.o)
    else:
      print(context)
  elif parser.ne:
    matgenrester = MatgenRester()
    context=matgenrester.get_structure_with_filter(parser.e, filter={"_nelements":parser.ne}, fields=parser.f.split(','), pages=parser.p, pageno=parser.s)
    if parser.o:
      print(str(context))
      print(type(parser.o))
      matgenrester.download_data_set(str(context),parser.o)
    else:
      print(context)

  elif ('v' in parser and parser.v == None) and ('cs' in parser and parser.cs == None) and ('sg' in parser and parser.sg == None)::
    print(1)
    matgenrester = MatgenRester()
    context = matgenrester.get_structure_with_filter(parser.e, filter=None, fields=parser.f.split(','), matgen_decode=parser.m,pages=parser.p, pageno=parser.s)
    if parser.o:
      print(str(context))
      print(type(parser.o))
      matgenrester.download_data_set(str(context),parser.o)
    else:
      print(context)

  elif ('v' in parser and parser.v != None) and ('cs' in parser and parser.cs == None) and ('sg' in parser and parser.sg == None):
    volume = parser.v.split(',')
    new_v = []
    for v in volume:
      new_v.append(float(v))
    volume = new_v
    print(volume)
    matgenrester = MatgenRester()
    context = matgenrester.get_structure_with_filter(parser.e, filter={"_volume":volume}, fields=parser.f.split(','), pages=parser.p, pageno=parser.s)
    if parser.o:
      print(str(context))
      print(type(parser.o))
      matgenrester.download_data_set(str(context),parser.o)
    else:
      print(context)

  elif ('v' in parser and parser.v != None) and ('cs' in parser and parser.cs != None) and ('sg' in parser and parser.sg != None)::
    print(2)
    volume = parser.v.split(',')
    new_v = []
    for v in volume:
      new_v.append(float(v))
    volume = new_v
    crystalSystem = parser.crystalSystem.split(',')
    spaceGroup = parser.spaceGroup.split(',')
    matgenrester = MatgenRester()
    context = matgenrester.get_structure_with_filter(parser.e, filter={"_volume":volume,"_space_group":spaceGroup,"_crystal_system":crystalSystem}, fields=parser.f.split(','), pages=parser.p, pageno=parser.s)
    if parser.o:
      print(str(context))
      print(type(parser.o))
      matgenrester.download_data_set(str(context),parser.o)
    else:
      print(context)

  elif ('v' in parser and parser.v != None) and ('cs' in parser and parser.cs != None) and ('sg' in parser and parser.sg == None):
    print(3)
    volume = parser.v.split(',')
    new_v = []
    for v in volume:
      new_v.append(float(v))
    volume = new_v
    crystalSystem = parser.cs.split(',')
    matgenrester = MatgenRester()
    context = matgenrester.get_structure_with_filter(parser.e, filter={"_volume":volume,"_crystal_system":crystalSystem}, fields=parser.f.split(','), pages=parser.p, pageno=parser.s)
    if parser.o:
      print(str(context))
      print(type(parser.o))
      matgenrester.download_data_set(str(context),parser.o)
    else:
      print(context)

  elif ('v' in parser and parser.v == None) and ('cs' in parser and parser.cs == None) and ('sg' in parser and parser.sg != None):
    print(5)
    
    spaceGroup = parser.sg.split(',')
    matgenrester = MatgenRester()
    context = matgenrester.get_structure_with_filter(parser.e, filter={"_volume":volume,"_space_group":spaceGroup}, fields=parser.f.split(','), pages=parser.p, pageno=parser.s)
    if parser.o:
      print(str(context))
      print(type(parser.o))
      matgenrester.download_data_set(str(context),parser.o)
    else:
      print(context)
  
  elif ('v' in parser and parser.v == None) and ('cs' in parser and parser.cs != None) and ('sg' in parser and parser.sg == None):
    print(6)
    crystalSystem = parser.cs.split(',')
    matgenrester = MatgenRester()
    context = matgenrester.get_structure_with_filter(parser.e, filter={"_crystal_system":crystalSystem}, fields=parser.f.split(','), pages=parser.p, pageno=parser.s)
    if parser.o:
      print(str(context))
      print(type(parser.o))
      matgenrester.download_data_set(str(context),parser.o)
    else:
      print(context)


  elif ('v' in parser and parser.v == None) and ('cs' in parser and parser.cs != None) and ('sg' in parser and parser.sg != None):
    print(7)
    crystalSystem = parser.cs.split(',')
    spaceGroup = parser.sg.split(',')
    matgenrester = MatgenRester()
    context = matgenrester.get_structure_with_filter(parser.e, filter={"_space_group":spaceGroup,"_crystal_system":crystalSystem}, fields=parser.f.split(','), pages=parser.p, pageno=parser.s)
    if parser.o:
      print(str(context))
      print(type(parser.o))
      matgenrester.download_data_set(str(context),parser.o)
    else:
      print(context)

  elif ('v' in parser and parser.v == None) and ('cs' in parser and and parser.cs == None) and ('sg' in parser and and parser.sg != None):
    print(8)
    spaceGroup = parser.sg.split(',')
    matgenrester = MatgenRester()
    context = matgenrester.get_structure_with_filter(parser.e, filter={"_space_group":spaceGroup}, fields=parser.f.split(','), pages=parser.p, pageno=parser.s)
    if parser.o:
      print(str(context))
      print(type(parser.o))
      matgenrester.download_data_set(str(context),parser.o)
    else:
      print(context)
  
  
# elements = "Ba-S"
# matid="mat_16680"
# pages = 1
# pageno = 1
# m = MatgenRester()
# m = MatgenRester(username="matgen",password="matgen",endpoint="http://localhost:8081")
# print(SETTINGS.get("MATGEN_TOKEN"))
# print(m.test())
  # print(m.get_structure_with_filter(elements, filter={"_nelements":"O-Ti"}, fields=None, matgen_decode=False,pages=5, pageno=0))
  # print(m.get_structure_with_filter(elements, filter={"_volume":[0,100]}, fields=['conventional_cell'], matgen_decode=False,pages=5, pageno=0))
  # print(m.get_strcuture_by_matid(matid,fields=["matid","!bandStructure"]))
  # print("res is", m.get_structure_with_filter(elements=elements,pages=pages,pageno=pageno))    