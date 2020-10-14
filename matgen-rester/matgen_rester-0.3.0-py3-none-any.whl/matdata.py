# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 11:29:09 2020

@author: LENOVO
"""
from properties.band_structure import BandStructure
from properties.cell import Cell
from properties.conventional_cell_site import ConventionalCellSite
from properties.density_of_states import DensityOfStates
from properties.magnetization import Magnetization
from properties.primitive_cell_site import PrimitiveCellSite

class MatData(object):
  def __init__(self,entries: dict={}):
    for k, v in entries.items():
      if isinstance(v, dict):
        if k == 'bandStructure':
          self.__dict__[k] = BandStructure(v)
        elif k in ['conventional_cell','primitive_cell']:
          self.__dict__[k] = Cell(v)
        elif k == 'conventional_cell_site':
          self.__dict__[k] = ConventionalCellSite(v)
        elif k == 'primitive_cell_site':
          self.__dict__[k] = PrimitiveCellSite(v)
        elif k == 'dennsityOfStates':
          self.__dict__[k] = DensityOfStates(v)
        elif k == "magnetization":
          self.__dict__[k] = Magnetization(v)
        else:
          self.__dict__[k] = MatData(v)
      else:
        self.__dict__[k] = v
  
  def obj_to_string(self):
    if not isinstance(self, MatData):
        raise TypeError("obj_to_string func: 'the object is not an instance of the specify class.'")
    to_string = str(MatData.__name__) + "("
    items = self.__dict__
    n = 0
    for k in items:
        if k.startswith("_"):
            continue
        to_string = to_string + str(k) + ":" + str(items[k]) + ","
        n += 1
    if n == 0:
        to_string += str(MatData.__name__).lower() + ": 'Instantiated objects have no property values'"
    return to_string.rstrip(",") + ")"
  
  def __str__(self):
    return self.obj_to_string()
    

  