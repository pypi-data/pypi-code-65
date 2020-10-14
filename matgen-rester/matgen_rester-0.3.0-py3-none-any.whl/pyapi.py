# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 10:56:51 2020

@author: LENOVO
"""

import requests
import sys
import json
import SETTINGS
import warnings
from concurrent.futures import ThreadPoolExecutor,as_completed

class MatgenRester:

  def __init__(self, username, password, token=None, endpoint=None):
    if token is not None:
      self.token = token
    else:
      self.token = SETTINGS.get("MATGEN_TOKEN","")
      
    if endpoint is not None:
      self.preamble = endpoint
    else:
      self.preamble = SETTINGS.get("MATGEN_ENDPOINT","https://matgen.nscc-gz.cn/api")
      
    if self.preamble != "https://matgen.nscc-gz.cn/api":
      warnings.warn("None-default endpoint used:{}".format(self.preabmle))
      
    self.session = requests.Session()
    self.login
    self.session.headers = {"token": self.token}
  
    
  def download_data_set(context, filename):
    with open(filename, 'w+') as f:
      f.write(context)

  def get_dft_by_elements(elements,pages=0,pageno=0):
    param={
      "pages":pages,
      "pageno": pageno
    }
    try:
      if pages == 0:
        print("data may be large, do you want to download data set")
        r = requests.get('http://matgen.nscc-gz.cn/api/dft/elements/'+ elements)
      else:
        r = requests.get('http://matgen.nscc-gz.cn/api/dft/elements/'+ elements,params=param)
        print(r.json())
    except:
      s=sys.exc_info()
      print("error is",s)
  
  def get_dft_by_icsdid(icsdid):
    try:
      r = requests.get('https://matgen.nscc-gz.cn/api/dft/icsdid/' + str(icsdid))
      print(r.json())
    except:
      s = sys.exc_info()
      print("error is", s)
  
  def dft_filter(elements, space_groups=None,volume=None, crystal_system=None,pages=0,pageno=0):
    headers = {
      "Content-Type": "application/json"
      }
    param={
      "pages": pages,
      "pageno": pageno
      }
    if (space_groups is None) & (volume is None) & (crystal_system is None):
      data = {}
      try:
        r = requests.post('http://localhost:8088/elements/'+elements, data=json.dumps(data), params=param, headers=headers)
        return r.json()
      except:
        print("error is",sys.exc_info())
    elif (space_groups is None) & (volume is None):
      data = {
        "spaceGroup": space_groups,
        "volume": volume,
        }
      try:
        r = requests.post('http://localhost:8088/elements/'+elements,data=json.dumps(data), params=param,headers=headers)
        return r.json()
      except:
        print("error is",sys.exc_info())
    elif (space_groups is None) & (crystal_system is None):
      data = {
        "spaceGroup": space_groups,
        "crystalSystem": crystal_system
        }
      try:
        r = requests.post('http://localhost:8088/elements/'+elements,data=json.dumps(data), params=param,headers=headers)
        return r.json()
      except:
        print("error is",sys.exc_info())
    elif (volume is None) & (crystal_system is None):
      data = {
        "volume": volume,
        "crystalSystem": crystal_system
        }
      try:
        r = requests.post('http://localhost:8088/elements/'+elements,data=json.dumps(data), params=param,headers=headers)
        return r.json()
      except:
        print("error is",sys.exc_info())
    elif crystal_system is None:
      data = {
        "spaceGroup": space_groups,
        "volume": volume,
        }
    elif volume is None:
      data = {
        "spaceGroup": space_groups,
        "crystalSystem": crystal_system
        }
    elif space_groups is None:
      data = {
        "volume": volume,
        "crystalSystem": crystal_system
        }
    data = {
      "spaceGroup": space_groups,
      "volume": volume,
      "crystalSystem": crystal_system
    }
    
  def parallel_dft_filter(self,elements, space_groups=None,volume=None, crystal_system=None,pages=0,pageno=0):
    with ThreadPoolExecutor(max_workers=self.max_connection) as executor:
      future_to_filter = []
      for index in range(0,len(elements)):
        executor.submit(self.dft_filter,self.elements[index],self.space_group[index],self.volume[index],crystal_system[index],pages[index],pageno[index])
      for future in as_completed(future_to_filter):
          res = future_to_filter[future]
          try:
            yield future.result()
          except Exception as exc:
            print(f"{res} caused exception: {exc}")
        
if __name__ == "__main__":
  elements = "C"
  pages = 1
  pageno = 1
  print("res is", MatgenRester.get_dft_filter(elements=elements,pages=pages,pageno=pageno))
  
# import matgen_rester as mr
# //filter by volume, spaceGroup,crystalSystem
# with mr.MatgenRester() as m:
#   kwargs = {
#     "elements":"Fe,O",
#     "volume":[0,100],
#     "spaceGroup":[""],
#     "crystalSystem":[""],
#     "fileds":["cisdid","formula"]
#   }
#   list = q.get_dft_filter(**kwargs)

# //get by icsdid
# with mr.MatgenRester() as m:
#   data = m.get_dft_by_icsdid(icsdid=16887,fields=None)
    